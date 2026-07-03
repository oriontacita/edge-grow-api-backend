from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schema import UserCreate, UserUpdate, GenderEnum
from app.models import User
from app.utils import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/")
def get_users(gender: GenderEnum = Query(None), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    query = db.query(User)
    if gender:
        query = query.filter(User.gender == gender)
    users = query.all()
    return {"success": True, "message": "Users retrieved", "data": {"users": users}}

@router.get("/view/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail={"success": False, "message": "User not found", "data": None})
    return {"success": True, "message": "User retrieved", "data": {"user": user}}

@router.post("/add", status_code=201)
def add_user(req: UserCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Cek conflict username
    existing_user = db.query(User).filter(User.username == req.username).first()
    if existing_user:
        return {"success": False, "message": "Username already exists", "errors": {"username": "Conflict"}}
        
    new_user = User(**req.dict())
    db.add(new_user)
    db.commit()
    return {"success": True, "message": "User created successfully"}

@router.put("/edit/{user_id}")
def edit_user(user_id: int, req: UserUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail={"success": False, "message": "User not found", "data": None})
    
    for key, value in req.dict().items():
        setattr(user, key, value)
    db.commit()
    return {"success": True, "message": "User updated successfully"}

@router.delete("/delete/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail={"success": False, "message": "User not found", "data": None})
    db.delete(user)
    db.commit()
    return {"success": True, "message": "User deleted successfully", "data": None}