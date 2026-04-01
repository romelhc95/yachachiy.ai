import os
import sys
import unicodedata
import re
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import ssl

# Load environment variables
load_dotenv()

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Direct Supabase Connection (using environment variables)
DATABASE_URL = os.getenv("SUPABASE_DB_URL")

def slugify(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', str(text))
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text

def heal_slugs():
    if not DATABASE_URL:
        print("Error: SUPABASE_DB_URL not set in .env")
        return

    print("Connecting to Supabase...")
    try:
        # Configuration for pg8000 + SSL if needed
        connect_args = {}
        if "pg8000" in DATABASE_URL:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connect_args["ssl_context"] = ssl_context

        engine = create_engine(DATABASE_URL, connect_args=connect_args)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("Fetching courses...")
        result = session.execute(text("SELECT id, name, slug FROM courses")).fetchall()
        
        print(f"Found {len(result)} courses.")
        
        updated_count = 0
        for row in result:
            course_id = row[0]
            old_slug = row[2]
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
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    heal_slugs()
