import os
import sys
# Add the project root to the sys.path to import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal, engine
from api.models import Institution, Course

def check_db_status():
    db = SessionLocal()
    try:
        inst_count = db.query(Institution).count()
        course_count = db.query(Course).count()
        print(f"Institutions count: {inst_count}")
        print(f"Courses count: {course_count}")
        
        if course_count > 0:
            example = db.query(Course).first()
            print(f"Example Course: {example.__dict__}")
        else:
            print("No courses found yet.")
            
        if inst_count > 0:
            example_inst = db.query(Institution).first()
            print(f"Example Institution: {example_inst.__dict__}")
            
    except Exception as e:
        print(f"Error checking DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_db_status()
