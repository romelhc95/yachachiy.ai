import json
import os
import re
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import sys

# Agregamos la raíz al sys.path para poder importar api.models y api.database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.models import Institution, Course
from api.database import DATABASE_URL, engine as db_engine

load_dotenv(override=True)

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def get_upsert_stmt(engine_name, table, values, index_elements, update_dict):
    if engine_name == 'postgresql':
        from sqlalchemy.dialects.postgresql import insert
        stmt = insert(table).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=index_elements,
            set_=update_dict
        )
        return stmt
    else:
        # Simplified for Production - only Postgres
        from sqlalchemy.dialects.postgresql import insert
        stmt = insert(table).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=index_elements,
            set_=update_dict
        )
        return stmt

def process_db(engine, data):
    print(f"\nProcessing DB: {engine.url}")
    Session = sessionmaker(bind=engine)
    session = Session()

    now = datetime.now()

    try:
        for item in data:
            inst_name = item.get("institucion", "Desconocida")
            inst_slug = slugify(inst_name)
            
            # Create institution if not exists
            inst = session.query(Institution).filter_by(slug=inst_slug).first()
            if not inst:
                print(f"Creando institución: {inst_name}")
                inst = Institution(
                    name=inst_name,
                    slug=inst_slug,
                    website_url=""
                )
                session.add(inst)
                session.flush() # To get the id
            
            course_name = item.get("nombre", "")
            course_slug = slugify(course_name)
            
            # Prepare values for course
            course_values = {
                "institution_id": inst.id,
                "name": course_name,
                "slug": course_slug,
                "price_pen": item.get("inversion", 0.0),
                "mode": item.get("modalidad", "Presencial"),
                "address": item.get("sede", ""),
                "duration": item.get("tiempo", ""),
                "category": item.get("category", "Curso"),
                "url": item.get("url", ""),
                "last_scraped_at": now
            }
            
            # UPSERT based on (institution_id, name, slug) and update last_scraped_at
            stmt = get_upsert_stmt(
                engine.name, 
                Course, 
                course_values, 
                ['institution_id', 'name', 'slug'], 
                {
                    "price_pen": course_values["price_pen"],
                    "mode": course_values["mode"],
                    "address": course_values["address"],
                    "duration": course_values["duration"],
                    "category": course_values["category"],
                    "url": course_values["url"],
                    "last_scraped_at": course_values["last_scraped_at"]
                }
            )
            session.execute(stmt)
        
        session.commit()
        print("Datos insertados exitosamente en SUPABASE.")
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

def main():
    json_path = os.path.join(os.path.dirname(__file__), 'processed_courses_2026.json')
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Usar el motor de base de datos de producción definido en api.database
    process_db(db_engine, data)

if __name__ == "__main__":
    main()
