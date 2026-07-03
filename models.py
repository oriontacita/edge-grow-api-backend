from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class GenderEnum(enum.Enum):
    male = "male"
    female = "female"

class RoleEnum(enum.Enum):
    admin = "admin"
    cadre = "cadre"

class StatusEnum(enum.Enum):
    normal = "normal"
    risk = "risk"
    stunted = "stunted"

class BreastfeedingEnum(enum.Enum):
    yes = "yes"
    no = "no"

class Village(Base):
    __tablename__ = "villages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    pin = Column(String(255), nullable=False)
    gender = Column(SAEnum(GenderEnum), nullable=False)
    role = Column(SAEnum(RoleEnum), default=RoleEnum.cadre)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Toddler(Base):
    __tablename__ = "toddlers"
    id = Column(Integer, primary_key=True, index=True)
    toddler_full_name = Column(String(255), nullable=False)
    biological_mother_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(SAEnum(GenderEnum), nullable=False)
    birth_weight = Column(Float, nullable=False)
    birth_length = Column(Float, nullable=False)
    status = Column(SAEnum(StatusEnum), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    measurements = relationship("Measurement", back_populates="toddler")

class Measurement(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True, index=True)
    toddler_id = Column(Integer, ForeignKey('toddlers.id'), nullable=False)
    measurement_date = Column(Date, nullable=False)
    current_age = Column(Integer, nullable=True)
    current_weight = Column(Float, nullable=False)
    current_length = Column(Float, nullable=False)
    breastfeeding = Column(SAEnum(BreastfeedingEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    toddler = relationship("Toddler", back_populates="measurements")

class MenuIngredient(Base):
    __tablename__ = "menu_ingredients"
    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey('menus.id'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)
    
    menu = relationship("Menu", back_populates="recipes")
    ingredient = relationship("Ingredient")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LocalIngredientMap(Base):
    __tablename__ = "local_ingredient_maps"
    id = Column(Integer, primary_key=True, index=True)
    village_id = Column(Integer, ForeignKey('villages.id'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)
    start_month = Column(Integer, nullable=False)
    end_month = Column(Integer, nullable=False) 
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Menu(Base):
    __tablename__ = "menus"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    calories = Column(Float, nullable=True)
    cooking_method = Column(String(255), nullable=True)
    min_age_months = Column(Integer, nullable=True, default=6)
    max_age_months = Column(Integer, nullable=True, default=59)

    recipes = relationship("MenuIngredient", back_populates="menu")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)