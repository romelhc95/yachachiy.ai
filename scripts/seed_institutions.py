from api.database import SessionLocal
from api.models import Institution

INSTITUTIONS = [
    ('Universidad Privada del Norte', 'upn', 'Lima, Trujillo, Cajamarca', 'https://www.upn.edu.pe'),
    ('Universidad de San Martín de Porres', 'usmp', 'Lima, Chiclayo, Arequipa', 'https://usmp.edu.pe'),
    ('Universidad Peruana Unión', 'upeu', 'Lima, Tarapoto, Juliaca', 'https://www.upeu.edu.pe'),
    ('Senati', 'senati', 'Nacional', 'https://www.senati.edu.pe'),
    ('Universidad del Pacífico', 'upacifico', 'Jesús María, Lima', 'https://www.up.edu.pe'),
    ('Universidad Nacional de Ingeniería', 'uni', 'Rímac, Lima', 'https://www.uni.edu.pe'),
    ('Universidad de Lima', 'ulima', 'Santiago de Surco, Lima', 'https://www.ulima.edu.pe'),
    ('Universidad Autónoma del Perú', 'autonoma', 'Villa EL Salvador, Lima', 'https://www.autonoma.pe'),
    ('Universidad de Piura', 'udep', 'Piura, Lima', 'https://udep.edu.pe'),
    ('Pontificia Universidad Católica del Perú', 'pucp', 'San Miguel, Lima', 'https://www.pucp.edu.pe'),
    ('Universidad Científica del Sur', 'cientifica', 'Villa, Lima', 'https://www.cientifica.edu.pe'),
    ('Instituto Continental', 'continental', 'Huancayo, Lima, Cusco', 'https://icontinental.edu.pe'),
    ('Universidad Nacional Mayor de San Marcos', 'unmsm', 'Cercado de Lima', 'https://unmsm.edu.pe'),
    ('ESAN', 'esan', 'Santiago de Surco, Lima', 'https://www.esan.edu.pe'),
    ('Universidad de Ingeniería y Tecnología', 'utec', 'Barranco, Lima', 'https://www.utec.edu.pe'),
    ('UNIR Perú', 'unir', 'Remoto', 'https://peru.unir.net'),
    ('ISIL', 'isil', 'Lima', 'https://isil.pe'),
    ('Data Science Research Peru', 'dsrp', 'Remoto/Lima', 'https://datascience.pe'),
    ('IDAT', 'idat', 'Lima', 'https://www.idat.edu.pe')
]

def seed_institutions():
    db = SessionLocal()
    try:
        for name, slug, address, url in INSTITUTIONS:
            # Verificar si ya existe
            existing = db.query(Institution).filter(Institution.slug == slug).first()
            if not existing:
                institution = Institution(name=name, slug=slug, address=address, website_url=url)
                db.add(institution)
            else:
                existing.website_url = url
                existing.address = address
        
        db.commit()
        print(f"Éxito: Se han sembrado/actualizado {len(INSTITUTIONS)} instituciones.")
    except Exception as e:
        db.rollback()
        print(f"Error sembrando instituciones: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_institutions()
