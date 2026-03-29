import os
import sys
from sqlalchemy import text
import re

# Add the project root to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal, engine

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

institutions = [
    {"name": "Pontificia Universidad Católica del Perú", "website_url": "https://www.pucp.edu.pe"},
    {"name": "Universidad Peruana Cayetano Heredia", "website_url": "https://www.upch.edu.pe"},
    {"name": "Universidad Nacional Mayor de San Marcos", "website_url": "https://www.unmsm.edu.pe"},
    {"name": "Universidad Nacional de Ingeniería", "website_url": "https://www.uni.edu.pe"},
    {"name": "Universidad Nacional Agraria La Molina", "website_url": "https://www.lamolina.edu.pe"},
    {"name": "Universidad Científica del Sur", "website_url": "https://www.cientifica.edu.pe"},
    {"name": "Universidad Nacional de San Agustín", "website_url": "https://www.unsa.edu.pe"},
    {"name": "Universidad de Ingeniería y Tecnología", "website_url": "https://www.utec.edu.pe"},
    {"name": "Universidad Peruana de Ciencias Aplicadas", "website_url": "https://www.upc.edu.pe"},
    {"name": "Universidad de Lima", "website_url": "https://www.ulima.edu.pe"},
    {"name": "Universidad del Pacífico", "website_url": "https://www.up.edu.pe"},
    {"name": "ESAN Graduate School of Business", "website_url": "https://www.esan.edu.pe"},
    {"name": "CENTRUM PUCP", "website_url": "https://centrum.pucp.edu.pe"},
    {"name": "Universidad San Ignacio de Loyola", "website_url": "https://www.usil.edu.pe"},
    {"name": "Universidad de Piura", "website_url": "https://www.udep.edu.pe"},
    {"name": "Universidad Nacional de Trujillo", "website_url": "https://www.unitru.edu.pe"},
    {"name": "Universidad Nacional de San Antonio Abad del Cusco", "website_url": "https://www.unsaac.edu.pe"},
    {"name": "Universidad Peruana Unión", "website_url": "https://www.upeu.edu.pe"},
    {"name": "Universidad Privada del Norte", "website_url": "https://www.upn.edu.pe"},
    {"name": "Universidad Tecnológica del Perú", "website_url": "https://www.utp.edu.pe"}
]

def seed_institutions():
    db = SessionLocal()
    import uuid
    try:
        print(f"Seeding {len(institutions)} institutions...")
        for inst in institutions:
            slug = slugify(inst["name"])
            inst_id = str(uuid.uuid4())
            
            # Use SQL directly to handle UUID if necessary or use SQLAlchemy models
            if "sqlite" in str(engine.url):
                query = text("""
                    INSERT INTO institutions (id, name, slug, website_url)
                    VALUES (:id, :name, :slug, :website_url)
                """)
                db.execute(query, {"id": inst_id, "name": inst["name"], "slug": slug, "website_url": inst["website_url"]})
            else:
                # For PostgreSQL, we also provide the ID to avoid issues with defaults
                query = text("""
                    INSERT INTO institutions (id, name, slug, website_url)
                    VALUES (:id, :name, :slug, :website_url)
                    ON CONFLICT (slug) DO NOTHING
                """)
                db.execute(query, {"id": inst_id, "name": inst["name"], "slug": slug, "website_url": inst["website_url"]})
        
        db.commit()
        print("Seeding successful.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding institutions: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_institutions()
