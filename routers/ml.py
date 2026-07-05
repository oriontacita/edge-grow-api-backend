from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Toddler, Measurement
from app.utils import get_current_user, calculate_age_in_months
from app.ml_model import predict_stunting_status
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])

# ==========================================
# 1. PREDIKSI OTOMATIS BERDASarkan ID TODDLER
# ==========================================
@router.post("/predict/{toddler_id}")
def predict_toddler_status(
    toddler_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """
    Mencari data pengukuran terakhir dari toddler_id, 
    lalu memprediksi status stunting dan mengupdate DB.
    """
    # 1. Cek apakah toddler ada
    toddler = db.query(Toddler).filter(Toddler.id == toddler_id).first()
    if not toddler:
        raise HTTPException(status_code=404, detail={"success": False, "message": "Toddler not found", "data": None})
    
    # 2. Cari data pengukuran paling baru
    latest_measurement = db.query(Measurement)\
        .filter(Measurement.toddler_id == toddler_id)\
        .order_by(Measurement.measurement_date.desc())\
        .first()
        
    if not latest_measurement:
        raise HTTPException(status_code=400, detail={"success": False, "message": "Belum ada data pengukuran untuk balita ini", "data": None})

    # 3. Hitung Usia
    age_in_months = latest_measurement.current_age
    if not age_in_months:
        age_in_months = calculate_age_in_months(toddler.date_of_birth, latest_measurement.measurement_date)

    # 4. Jalankan Model XGBoost
    predicted_status = predict_stunting_status(
        gender=toddler.gender.value,
        age=age_in_months,
        birth_weight=toddler.birth_weight,
        birth_length=toddler.birth_length,
        body_weight=latest_measurement.current_weight,
        body_length=latest_measurement.current_length,
        breastfeeding=latest_measurement.breastfeeding.value
    )

    # 5. Update status di database
    old_status = toddler.status.value if toddler.status else None
    toddler.status = predicted_status
    db.commit()

    return {
        "success": True, 
        "message": "Prediction successful",
        "data": {
            "toddler_id": toddler.id,
            "toddler_name": toddler.toddler_full_name,
            "old_status": old_status,
            "predicted_status": predicted_status,
            "based_on_measurement_id": latest_measurement.id
        }
    }

# ==========================================
# 2. PREDIKSI MASSAL (SEMUA TODDLER SEKALIGUS)
# ==========================================
@router.post("/predict/batch")
def predict_all_toddlers(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """
    Memindai seluruh balita yang memiliki data pengukuran, 
    memprediksi statusnya, dan mengupdate DB secara massal.
    """
    toddlers = db.query(Toddler).all()
    updated_count = 0
    failed_count = 0

    for toddler in toddlers:
        latest_measurement = db.query(Measurement)\
            .filter(Measurement.toddler_id == toddler.id)\
            .order_by(Measurement.measurement_date.desc())\
            .first()
            
        if not latest_measurement:
            continue # Lewati jika belum ada data pengukuran
            
        age_in_months = latest_measurement.current_age or calculate_age_in_months(toddler.date_of_birth, latest_measurement.measurement_date)
        
        predicted_status = predict_stunting_status(
            gender=toddler.gender.value,
            age=age_in_months,
            birth_weight=toddler.birth_weight,
            birth_length=toddler.birth_length,
            body_weight=latest_measurement.current_weight,
            body_length=latest_measurement.current_length,
            breastfeeding=latest_measurement.breastfeeding.value
        )
        
        if predicted_status != toddler.status:
            toddler.status = predicted_status
            updated_count += 1
        else:
            updated_count += 0 # Tetap dihitung sebagai proses yang berhasil dijalankan
            
    db.commit()

    return {
        "success": True, 
        "message": "Batch prediction completed",
        "data": {
            "total_toddlers_scanned": len(toddlers),
            "statuses_updated": updated_count
        }
    }

# ==========================================
# 3. TESTING MANUAL (INPUT DATA BEBAS)
# ==========================================
@router.post("/predict/manual")
def predict_manual_data(
    req: ManualPredictRequest, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """
    Endpoint untuk testing. Mengirim data secara manual tanpa mengambil dari DB.
    Tidak mengupdate DB, hanya mengembalikan hasil prediksi.
    """
    predicted_status = predict_stunting_status(
        gender=req.gender,
        age=req.age,
        birth_weight=req.birth_weight,
        birth_length=req.birth_length,
        body_weight=req.body_weight,
        body_length=req.body_length,
        breastfeeding=req.breastfeeding
    )

    return {
        "success": True, 
        "message": "Manual prediction successful",
        "data": {
            "input_data": req.dict(),
            "predicted_status": predicted_status
        }
    }