import os
import sys
import re
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text

# Add the project root to the sys.path to import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal, engine
from api.models import Institution

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

institutions_data = [
    {"name": "Pontificia Universidad Católica del Perú (PUCP)", "website_url": "https://www.pucp.edu.pe"},
    {"name": "Universidad Nacional Mayor de San Marcos (UNMSM)", "website_url": "https://www.unmsm.edu.pe"},
    {"name": "Universidad Peruana Cayetano Heredia (UPCH)", "website_url": "https://www.upch.edu.pe"},
    {"name": "Universidad de Lima (ULima)", "website_url": "https://www.ulima.edu.pe"},
    {"name": "Universidad del Pacífico (UP)", "website_url": "https://www.up.edu.pe"},
    {"name": "Universidad Nacional de Ingeniería (UNI)", "website_url": "https://www.uni.edu.pe"},
    {"name": "Universidad Peruana de Ciencias Aplicadas (UPC)", "website_url": "https://www.upc.edu.pe"},
    {"name": "Universidad Científica del Sur (UCSUR)", "website_url": "https://www.cientifica.edu.pe"},
    {"name": "Universidad de Piura (UDEP)", "website_url": "https://www.udep.edu.pe"},
    {"name": "Universidad Nacional Agraria La Molina (UNALM)", "website_url": "https://www.lamolina.edu.pe"},
    {"name": "Universidad San Ignacio de Loyola (USIL)", "website_url": "https://www.usil.edu.pe"},
    {"name": "Universidad Nacional de San Agustín (UNSA)", "website_url": "https://www.unsa.edu.pe"},
    {"name": "Universidad Nacional de Trujillo (UNT)", "website_url": "https://www.unitru.edu.pe"},
    {"name": "Universidad de San Martín de Porres (USMP)", "website_url": "https://www.usmp.edu.pe"},
    {"name": "Universidad César Vallejo (UCV)", "website_url": "https://www.ucv.edu.pe"},
    {"name": "Universidad Continental", "website_url": "https://www.continental.edu.pe"},
    {"name": "Universidad Nacional de Moquegua (UNAM)", "website_url": "https://www.unam.edu.pe"},
    {"name": "Universidad Nacional Toribio Rodríguez de Mendoza (UNTRM)", "website_url": "https://www.untrm.edu.pe"},
    {"name": "Universidad Federico Villarreal (UNFV)", "website_url": "https://www.unfv.edu.pe"},
    {"name": "Universidad Privada del Norte (UPN)", "website_url": "https://www.upn.edu.pe"},
    {"name": "CENTRUM PUCP Business School", "website_url": "https://centrum.pucp.edu.pe"},
    {"name": "ESAN Graduate School of Business", "website_url": "https://www.esan.edu.pe"},
    {"name": "Pacífico Business School (PBS)", "website_url": "https://pbs.edu.pe"},
    {"name": "PAD - Escuela de Dirección (UDEP)", "website_url": "https://www.pad.edu"}
]

def seed_institutions():
    db = SessionLocal()
    try:
        print(f"Engine URL: {engine.url}")
        print(f"Seeding {len(institutions_data)} institutions...")
        
        for data in institutions_data:
            slug = slugify(data["name"])
            
            # Use SQL text for UPSERT compatibility with SQLite/Postgres if needed
            # For simplicity in this script, we'll use ORM or core insert
            
            if "sqlite" in str(engine.url):
                # SQLite doesn't support ON CONFLICT in the same way with SQLAlchemy core as Postgres easily
                # but we can check existence or use raw SQL
                existing = db.query(Institution).filter(Institution.slug == slug).first()
                if existing:
                    existing.name = data["name"]
                    existing.website_url = data["website_url"]
                else:
                    new_inst = Institution(
                        name=data["name"],
                        slug=slug,
                        website_url=data["website_url"]
                    )
                    db.add(new_inst)
            elif "mysql" in str(engine.url):
                # MySQL UPSERT using SQLAlchemy core
                from sqlalchemy.dialects.mysql import insert as mysql_insert
                stmt = mysql_insert(Institution).values(
                    name=data["name"],
                    slug=slug,
                    website_url=data["website_url"]
                ).on_duplicate_key_update(
                    name=data["name"],
                    website_url=data["website_url"]
                )
                db.execute(stmt)
            else:
                # Postgres UPSERT
                stmt = insert(Institution).values(
                    name=data["name"],
                    slug=slug,
                    website_url=data["website_url"]
                ).on_conflict_do_update(
                    index_elements=['slug'],
                    set_=dict(name=data["name"], website_url=data["website_url"])
                )
                db.execute(stmt)
        
        db.commit()
        print("Institutions seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding institutions: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_institutions()
