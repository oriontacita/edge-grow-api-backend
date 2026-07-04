from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schema import MeasurementCreate, MeasurementUpdate
from app.models import Measurement, Toddler
from app.utils import get_current_user

router = APIRouter(tags=["Measurements"])

@router.get("/api/toddlers/{toddler_id}/measurements")
def get_measurements(toddler_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    toddler = db.query(Toddler).filter(Toddler.id == toddler_id).first()
    if not toddler:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Toddler not found", "data": None})
        
    measurements = db.query(Measurement).filter(Measurement.toddler_id == toddler_id).all()
    return {"success": True, "message": "Measurements retrieved", "data": {"toddler_id": toddler_id, "measurements": measurements}}

@router.get("/api/measurements/{measurement_id}/detail")
def get_measurement_detail(measurement_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    measurement = db.query(Measurement).filter(Measurement.id == measurement_id).first()
    if not measurement:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Measurement not found", "data": None})
        
    return {
        "success": True, 
        "message": "Measurement retrieved", 
        "data": {
            "measurement": {
                "id": measurement.id,
                "toddler_id": measurement.toddler_id,
                "toddler_name": measurement.toddler.toddler_full_name,
                "measurement_date": measurement.measurement_date.isoformat(),
                "current_age": measurement.current_age,
                "current_weight": measurement.current_weight,
                "current_length": measurement.current_length,
                "breastfeeding": measurement.breastfeeding.value,
                "created_at": measurement.created_at.isoformat(),
                "updated_at": measurement.updated_at.isoformat()
            }
        }
    }

@router.post("/api/toddlers/{toddler_id}/measurements/add", status_code=201)
def add_measurement(toddler_id: int, req: MeasurementCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    toddler = db.query(Toddler).filter(Toddler.id == toddler_id).first()
    if not toddler:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Toddler not found", "data": None})
        
    # age_in_months = calculate_age_in_months(toddler.date_of_birth, req.measurement_date)
    
    new_measurement = Measurement(
        toddler_id=toddler_id,
        **req.dict(),
    )
    db.add(new_measurement)
    db.commit()
    return {"success": True, "message": "Measurement created successfully"}

@router.put("/api/measurements/edit/{measurement_id}")
def edit_measurement(measurement_id: int, req: MeasurementUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    measurement = db.query(Measurement).filter(Measurement.id == measurement_id).first()
    if not measurement:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Measurement not found", "data": None})
        
    for key, value in req.dict().items():
        setattr(measurement, key, value)
        
    toddler = db.query(Toddler).filter(Toddler.id == measurement.toddler_id).first()
    measurement.current_age = calculate_age_in_months(toddler.date_of_birth, measurement.measurement_date)
    
    db.commit()
    return {"success": True, "message": "Measurement updated successfully"}

@router.delete("/api/measurements/delete/{measurement_id}")
def delete_measurement(measurement_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    measurement = db.query(Measurement).filter(Measurement.id == measurement_id).first()
    if not measurement:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Measurement not found", "data": None})
    db.delete(measurement)
    db.commit()
    return {"success": True, "message": "Measurement deleted successfully", "data": None}