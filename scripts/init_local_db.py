import pymysql

def create_db():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            port=3307
        )
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS yachachiy")
        connection.close()
        print("Database 'yachachiy' verified/created.")
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    create_db()
