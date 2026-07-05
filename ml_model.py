import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# ==========================================
# PATH KONFIGURASI DATASETS
# ==========================================
DATASET_DIR = "app/datasets"
MODEL_PATH = os.path.join(DATASET_DIR, "stunting_xgb_model.json")
# Path encoder sesuai permintaan kamu
ENCODER_PATH = os.path.join(DATASET_DIR, "le_xgb_stunting_none.pkl") 

def train_model(csv_path=os.path.join(DATASET_DIR, "Stunting_Dataset.csv")):
    print("Memulai pelatihan model XGBoost...")
    
    # BUAT FOLDER JIKA BELUM ADA
    os.makedirs(DATASET_DIR, exist_ok=True)

    try:
        df = pd.read_csv(csv_path)
        
        # 1. Ambil 50 data pertama dan kolom yang diminta
        required_cols = ['Gender', 'Age', 'Birth Weight', 'Birth Length', 'Body Weight', 'Body Length', 'Breastfeeding', 'Stunting']
        df = df.iloc[:50][required_cols]
        
        # 2. Pisahkan Features (X) dan Target (y)
        feature_cols = ['Gender', 'Age', 'Birth Weight', 'Birth Length', 'Body Weight', 'Body Length', 'Breastfeeding']
        X = df[feature_cols]
        y = df['Stunting']
        
        # 3. Encode Data Kategorikal (Gender & Breastfeeding)
        le_gender = LabelEncoder()
        le_breast = LabelEncoder()

        le_gender.fit(["Male", "Female"])
        le_breast.fit(["Yes", "No"])
        
        X['Gender'] = le_gender.transform(X['Gender']) # Male=1, Female=0
        X['Breastfeeding'] = le_breast.transform(X['Breastfeeding']) # No=0, Yes=1
        
        # Encode Target (No = 0, Yes = 1)
        y = y.map({'No': 0, 'Yes': 1})
        
        # 4. Training XGBoost
        model = xgb.XGBClassifier(
            n_estimators=50, # Kecil karena data hanya 50
            max_depth=3, 
            learning_rate=0.1,
            objective='binary:logistic',
            use_label_encoder=False
        )
        model.fit(X, y)
        
        # 5. Simpan Model dan Encoders ke dalam folder app/datasets/
        model.save_model(MODEL_PATH)
        joblib.dump({'gender': le_gender, 'breast': le_breast}, ENCODER_PATH)
        
        print(f"Model berhasil dilatih dan disimpan di folder {DATASET_DIR}/ !")
        
    except Exception as e:
        print(f"Gagal melatih model: {e}")

def predict_stunting_status(gender: str, age: int, birth_weight: float, birth_length: float, 
                             body_weight: float, body_length: float, breastfeeding: str) -> str:
    """
    Melakukan prediksi status stunting.
    Mengembalikan: 'normal', 'risk', atau 'stunted'
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODER_PATH):
        # Fallback jika model atau encoder belum dilatih
        print("Warning: File model tidak ditemukan, mengembalikan status 'normal'")
        return "normal"

    # Load model dan encoder
    model = xgb.XGBClassifier()
    model.load_model(MODEL_PATH)
    encoders = joblib.load(ENCODER_PATH)
    
    # Siapkan data dalam format yang sama persis dengan saat training
    data = pd.DataFrame([[
        encoders['gender'].transform([gender.title()])[0],
        int(age),
        float(birth_weight),
        float(birth_length),
        float(body_weight),
        float(body_length),
        encoders['breast'].transform([breastfeeding.title()])[0]
    ]], columns=['Gender', 'Age', 'Birth Weight', 'Birth Length', 'Body Weight', 'Body Length', 'Breastfeeding'])
    
    # Prediksi probabilitas
    proba = model.predict_proba(data)[0]
    prob_stunted = proba[1] # Probabilitas terkena stunting (Kelas 1)
    
    # Klasifikasi berdasarkan probabilitas (Menggunakan logika Z-Score yang disesuaikan)
    if prob_stunted < 0.40:
        return "normal"
    elif prob_stunted < 0.70:
        return "risk"
    else:
        return "stunted"