import os
import sys
from sqlalchemy import func

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal
from api.models import Course

def check_timestamps():
    db = SessionLocal()
    try:
        courses = db.query(Course).order_by(Course.last_scraped_at).all()
        for c in courses:
            print(f"{c.last_scraped_at} - {c.name}")
    finally:
        db.close()

if __name__ == "__main__":
    check_timestamps()
