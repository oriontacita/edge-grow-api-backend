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