from sqlalchemy import create_engine, text
import os

def check_sqlite():
    db_path = "C:/xampp/htdocs/yachachiy_ai/yachachiy.db"
    if not os.path.exists(db_path):
        print(f"SQLite file {db_path} does not exist.")
        return
    
    url = f"sqlite:///{db_path}"
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            inst_count = conn.execute(text("SELECT count(*) FROM institutions")).scalar()
            course_count = conn.execute(text("SELECT count(*) FROM courses")).scalar()
            print(f"SQLite Institutions: {inst_count}")
            print(f"SQLite Courses: {course_count}")
    except Exception as e:
        print(f"Error checking SQLite: {e}")

if __name__ == "__main__":
    check_sqlite()
