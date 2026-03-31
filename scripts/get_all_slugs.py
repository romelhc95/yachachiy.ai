import os
from sqlalchemy import create_engine, text

# Correct URL from migration script
REMOTE_URL = "postgresql+pg8000://postgres:2121146800R$.@db.fmcxwoqvxatbrawwtqke.supabase.co:5432/postgres"

try:
    engine = create_engine(REMOTE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT slug FROM courses ORDER BY slug ASC"))
        rows = result.fetchall()
        print(f"Total slugs: {len(rows)}")
        for row in rows:
            print(row[0])
except Exception as e:
    print(f"Error querying database: {e}")
