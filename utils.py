from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt 
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from dotenv import load_dotenv
from os import getenv

load_dotenv()

SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # PyJWT menggunakan encode langsung
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"success": False, "message": "Invalid or expired token", "data": None}
    )
    try:
        # PyJWT menggunakan jwt.decode dan menangkap jwt.InvalidTokenError
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError: # <-- PERUBAHAN DI SINI (dari JWTError menjadi InvalidTokenError)
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def calculate_age_in_months(dob, measurement_date) -> int:
    return (measurement_date.year - dob.year) * 12 + (measurement_date.month - dob.month)