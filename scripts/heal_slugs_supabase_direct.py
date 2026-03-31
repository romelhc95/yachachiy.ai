import os
import sys
import unicodedata
import re
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Direct Supabase Connection (using Pooler credentials)
PROJECT_ID = "fmcxwoqvxatbrawwtqke"
DB_USER = f"postgres.{PROJECT_ID}"
DB_PASS = "2121146800R$."
DB_HOST = "aws-0-us-east-1.pooler.supabase.com"
DB_PORT = "6543"
DB_NAME = "postgres"

DATABASE_URL = f"postgresql+pg8000://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

def slugify(text: str) -> str:
    if not text:
        return ""
    # Normalize unicode to decompose combined characters
    text = unicodedata.normalize('NFKD', str(text))
    # Encode to ASCII and decode back, ignoring non-ASCII characters
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Lowercase
    text = text.lower()
    # Replace non-alphanumeric with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Strip leading/trailing hyphens and multiple hyphens
    text = re.sub(r'-+', '-', text).strip('-')
    return text

def heal_slugs():
    print(f"Connecting to Supabase at {DB_HOST}...")
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("Fetching courses...")
        # Get all courses from Supabase
        result = session.execute(text("SELECT id, name, slug FROM courses")).fetchall()
        
        print(f"Found {len(result)} courses.")
        print("--- BEFORE HEALING ---")
        for row in result:
            print(f"ID: {row[0]}, Slug: {row[2]}")
            
        print("\n--- HEALING PROCESS ---")
        updated_count = 0
        for row in result:
            course_id = row[0]
            old_slug = row[2]
            # Simple normalization of the current slug (it might already have the institution suffix)
            new_slug = slugify(old_slug)
            
            if old_slug != new_slug:
                print(f"Updating ID {course_id}: '{old_slug}' -> '{new_slug}'")
                session.execute(
                    text("UPDATE courses SET slug = :new_slug WHERE id = :id"),
                    {"new_slug": new_slug, "id": course_id}
                )
                updated_count += 1
        
        session.commit()
        print(f"\nSuccessfully updated {updated_count} slugs.")
        
        print("\n--- AFTER HEALING ---")
        final_result = session.execute(text("SELECT name, slug FROM courses")).fetchall()
        for row in final_result:
            print(f"Name: {row[0]} | Slug: {row[1]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    heal_slugs()
