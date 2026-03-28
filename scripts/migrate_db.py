from api.database import engine, Base, SessionLocal
from api.models import Institution, Course
from decimal import Decimal
import uuid

def migrate():
    print("Creando tablas en la base de datos remota...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if we already have data
    try:
        if db.query(Institution).count() > 0:
            print("La base de datos ya tiene datos. Saltando seeding.")
            db.close()
            return
    except Exception as e:
        print(f"Error al verificar datos: {e}. Intentando continuar...")

    print("Sembrando datos iniciales...")
    
    # Institutions
    utec_id = uuid.uuid4()
    utec = Institution(
        id=utec_id,
        name="UTEC",
        slug="utec",
        location_lat=Decimal("-12.1350"),
        location_long=Decimal("-77.0220")
    )
    
    upc_id = uuid.uuid4()
    upc = Institution(
        id=upc_id,
        name="UPC",
        slug="upc",
        location_lat=Decimal("-12.1040"),
        location_long=Decimal("-76.9630")
    )
    
    db.add(utec)
    db.add(upc)
    db.commit() # Commit here to ensure they exist before courses
    
    db = SessionLocal() # New session
    
    # Courses
    courses = [
        Course(
            id=uuid.uuid4(),
            institution_id=utec_id,
            name="Data Science Piloto",
            slug="data-science-piloto",
            price_pen=Decimal("5000.00"),
            mode="Remoto",
            address="Lima",
            duration="Variable",
            expected_monthly_salary=Decimal("3000.00")
        ),
        Course(
            id=uuid.uuid4(),
            institution_id=upc_id,
            name="Ingeniería de Software",
            slug="ingenieria-software",
            price_pen=Decimal("60000.00"),
            mode="Presencial",
            address="Monterrico",
            duration="10 ciclos",
            expected_monthly_salary=Decimal("4500.00")
        )
    ]
    
    for c in courses:
        db.add(c)
    
    db.commit()
    db.close()
    print("Migración y seeding completados con éxito.")

if __name__ == "__main__":
    migrate()
