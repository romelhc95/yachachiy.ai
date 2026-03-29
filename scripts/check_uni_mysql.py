
import os
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:@localhost:3307/yachachiy"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_uni():
    db = SessionLocal()
    try:
        # Check if UNI exists
        result = db.execute(text("SELECT id FROM institutions WHERE slug='uni'")).fetchone()
        if result:
            print(f"UNI found with ID: {result[0]}")
            return result[0]
        else:
            print("UNI not found. Seeding now...")
            # Create UNI institution if it doesn't exist
            new_id = str(uuid.uuid4()).replace('-', '') # MySQL IDs might be strings in models?
            # Let's check the schema first or just use the model
            from api.models import Institution
            uni = Institution(
                id=str(uuid.uuid4()).replace('-', ''),
                name="Universidad Nacional de Ingeniería (UNI)",
                slug="uni",
                address="Lima",
                website_url="https://posgrado.uni.edu.pe"
            )
            db.add(uni)
            db.commit()
            print(f"UNI created with ID: {uni.id}")
            return uni.id
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    check_uni()
