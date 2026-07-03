from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schema import ToddlerCreate, ToddlerUpdate, GenderEnum
from app.models import Toddler
from app.utils import get_current_user

router = APIRouter(prefix="/api/toddlers", tags=["Toddlers"])

@router.get("/")
def get_toddlers(gender: GenderEnum = Query(None), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    query = db.query(Toddler)
    if gender:
        query = query.filter(Toddler.gender == gender)
    toddlers = query.all()
    return {"success": True, "message": "Toddlers retrieved", "data": {"toddlers": toddlers}}

@router.get("/view/{toddler_id}")
def get_toddler(toddler_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    toddler = db.query(Toddler).filter(Toddler.id == toddler_id).first()
    if not toddler:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Toddler not found", "data": None})
    return {"success": True, "message": "Toddler retrieved", "data": {"toddler": toddler}}

@router.post("/add", status_code=201)
def add_toddler(req: ToddlerCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    new_toddler = Toddler(**req.dict())
    db.add(new_toddler)
    db.commit()
    return {"success": True, "message": "Toddler created successfully"}

@router.put("/edit/{toddler_id}")
def edit_toddler(toddler_id: int, req: ToddlerUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    toddler = db.query(Toddler).filter(Toddler.id == toddler_id).first()
    if not toddler:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Toddler not found", "data": None})
    
    for key, value in req.dict().items():
        setattr(toddler, key, value)
    db.commit()
    return {"success": True, "message": "Toddler updated successfully"}

@router.delete("/delete/{toddler_id}")
def delete_toddler(toddler_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    toddler = db.query(Toddler).filter(Toddler.id == toddler_id).first()
    if not toddler:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Toddler not found", "data": None})
    db.delete(toddler)
    db.commit()
    return {"success": True, "message": "Toddler deleted successfully", "data": None}