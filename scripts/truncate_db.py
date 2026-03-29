import os
import sys
from sqlalchemy import text
# Add the project root to the sys.path to import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal, engine

def truncate_db():
    db = SessionLocal()
    try:
        print("Truncating courses and institutions tables...")
        # Check if we are using SQLite or PostgreSQL
        if "sqlite" in str(engine.url):
            # SQLite specific truncation
            db.execute(text("DELETE FROM courses"))
            db.execute(text("DELETE FROM institutions"))
            # Optional: Reset sqlite_sequence if it exists
            try:
                db.execute(text("DELETE FROM sqlite_sequence WHERE name='courses'"))
                db.execute(text("DELETE FROM sqlite_sequence WHERE name='institutions'"))
            except Exception:
                pass
        else:
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
