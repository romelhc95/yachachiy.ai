import psycopg2
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Warning: DATABASE_URL not set.")

# List of keywords that define a DATA course
DATA_KEYWORDS = [
    r"data science", r"ciencia de datos", r"inteligencia artificial", r"artificial intelligence",
    r"machine learning", r"aprendizaje automático", r"data analytics", r"analítica de datos",
    r"data engineering", r"ingeniería de datos", r"big data", r"deep learning", r"minería de datos"
]

def standardize_mode(mode_str):
    """Standardizes modality using common synonyms"""
    if not mode_str:
        return "Presencial"
    
    m = mode_str.lower()
    if any(k in m for k in ["remoto", "online", "virtual", "a distancia"]):
        return "Remoto"
    elif any(k in m for k in ["híbrido", "hybrid", "semipresencial"]):
        return "Híbrido"
    else:
        return "Presencial"

def is_data_course(name):
    """Checks if the course name matches DATA keywords"""
    if not name:
        return False
    name_lower = name.lower()
    return any(re.search(k, name_lower) for k in DATA_KEYWORDS)

def ai_parse_and_validate():
    """Simulates AI Parser: Validates courses and standardizes metadata"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # 1. Fetch all courses
        cur.execute("SELECT id, name, mode, price_pen FROM courses")
        courses = cur.fetchall()
        
        validated_count = 0
        deleted_count = 0
        
        for course_id, name, mode, price in courses:
            # Validate if it's a DATA course
            if not is_data_course(name):
                # If not a DATA course, we might want to flag or delete it for Yachachiy.ai
                # For this pilot, we'll mark them or just ignore them. 
                # Let's delete them to keep the "Google Flights of DATA" focus.
                cur.execute("DELETE FROM courses WHERE id = %s", (course_id,))
                deleted_count += 1
                continue
            
            # Standardize mode
            new_mode = standardize_mode(mode)
            
            # Update course with standardized data
            # For this simulation, we'll assume price is validated as is if > 0, 
            # or we could set a placeholder if it's 0.
            cur.execute("""
                UPDATE courses 
                SET mode = %s, updated_at = now()
                WHERE id = %s
            """, (new_mode, course_id))
            
            validated_count += 1
            
        conn.commit()
        print(f"AI Parser: Validated {validated_count} courses, removed {deleted_count} non-DATA courses.")
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error in AI Parser: {e}")

if __name__ == "__main__":
    ai_parse_and_validate()
