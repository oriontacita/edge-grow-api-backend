from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schema import LoginRequest
from app.models import User
from app.utils import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or user.pin != req.pin:
        return {"success": False, "message": "Invalid username or PIN", "data": None}
    
    token = create_access_token(data={"sub": user.username})
    return {"success": True, "message": "Login successful", "token": token}