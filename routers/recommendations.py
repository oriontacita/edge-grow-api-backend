from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.database import get_db
from app.models import User, Toddler, Measurement, Village, Ingredient, Menu, MenuIngredient, LocalIngredientMap
from app.schema import VillageCreate, IngredientCreate, MenuCreate, LocalMapCreate
from app.utils import get_current_user, calculate_age_in_months

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])

@router.post("/villages")
def create_village(req: VillageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    village = Village(name=req.name)
    db.add(village)
    db.commit()
    return {"success": True, "message": "Village added"}

@router.post("/ingredients")
def create_ingredient(req: IngredientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ingredient = Ingredient(name=req.name)
    db.add(ingredient)
    db.commit()
    return {"success": True, "message": "Ingredient added"}

@router.post("/menus")
def create_menu(req: MenuCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    menu = Menu(
        name=req.name, calories=req.calories, cooking_method=req.cooking_method,
        min_age_months=req.min_age_months, max_age_months=req.max_age_months
    )
    db.add(menu)
    db.flush()
    for ing_id in req.ingredient_ids:
        db.add(MenuIngredient(menu_id=menu.id, ingredient_id=ing_id))
    db.commit()
    return {"success": True, "message": "Menu added"}

@router.post("/local-maps")
def create_local_map(req: LocalMapCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.add(LocalIngredientMap(
        village_id=req.village_id, ingredient_id=req.ingredient_id, 
        start_month=req.start_month, end_month=req.end_month
    ))
    db.commit()
    return {"success": True, "message": "Local ingredient mapped"}


@router.get("/menus/{toddler_id}")
def get_recommended_menus(
    toddler_id: int,
    target_month: int = Query(None, description="Bulan target (1-12), default bulan sekarang"),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    current_month = target_month if target_month else today.month
    toddler_age_months = None

    if toddler_id:
        toddler = db.query(Toddler).filter(Toddler.id == toddler_id).first()
        if not toddler:
            raise HTTPException(status_code=404, detail={"success": False, "message": "Toddler not found", "data": None})

        latest_measurement = db.query(Measurement).filter(Measurement.toddler_id == toddler_id).order_by(Measurement.measurement_date.desc()).first()
        
        print(f"current age: {latest_measurement.current_age}")

        
        if latest_measurement:
            toddler_age_months = latest_measurement.current_age
        else:
            toddler_age_months = calculate_age_in_months(toddler.date_of_birth, date.today())

    if not current_user.village_id:
        raise HTTPException(status_code=400, detail={"success": False, "message": "Kader belum memiliki Desa.", "data": None})
    
    available_maps = db.query(LocalIngredientMap).filter(
        LocalIngredientMap.village_id == current_user.village_id,
        LocalIngredientMap.start_month <= current_month,
        LocalIngredientMap.end_month >= current_month
    ).all()
    available_ingredient_ids = set([m.ingredient_id for m in available_maps])
    
    if not available_ingredient_ids:
        return {"success": True, "message": f"Tidak ada bahan lokal yang tersedia di bulan {current_month}", "data": {"recommended_menus": []}}
    
    query = db.query(Menu)
    
    if toddler_age_months is not None:
        query = query.filter(
            Menu.min_age_months <= toddler_age_months,
            Menu.max_age_months >= toddler_age_months
        )
        
    all_menus = query.all()
    
    recommended = []
    for menu in all_menus:
        required_ingredients = db.query(MenuIngredient).filter(MenuIngredient.menu_id == menu.id).all()
        required_ids = set([r.ingredient_id for r in required_ingredients])
        
        if required_ids.issubset(available_ingredient_ids):
            ing_names = db.query(Ingredient.name).filter(Ingredient.id.in_(required_ids)).all()
            recommended.append({
                "id": menu.id,
                "name": menu.name,
                "calories": menu.calories,
                "cooking_method": menu.cooking_method,
                "for_age_months": f"{menu.min_age_months} - {menu.max_age_months} bulan",
                "available_ingredients": [name[0] for name in ing_names]
            })
            
    age_text = f"{toddler_age_months} bulan" if toddler_age_months is not None else "Semua Usia (Tidak ada ID Balita)"
    print("d:" ,toddler_age_months)
    return {
        "success": True, 
        "message": f"Recommended menus retrieved (Desa: {current_user.village_id}, Bulan: {current_month}, Umur Balita: {age_text})", 
        "data": {"recommended_menus": recommended}
    } 