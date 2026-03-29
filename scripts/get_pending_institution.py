
import os
from sqlalchemy.orm import Session
from api.database import SessionLocal
from api.models import Institution, Course
from sqlalchemy import func

def get_pending_institution():
    db = SessionLocal()
    try:
        # Encuentra instituciones que no tengan cursos registrados
        pending = db.query(Institution).outerjoin(Course).group_by(Institution.id).having(func.count(Course.id) == 0).first()
        if pending:
            print(f"ID: {pending.id}")
            print(f"Name: {pending.name}")
            print(f"Website: {pending.website_url}")
        else:
            print("No pending institutions found.")
    finally:
        db.close()

if __name__ == "__main__":
    get_pending_institution()
