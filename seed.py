# seed.py
from app.database import engine, SessionLocal, Base
from app.models import User, Toddler, GenderEnum, RoleEnum, StatusEnum
from app.utils import create_access_token

print("Membuat tabel jika belum ada...")
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("Data sudah ada di database. Seeder dibatalkan.")
            return

        print("Menyimpan data awal...")

        # 1. Seed User
        user_admin = User(
            full_name="Administrator",
            username="admin",
            pin="123456", 
            gender=GenderEnum.male,
            role=RoleEnum.admin
        )
        user_cadre = User(
            full_name="Ny. Sri Rahayu",
            username="Ny. Sri Rahayu",
            pin="123456",
            gender=GenderEnum.female,
            role=RoleEnum.cadre
        )
        db.add(user_admin)
        db.add(user_cadre)

        # 2. Seed Toddler
        toddler_1 = Toddler(
            toddler_full_name="Ahmad Fauzi",
            biological_mother_name="Siti Aminah",
            date_of_birth="2024-01-15",
            gender=GenderEnum.male,
            birth_weight=3.2,
            birth_length=50.0,
            status=StatusEnum.normal
        )
        db.add(toddler_1)

        # Commit untuk menyimpan ke database
        db.commit()

        # Generate token untuk testing (opsional, agar kamu bisa langsung copy paste ke Postman)
        token_admin = create_access_token(data={"sub": user_admin.username})
        token_cadre = create_access_token(data={"sub": user_cadre.username})

        print("\n=== SEEDER BERHASIL ===")
        print(f"User Admin berhasil dibuat.")
        print(f"Token Admin: Bearer {token_admin}\n")
        print(f"User Kader berhasil dibuat.")
        print(f"Token Kader: Bearer {token_cadre}\n")

    except Exception as e:
        print(f"Error saat seeding: {e}")
        db.rollback()
    finally:
        db.close()
