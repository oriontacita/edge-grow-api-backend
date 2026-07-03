from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
import enum

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"

class RoleEnum(str, enum.Enum):
    admin = "admin"
    cadre = "cadre"

class StatusEnum(str, enum.Enum):
    normal = "normal"
    risk = "risk"
    stunted = "stunted"

class BreastfeedingEnum(str, enum.Enum):
    yes = "yes"
    no = "no"

# Auth
class LoginRequest(BaseModel):
    username: str
    pin: str

# Toddlers
class ToddlerCreate(BaseModel):
    toddler_full_name: str
    biological_mother_name: str
    date_of_birth: date
    gender: GenderEnum
    birth_weight: float
    birth_length: float

class ToddlerUpdate(BaseModel):
    toddler_full_name: str
    biological_mother_name: str
    date_of_birth: date
    gender: GenderEnum
    birth_weight: float
    birth_length: float
    status: StatusEnum

# Measurements
class MeasurementCreate(BaseModel):
    measurement_date: date
    current_weight: float
    current_length: float
    breastfeeding: BreastfeedingEnum

class MeasurementUpdate(BaseModel):
    measurement_date: date
    current_weight: float
    current_length: float
    breastfeeding: BreastfeedingEnum

# Users
class UserCreate(BaseModel):
    full_name: str
    username: str
    pin: str
    gender: GenderEnum
    role: RoleEnum = RoleEnum.cadre
    village_id: int

class UserUpdate(BaseModel):
    full_name: str
    username: str
    pin: str
    gender: GenderEnum

# Sync
class SyncToddlerData(BaseModel):
    toddler_full_name: str
    biological_mother_name: str
    date_of_birth: date
    gender: GenderEnum
    birth_weight: float
    birth_length: float

class SyncMeasurementData(BaseModel):
    toddler_id: int # Harus ada id balita saat sync
    measurement_date: date
    current_weight: float
    current_length: float
    breastfeeding: BreastfeedingEnum

class SyncPayload(BaseModel):
    toddlers: List[SyncToddlerData] = []
    measurements: List[SyncMeasurementData] = []

class VillageCreate(BaseModel):
    name: str

class IngredientCreate(BaseModel):
    name: str

class MenuCreate(BaseModel):
    name: str
    calories: Optional[float] = None
    cooking_method: Optional[str] = None
    ingredient_ids: List[int]

class LocalMapCreate(BaseModel):
    village_id: int
    ingredient_id: int
    start_month: int = Field(..., ge=1, le=12)
    end_month: int = Field(..., ge=1, le=12)

class MenuRecommendationOut(BaseModel):
    id: int
    name: str
    calories: Optional[float]
    cooking_method: Optional[str]
    available_ingredients: List[str]
    class Config:
        from_attributes = True

class MenuCreate(BaseModel):
    name: str
    calories: Optional[float] = None
    cooking_method: Optional[str] = None
    min_age_months: int = 6
    max_age_months: int = 59
    ingredient_ids: List[int]