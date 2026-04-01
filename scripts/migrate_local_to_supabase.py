import os
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import sys
import ssl

# Load environment variables
load_dotenv()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Ensure cloudflare_backend is in path for models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../cloudflare_backend')))

# We try to import models from the cloudflare_backend/worker.py since it has the SQLAlchemy definitions
try:
    from worker import Base, Institution, Course
except ImportError:
    print("Warning: Could not import models from worker.py. Migration might fail.")

def migrate():
    # Configuration from .env
    LOCAL_URL = os.getenv("LOCAL_DATABASE_URL") or "mysql+pymysql://root@localhost:3307/yachachiy"
    REMOTE_URL = os.getenv("SUPABASE_DB_URL")
    
    if not REMOTE_URL:
        print("Error: SUPABASE_DB_URL not set in .env")
        return

    print("--- INICIANDO MIGRACIÓN LOCAL -> SUPABASE ---")
    
    # SSL context for Supabase if using pg8000
    connect_args = {}
    if "pg8000" in REMOTE_URL:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args["ssl_context"] = ssl_context

    # Engines
    local_engine = create_engine(LOCAL_URL)
    remote_engine = create_engine(REMOTE_URL, connect_args=connect_args)
    
    # Sessions
    LocalSession = sessionmaker(bind=local_engine)
    RemoteSession = sessionmaker(bind=remote_engine)
    
    local_session = LocalSession()
    remote_session = RemoteSession()
    
    try:
        # 1. Migrate Institutions
        print("Migrando Instituciones...")
        local_institutions = local_session.query(Institution).all()
        print(f"Encontradas {len(local_institutions)} instituciones localmente.")
        
        for inst in local_institutions:
            existing = remote_session.query(Institution).filter_by(slug=inst.slug).first()
            if not existing:
                new_inst = Institution(
                    id=inst.id,
                    name=inst.name,
                    slug=inst.slug,
                    website_url=inst.website_url,
                    location_lat=inst.location_lat,
                    location_long=inst.location_long,
                    address=inst.address,
                    created_at=inst.created_at,
                    updated_at=inst.updated_at
                )
                remote_session.add(new_inst)
            else:
                existing.name = inst.name
                existing.website_url = inst.website_url
                existing.location_lat = inst.location_lat
                existing.location_long = inst.location_long
                existing.address = inst.address
                existing.updated_at = inst.updated_at
        
        remote_session.commit()
        print("Instituciones migradas/sincronizadas.")
        
        # 2. Migrate Courses
        print("Migrando Cursos...")
        local_courses = local_session.query(Course).all()
        print(f"Encontrados {len(local_courses)} cursos localmente.")
        
        for course in local_courses:
            existing = remote_session.query(Course).filter_by(
                institution_id=course.institution_id,
                name=course.name,
                slug=course.slug
            ).first()
            
            if not existing:
                new_course = Course(
                    id=course.id,
                    institution_id=course.institution_id,
                    name=course.name,
                    slug=course.slug,
                    price_pen=course.price_pen,
                    mode=course.mode,
                    address=course.address,
                    duration=course.duration,
                    category=course.category,
                    url=course.url,
                    description=course.description,
                    syllabus=course.syllabus,
                    target_audience=course.target_audience,
                    requirements=course.requirements,
                    certification=course.certification,
                    start_date=course.start_date,
                    benefits=course.benefits,
                    expected_monthly_salary=course.expected_monthly_salary,
                    last_scraped_at=course.last_scraped_at,
                    created_at=course.created_at,
                    updated_at=course.updated_at
                )
                remote_session.add(new_course)
            else:
                # Update
                for attr in ['price_pen', 'mode', 'address', 'duration', 'category', 'url', 'description', 
                            'syllabus', 'target_audience', 'requirements', 'certification', 'start_date', 
                            'benefits', 'expected_monthly_salary', 'last_scraped_at', 'updated_at']:
                    setattr(existing, attr, getattr(course, attr))
        
        remote_session.commit()
        print("Cursos migrados/sincronizados.")
        print("--- MIGRACIÓN COMPLETADA EXITOSAMENTE ---")
        
    except Exception as e:
        remote_session.rollback()
        print(f"ERROR DURANTE LA MIGRACIÓN: {e}")
    finally:
        local_session.close()
        remote_session.close()

if __name__ == "__main__":
    migrate()
