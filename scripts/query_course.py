import os
import urllib.parse
from sqlalchemy import create_engine, text

PROJECT_ID = "fmcxwoqvxatbrawwtqke"
DB_USER = f"postgres.{PROJECT_ID}"
DB_PASS = "2121146800R$."
DB_HOST = "aws-0-us-east-1.pooler.supabase.com"
DB_PORT = "6543"
DB_NAME = "postgres"

# For pg8000, we'll try without manual sslmode first as Supabase might not strictly require it for small queries or it's implicitly handled.
# Or better, use the connection string as recommended for pg8000.
DATABASE_URL = f"postgresql+pg8000://{DB_USER}:{urllib.parse.quote(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name, slug FROM courses WHERE name ILIKE '%Communication Level Up%'"))
        rows = result.fetchall()
        print(f"Found {len(rows)} matches:")
        for row in rows:
            print(f"Name: {row[0]}, Slug: {row[1]}")
except Exception as e:
    print(f"Error querying database: {e}")
