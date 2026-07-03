from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Toddler
from app.utils import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/")
def get_dashboard(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    toddlers = db.query(Toddler).all()
    data = [{
        "id": t.id,
        "toddler_full_name": t.toddler_full_name,
        "date_of_birth": t.date_of_birth.isoformat(),
        "gender": t.gender.value
    } for t in toddlers]
    return {"success": True, "message": "Dashboard data retrieved", "data": {"toddlers": data}}