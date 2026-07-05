# seed.py
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app.database import engine, SessionLocal, Base
from app.models import User, Toddler, GenderEnum, RoleEnum, StatusEnum, Ingredient, MenuIngredient, Menu,LocalIngredientMap, Village
from app.utils import create_access_token


Base.metadata.create_all(bind=engine)

def get_or_create_ingredient(db, name):
    ing = db.query(Ingredient).filter(Ingredient.name == name).first()
    if not ing:
        ing = Ingredient(name=name)
        db.add(ing)
        db.flush()
    return ing.id

def seed_data():
    db = SessionLocal()
    try:
        # existing_user = db.query(User).filter(User.username == "admin").first()
        # if existing_user:
        #     print("Data sudah ada di database. Seeder dibatalkan.")
        #     return

        print("Menyimpan data awal...")

        desa_mappi = Village(name="Desa Mappi - Papua")
        db.add(desa_mappi)
        db.flush()

        # 1. Seed User
        user_admin = User(
            full_name="Administrator",
            username="admin",
            pin="123456", 
            gender=GenderEnum.male,
            role=RoleEnum.admin,
        )
        user_admin.village_id = desa_mappi.id
        user_cadre = User(
            full_name="Ny. Sri Rahayu",
            username="Ny. Sri Rahayu",
            pin="123456",
            gender=GenderEnum.female,
            role=RoleEnum.cadre
        )
        user_cadre.village_id = desa_mappi.id
        db.add(user_admin)
        db.add(user_cadre)

        # 2. Seed Toddler
        toddler_1 = Toddler(
            toddler_full_name="Ahmad Fauzi",
            biological_mother_name="Siti Aminah",
            date_of_birth="2026-07-4",
            gender=GenderEnum.male,
            birth_weight=3.2,
            birth_length=50.0,
            status=StatusEnum.normal
        )
        db.add(toddler_1)

        sagu = Ingredient(name="Sagu")
        ikan = Ingredient(name="Ikan Sungai")
        ubi = Ingredient(name="Ubi Jalar")
        db.add_all([sagu, ikan, ubi])
        db.flush()


        db.add(LocalIngredientMap(village_id=desa_mappi.id, ingredient_id=sagu.id, start_month=1, end_month=12))
        db.add(LocalIngredientMap(village_id=desa_mappi.id, ingredient_id=ikan.id, start_month=5, end_month=10))
        db.add(LocalIngredientMap(village_id=desa_mappi.id, ingredient_id=ubi.id, start_month=1, end_month=6))
        db.flush()

        # Menu Papeda (Butuh Sagu & Ikan)
        menu_papeda = Menu(name="Papeda", calories=150.0, cooking_method="Rebus")
        db.add(menu_papeda)
        db.flush()
        db.add(MenuIngredient(menu_id=menu_papeda.id, ingredient_id=sagu.id))
        db.add(MenuIngredient(menu_id=menu_papeda.id, ingredient_id=ikan.id))

        menu_kolak = Menu(name="Kolak Ubi", calories=120.0, cooking_method="Rebus gula merah")
        db.add(menu_kolak)
        db.flush()
        db.add(MenuIngredient(menu_id=menu_kolak.id, ingredient_id=ubi.id))


        print("Menyimpan Master Bahan Baku...")
        bahan_dict = {}
        bahan_baku_list = [
            "Singkong putih", "Ikan kembung", "Daging ayam", "Minyak kelapa", "Kaldu ayam", 
            "Jeruk manis", "Bayam", "Tepung jagung", "Tempe", "Pisang kepok", "Daun kangkung", 
            "Beras", "Telur puyuh", "Wortel", "Tomat", "Pepaya", "Ikan lele", "Bawang bombay", 
            "Bawang merah", "Bawang putih", "Sawi hijau", "Nasi putih", "Jagung muda", 
            "Labu kuning", "Telur ayam", "Pisang ambon", "Soun", "Daun salam", "Serai", "Jahe",
            "Daun jeruk", "Lengkuas", "Kentang", "Ikan mujair", "Kacang merah", "Bawang daun", 
            "Ubi jalar merah", "Buncis", "Tepung terigu", "Tepung roti", "Ikan Tongkol", "Tahu"
        ]
        for bahan in bahan_baku_list:
            bahan_dict[bahan] = get_or_create_ingredient(db, bahan)

        # ==========================================
        # 2. PETA KEKAYAAN DESA (CONTOH)
        # ==========================================
        print("Memetakan Bahan Lokal Desa Mappi...")
        peta_lokal = [
            ("Singkong putih", 1, 12), ("Ikan kembung", 5, 10), ("Ikan lele", 5, 10), 
            ("Ikan Tongkol", 6, 11), ("Ubi jalar merah", 1, 8), ("Jagung muda", 1, 12),
            ("Daun kangkung", 1, 12), ("Bayam", 1, 12), ("Labu kuning", 3, 9), ("Kentang", 4, 12)
        ]
        for nama_bahan, mulai, selesai in peta_lokal:
            db.add(LocalIngredientMap(
                village_id=desa_mappi.id, 
                ingredient_id=bahan_dict[nama_bahan], 
                start_month=mulai, end_month=selesai
            ))
        db.flush()

        print("Menyimpan Resep Menu Balita...")
        
        resep_buku = [
            {
                "name": "Bubur Singkong Kukuruyuk Saus Jeruk (6-8 Bulan)",
                "calories": 187.0, "cooking_method": "Rebus, Saring, Beri Saus",
                "min_age": 6, "max_age": 8,
                "bahan": ["Singkong putih", "Ikan kembung", "Daging ayam", "Minyak kelapa", "Kaldu ayam", "Jeruk manis", "Bayam"]
            },
            {
                "name": "Bubur Ikan Jagung (6-8 Bulan)",
                "calories": 190.6, "cooking_method": "Rebus dan Saring",
                "min_age": 6, "max_age": 8,
                "bahan": ["Tepung jagung", "Ikan kembung", "Tempe", "Pisang kepok", "Daun kangkung", "Minyak kelapa"]
            },
            {
                "name": "Nasi Tim Ikan Telur Puyuh Wortel (9-11 Bulan)",
                "calories": 202.7, "cooking_method": "Ditim",
                "min_age": 9, "max_age": 11,
                "bahan": ["Beras", "Ikan kembung", "Telur puyuh", "Wortel", "Tomat", "Minyak kelapa", "Kaldu ayam", "Pepaya"]
            },
            {
                "name": "Tim Ikan Menado (12-23 Bulan)",
                "calories": 234.3, "cooking_method": "Ditim",
                "min_age": 12, "max_age": 23,
                "bahan": ["Jagung muda", "Labu kuning", "Ikan kembung", "Telur ayam", "Daun kangkung", "Tomat", "Pisang ambon", "Minyak kelapa", "Kaldu ayam"]
            },
            {
                "name": "Soto Lamongan + Jeruk (12-23 Bulan)",
                "calories": 268.5, "cooking_method": "Rebus Kuah",
                "min_age": 12, "max_age": 23,
                "bahan": ["Nasi putih", "Daging ayam", "Soun", "Telur puyuh", "Wortel", "Minyak kelapa", "Jeruk manis", "Bawang merah", "Bawang putih", "Daun salam", "Serai", "Daun jeruk", "Lengkuas"]
            },
            {
                "name": "Nugget Sayuran (12-23 Bulan)",
                "calories": 270.5, "cooking_method": "Rebus, Haluskan, Goreng",
                "min_age": 12, "max_age": 23,
                "bahan": ["Ubi jalar merah", "Telur ayam", "Daging ayam", "Bayam", "Wortel", "Bawang putih", "Minyak kelapa"]
            },
            {
                "name": "Nasi Ayam Katsu, Tumis Sayuran + Melon (24-59 Bulan)",
                "calories": 403.3, "cooking_method": "Goreng Tepung, Tumis",
                "min_age": 24, "max_age": 59,
                "bahan": ["Nasi putih", "Daging ayam", "Tepung terigu", "Tepung jagung", "Tepung roti", "Telur ayam", "Wortel", "Buncis", "Jagung muda", "Bawang bombay", "Bawang putih"]
            },
            {
                "name": "Nasi Bakar Ikan Tongkol + Pepaya (24-59 Bulan)",
                "calories": 270.5, "cooking_method": "Bakar/Bungkus Daun Pisang",
                "min_age": 24, "max_age": 59,
                "bahan": ["Nasi putih", "Ikan Tongkol", "Bayam", "Tahu", "Minyak kelapa", "Jahe", "Lengkuas", "Serai", "Daun salam", "Bawang merah", "Bawang putih"]
            }
        ]

        for resep in resep_buku:
            new_menu = Menu(
                name=resep["name"], 
                calories=resep["calories"], 
                cooking_method=resep["cooking_method"],
                min_age_months=resep["min_age"],
                max_age_months=resep["max_age"]
            )
            db.add(new_menu)
            db.flush()
            
            for nama_bahan in resep["bahan"]:
                db.add(MenuIngredient(
                    menu_id=new_menu.id, 
                    ingredient_id=bahan_dict[nama_bahan]
                ))

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

if __name__ == "__main__":
    seed_data()
