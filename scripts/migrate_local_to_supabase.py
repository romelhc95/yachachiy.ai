import os
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import sys

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.models import Base, Institution, Course

def migrate():
    # Configuration
    LOCAL_URL = "mysql+pymysql://root@localhost:3307/yachachiy"
    REMOTE_URL = "postgresql://postgres:2121146800R$.@db.fmcxwoqvxatbrawwtqke.supabase.co:5432/postgres"
    
    print("--- INICIANDO MIGRACIÓN LOCAL -> SUPABASE ---")
    
    # Engines
    local_engine = create_engine(LOCAL_URL)
    remote_engine = create_engine(REMOTE_URL)
    
    # Create tables in remote if not exist
    print("Limpiando y recreando tablas en Supabase para asegurar el esquema...")
    Base.metadata.drop_all(bind=remote_engine)
    Base.metadata.create_all(bind=remote_engine)
    
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
            # Check if exists in remote by slug or id
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
                # Update existing
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
            # Check if exists in remote by institution_id, name, slug
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
                existing.price_pen = course.price_pen
                existing.mode = course.mode
                existing.address = course.address
                existing.duration = course.duration
                existing.category = course.category
                existing.url = course.url
                existing.description = course.description
                existing.syllabus = course.syllabus
                existing.target_audience = course.target_audience
                existing.requirements = course.requirements
                existing.certification = course.certification
                existing.start_date = course.start_date
                existing.benefits = course.benefits
                existing.expected_monthly_salary = course.expected_monthly_salary
                existing.last_scraped_at = course.last_scraped_at
                existing.updated_at = course.updated_at
        
        remote_session.commit()
        print("Cursos migrados/sincronizados.")
        print("--- MIGRACIÓN COMPLETADA EXITOSAMENTE ---")
        
    except Exception as e:
        remote_session.rollback()
        print(f"ERROR DURANTE LA MIGRACIÓN: {e}")
        import traceback
        traceback.print_exc()
    finally:
        local_session.close()
        remote_session.close()

if __name__ == "__main__":
    migrate()
