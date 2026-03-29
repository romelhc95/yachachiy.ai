import os
import sys
from sqlalchemy import text
# Add the project root to the sys.path to import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal, engine

def truncate_db():
    db = SessionLocal()
    try:
        print("Truncating courses and institutions tables (POSTGRES ONLY)...")
        # PostgreSQL specific truncation
        db.execute(text("TRUNCATE TABLE courses, institutions RESTART IDENTITY CASCADE"))
        
        db.commit()
        print("Truncation successful.")
    except Exception as e:
        db.rollback()
        print(f"Error truncating tables: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    truncate_db()
