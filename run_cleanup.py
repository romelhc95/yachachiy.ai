import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def clean_and_verify():
    # Local SQLite
    print("--- Cleaning Local SQLite ---")
    sqlite_url = "sqlite:///./yachachiy.db"
    sqlite_engine = create_engine(sqlite_url)
    with sqlite_engine.connect() as conn:
        # SQLite doesn't support TRUNCATE, using DELETE
        conn.execute(text("DELETE FROM leads;"))
        conn.execute(text("DELETE FROM courses;"))
        conn.execute(text("DELETE FROM institutions;"))
        conn.commit()
        
        # Count
        leads_count = conn.execute(text("SELECT COUNT(*) FROM leads;")).scalar()
        courses_count = conn.execute(text("SELECT COUNT(*) FROM courses;")).scalar()
        institutions_count = conn.execute(text("SELECT COUNT(*) FROM institutions;")).scalar()
        print(f"Local DB verification: {leads_count} leads, {courses_count} courses, {institutions_count} institutions.")

    # Remote Supabase
    print("\n--- Cleaning Remote Supabase ---")
    load_dotenv(override=True)
    supabase_url = os.getenv("DATABASE_URL")
    if supabase_url:
        print(f"Connecting to {supabase_url.split('@')[1] if '@' in supabase_url else 'Supabase'}...")
        supabase_engine = create_engine(supabase_url)
        with supabase_engine.connect() as conn:
            # Read and execute the exact SQL file
            with open("db/cleanup_total.sql", "r") as f:
                sql = f.read()
            conn.execute(text(sql))
            conn.commit()
            
            # Count
            leads_count = conn.execute(text("SELECT COUNT(*) FROM leads;")).scalar()
            courses_count = conn.execute(text("SELECT COUNT(*) FROM courses;")).scalar()
            institutions_count = conn.execute(text("SELECT COUNT(*) FROM institutions;")).scalar()
            print(f"Supabase DB verification: {leads_count} leads, {courses_count} courses, {institutions_count} institutions.")
    else:
        print("DATABASE_URL not found in .env")

if __name__ == "__main__":
    clean_and_verify()
