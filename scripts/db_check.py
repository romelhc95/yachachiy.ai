import sqlite3
import os

db_path = r'C:\xampp\htdocs\yachachiy_ai\yachachiy.db'
if not os.path.exists(db_path):
    print(f"File not found: {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    print(f"Tables: {tables}")
    for table in [t[0] for t in tables]:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"Table {table}: {count} records")
        if count > 0:
            sample = cursor.execute(f"SELECT * FROM {table} LIMIT 1").fetchone()
            print(f"Sample from {table}: {sample}")
    conn.close()
