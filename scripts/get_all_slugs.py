import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import ssl

# Load environment variables from .env file
load_dotenv()

REMOTE_URL = os.getenv("SUPABASE_DB_URL")

def main():
    if not REMOTE_URL:
        print("Error: SUPABASE_DB_URL not set in .env")
        return

    try:
        # Configuration for pg8000 + SSL if needed
        connect_args = {}
        if "pg8000" in REMOTE_URL:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connect_args["ssl_context"] = ssl_context

        engine = create_engine(REMOTE_URL, connect_args=connect_args)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT slug FROM courses ORDER BY slug ASC"))
            rows = result.fetchall()
            print(f"Total slugs: {len(rows)}")
            for row in rows:
                print(row[0])
    except Exception as e:
        print(f"Error querying database: {e}")

if __name__ == "__main__":
    main()
