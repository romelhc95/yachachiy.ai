from api.database import engine, Base
from api import models
import pymysql

def reset_tables():
    try:
        # Connect to MySQL and drop tables manually to ensure clean state
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            port=3307,
            database='yachachiy'
        )
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute("DROP TABLE IF EXISTS leads")
            cursor.execute("DROP TABLE IF EXISTS courses")
            cursor.execute("DROP TABLE IF EXISTS institutions")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        connection.close()
        
        # Create all tables using SQLAlchemy
        Base.metadata.create_all(bind=engine)
        print("Tables reset and created successfully.")
    except Exception as e:
        print(f"Error resetting tables: {e}")

if __name__ == "__main__":
    reset_tables()
