import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user_amauta:password_amauta@localhost:5432/amauta_db")

INSTITUTIONS = [
    ('Universidad Privada del Norte', 'upn', 'Lima, Trujillo, Cajamarca'),
    ('Universidad de San Martín de Porres', 'usmp', 'Lima, Chiclayo, Arequipa'),
    ('Universidad Peruana Unión', 'upeu', 'Lima, Tarapoto, Juliaca'),
    ('Senati', 'senati', 'Nacional'),
    ('Universidad del Pacífico', 'upacifico', 'Jesús María, Lima'),
    ('Universidad Nacional de Ingeniería', 'uni', 'Rímac, Lima'),
    ('Universidad de Lima', 'ulima', 'Santiago de Surco, Lima'),
    ('Universidad Autónoma del Perú', 'autonoma', 'Villa EL Salvador, Lima'),
    ('Universidad de Piura', 'udep', 'Piura, Lima'),
    ('Pontificia Universidad Católica del Perú', 'pucp', 'San Miguel, Lima'),
    ('Universidad Científica del Sur', 'cientifica', 'Villa, Lima'),
    ('Instituto Continental', 'continental', 'Huancayo, Lima, Cusco'),
    ('Universidad Nacional Mayor de San Marcos', 'unmsm', 'Cercado de Lima'),
    ('ESAN', 'esan', 'Santiago de Surco, Lima'),
    ('UNIR Perú', 'unir', 'Remoto'),
    ('ISIL', 'isil', 'Lima'),
    ('Data Science Research Peru', 'dsrp', 'Remoto/Lima'),
    ('IDAT', 'idat', 'Lima')
]

def seed_institutions():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        for name, slug, address in INSTITUTIONS:
            cur.execute("""
                INSERT INTO institutions (name, slug, address)
                VALUES (%s, %s, %s)
                ON CONFLICT (slug) DO NOTHING
            """, (name, slug, address))
        
        conn.commit()
        print(f"Successfully seeded {len(INSTITUTIONS)} institutions.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error seeding institutions: {e}")

if __name__ == "__main__":
    seed_institutions()
