
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:@localhost:3307/yachachiy"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify_uni():
    db = SessionLocal()
    try:
        # Get UNI ID
        uni_id_row = db.execute(text("SELECT id FROM institutions WHERE slug='uni'")).fetchone()
        if not uni_id_row:
            print("UNI not found.")
            return
        
        uni_id = uni_id_row[0]
        # Count courses
        count = db.execute(text("SELECT count(*) FROM courses WHERE institution_id = :uni_id"), {"uni_id": uni_id}).fetchone()[0]
        print(f"Total UNI courses in MySQL: {count}")
        
        # Sample
        sample = db.execute(text("SELECT name, category, price_pen, mode FROM courses WHERE institution_id = :uni_id LIMIT 1"), {"uni_id": uni_id}).fetchone()
        if sample:
            print(f"Sample: {sample}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_uni()
