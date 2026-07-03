from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schema import SyncPayload
from app.models import Toddler, Measurement, User
from app.utils import get_current_user, calculate_age_in_months

router = APIRouter(prefix="/api", tags=["Synchronize"])

@router.post("/syncronize", status_code=201)
def sync_data(payload: SyncPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        for t_data in payload.toddlers:
            new_toddler = Toddler(**t_data.dict())
            db.add(new_toddler)
            
        db.flush()
        
        # 2. Sync Measurements
        for m_data in payload.measurements:
            toddler = db.query(Toddler).filter(Toddler.id == m_data.toddler_id).first()
            if toddler:
                age = calculate_age_in_months(toddler.date_of_birth, m_data.measurement_date)
                new_measurement = Measurement(
                    **m_data.dict(),
                    current_age=age
                )
                db.add(new_measurement)
                
        db.commit()
        return {"success": True, "message": "data syncronized successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))