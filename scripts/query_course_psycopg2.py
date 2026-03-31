import os
import urllib.parse
import psycopg2

PROJECT_ID = "fmcxwoqvxatbrawwtqke"
DB_USER = "postgres"
DB_PASS = "2121146800R$."
DB_HOST = "db.fmcxwoqvxatbrawwtqke.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
        sslmode='require'
    )
    cur = conn.cursor()
    # Broaden search to "Communication"
    cur.execute("SELECT name, slug FROM courses WHERE name ILIKE '%Communication%'")
    rows = cur.fetchall()
    print(f"Found {len(rows)} matches:")
    for row in rows:
        print(f"Name: {row[0]}, Slug: {row[1]}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error querying database: {e}")
