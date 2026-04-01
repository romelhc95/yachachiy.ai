import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import ssl

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

def main():
    if not DATABASE_URL:
        print("Error: SUPABASE_DB_URL not set in .env")
        return

    try:
        # Configuration for pg8000 + SSL if needed
        connect_args = {}
        if "pg8000" in DATABASE_URL:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connect_args["ssl_context"] = ssl_context

        engine = create_engine(DATABASE_URL, connect_args=connect_args)
        with engine.connect() as conn:
            # Using parameter binding to prevent SQL Injection
            search_pattern = '%Communication Level Up%'
            query = text("SELECT name, slug FROM courses WHERE name ILIKE :pattern")
            result = conn.execute(query, {"pattern": search_pattern})
            rows = result.fetchall()
            
            print(f"Found {len(rows)} matches:")
            for row in rows:
                print(f"Name: {row[0]}, Slug: {row[1]}")
    except Exception as e:
        print(f"Error querying database: {e}")

if __name__ == "__main__":
    main()
