import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MySQL configuration
DB_HOST = os.getenv("LOCAL_DB_HOST") or "localhost"
DB_PORT = int(os.getenv("LOCAL_DB_PORT") or 3307)
DB_USER = os.getenv("LOCAL_DB_USER") or "root"
DB_PASS = os.getenv("LOCAL_DB_PASSWORD") or ""
DB_NAME = os.getenv("LOCAL_DB_NAME") or "yachachiy"

def reset_db():
    try:
        # Connect to MySQL server
        conn = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS)
        cursor = conn.cursor()
        
        # Drop and recreate
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        print(f"Database '{DB_NAME}' has been reset.")
        conn.close()
    except Exception as e:
        print(f"Error resetting local DB: {e}")

if __name__ == "__main__":
    reset_db()
