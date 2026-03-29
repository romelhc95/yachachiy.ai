import json
import os
import re
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import sys

# Agregamos la raíz al sys.path para poder importar api.models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.models import Institution, Course

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
    elif engine_name == 'sqlite':
        from sqlalchemy.dialects.sqlite import insert
        stmt = insert(table).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=index_elements,
            set_=update_dict
        )
        return stmt
    else:
        raise ValueError(f"Unsupported engine: {engine_name}")

def process_db(db_url, data):
    print(f"\nProcessing DB: {db_url}")
    # Fix for postgresql+psycopg2 if needed, but supabase urls usually start with postgresql://
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    now = datetime.now()

    try:
        for item in data:
            inst_name = item.get("institucion", "Desconocida")
            inst_slug = slugify(inst_name)
            
            # 3. Create institution if not exists
            inst = session.query(Institution).filter_by(slug=inst_slug).first()
            if not inst:
                print(f"Creando institución: {inst_name}")
                inst = Institution(
                    name=inst_name,
                    slug=inst_slug,
                    website_url=""
                )
                session.add(inst)
                session.commit()
            
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
            
            # 1. & 2. UPSERT based on (institution_id, name, slug) and update last_scraped_at
            # Using the ORM-level upsert approach because UUID generation for PK might complicate dialect-specific inserts
            # Wait, let's use standard application-level UPSERT to avoid dialect issues with UUIDs and defaults
            # Actually, "Realiza un UPSERT" - I will use the dialect insert.
            if engine.name in ['postgresql', 'sqlite']:
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
            else:
                existing = session.query(Course).filter_by(
                    institution_id=inst.id,
                    name=course_name,
                    slug=course_slug
                ).first()
                if existing:
                    existing.price_pen = course_values["price_pen"]
                    existing.mode = course_values["mode"]
                    existing.address = course_values["address"]
                    existing.duration = course_values["duration"]
                    existing.category = course_values["category"]
                    existing.url = course_values["url"]
                    existing.last_scraped_at = course_values["last_scraped_at"]
                else:
                    new_course = Course(**course_values)
                    session.add(new_course)
        
        session.commit()
        print("Datos insertados exitosamente.")
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

def main():
    json_path = os.path.join(os.path.dirname(__file__), 'processed_courses_2026.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    db_urls = []
    # Local BD
    db_urls.append("sqlite:///C:/xampp/htdocs/yachachiy_ai/yachachiy.db")
    
    # Supabase BD
    supabase_url = os.getenv("DATABASE_URL")
    if supabase_url:
        db_urls.append(supabase_url)
        
    for url in db_urls:
        process_db(url, data)

if __name__ == "__main__":
    main()
