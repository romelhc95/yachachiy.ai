import os
import urllib.parse
from sqlalchemy import create_engine, text

# Use the credentials found in scripts\migrate_local_to_supabase.py
PROJECT_ID = "fmcxwoqvxatbrawwtqke"
DB_USER = "postgres"
DB_PASS = "2121146800R$."
DB_HOST = "db.fmcxwoqvxatbrawwtqke.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"

DATABASE_URL = f"postgresql+pg8000://{DB_USER}:{urllib.parse.quote(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

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
