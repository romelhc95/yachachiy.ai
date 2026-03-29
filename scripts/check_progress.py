import os
import sys
from sqlalchemy import func

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal
from api.models import Institution, Course

def report_progress():
    db = SessionLocal()
    try:
        institutions = db.query(Institution).all()
        print(f"Total institutions: {len(institutions)}")
        
        for inst in institutions:
            course_count = db.query(Course).filter(Course.institution_id == inst.id).count()
            print(f" - {inst.name} ({inst.slug}): {course_count} courses")
            
        pending = db.query(Institution).outerjoin(Course).group_by(Institution.id).having(func.count(Course.id) == 0).all()
        print(f"\nPending institutions: {len(pending)}")
        for inst in pending:
            print(f"   * {inst.name}")
            
    finally:
        db.close()

if __name__ == "__main__":
    report_progress()
