from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schema import UserUpdate
from app.models import User
from app.utils import get_current_user

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("/{user_id}")
def get_settings(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail={"success": False, "message": "User not found", "data": None})
    return {"success": True, "message": "User retrieved", "data": {"user": user}}

@router.put("/edit/{user_id}")
def update_settings(user_id: int, req: UserUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail={"success": False, "message": "User not found", "data": None})
    
    for key, value in req.dict().items():
        setattr(user, key, value)
    db.commit()
    return {"success": True, "message": "User updated successfully"}