import sqlalchemy
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def test_mysql_connection():
    url = os.getenv("DATABASE_URL")
    print(f"Testing DATABASE_URL: {url}")
    if not url:
        print("DATABASE_URL not set in .env")
        return
    
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Successfully connected to the database.")
            print(f"Result: {result.fetchone()}")
            
            # Check database name
            res_db = conn.execute(text("SELECT DATABASE()"))
            print(f"Current Database: {res_db.fetchone()[0]}")
            
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_mysql_connection()
