import os
import sys
from sqlalchemy import text

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal
from api.models import Course

def test_slug_accessibility():
    # 1. El nombre original que dio problemas
    original_name = 'Maestría en Ciencias en Química'
    # 2. El slug que esperamos después de la normalización
    expected_slug = 'maestria-en-ciencias-en-quimica-uni'
    
    db = SessionLocal()
    try:
        # Buscar el curso por su nombre
        course_by_name = db.query(Course).filter(Course.name == original_name).first()
        if not course_by_name:
            print(f"Error: Curso '{original_name}' no encontrado en la DB.")
            return False
        
        print(f"Curso encontrado: '{course_by_name.name}' con slug '{course_by_name.slug}'")
        
        # Verificar que el slug coincide con lo esperado (normalizado)
        if course_by_name.slug != expected_slug:
            print(f"Error: El slug '{course_by_name.slug}' no coincide con el esperado '{expected_slug}'")
            return False
        
        # 3. SIMULAR ACCESO POR URL (Búsqueda por slug)
        # Esto es lo que hace el frontend: fetch(`.../courses?slug=eq.${slug}`)
        course_by_slug = db.query(Course).filter(Course.slug == expected_slug).first()
        
        if course_by_slug:
            print(f"ÉXITO: Curso accesible mediante slug normalizado '{expected_slug}'")
            return True
        else:
            print(f"ERROR: Curso NO accesible mediante slug '{expected_slug}'")
            return False
            
    finally:
        db.close()

if __name__ == "__main__":
    success = test_slug_accessibility()
    if success:
        print("\nACCESSIBILITY TEST PASSED")
        sys.exit(0)
    else:
        print("\nACCESSIBILITY TEST FAILED")
        sys.exit(1)
