import psycopg2
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user_yachachiy:password_yachachiy@localhost:5432/yachachiy_db")

COURSES = [
    {
        "name": "Ingeniería en Ciencia de Datos",
        "institution_slug": "upn",
        "price_pen": 0.0,  # To be filled later or estimated
        "mode": "Híbrido",
        "address": "Sede Breña/Los Olivos, Lima",
        "url": "https://www.upn.edu.pe/carreras/ingenieria-en-ciencia-de-datos"
    },
    {
        "name": "Ingeniería de Ciencia de Datos",
        "institution_slug": "usmp",
        "price_pen": 0.0,
        "mode": "Presencial",
        "address": "Facultad de Ingeniería y Arquitectura, La Molina",
        "url": "https://usmp.edu.pe/ingenieria-de-ciencia-de-datos/"
    },
    {
        "name": "Ingeniería de Ciencia de Datos e Inteligencia Artificial",
        "institution_slug": "senati",
        "price_pen": 0.0,
        "mode": "Presencial",
        "address": "Sede Independencia, Lima",
        "url": "https://www.senati.edu.pe/especialidades/tecnologias-de-la-informacion/ingenieria-de-ciencia-de-datos-e-inteligencia-artificial"
    },
    {
        "name": "Maestría en Data Science",
        "institution_slug": "uni",
        "price_pen": 0.0,
        "mode": "Híbrido",
        "address": "FIEECS, Rímac",
        "url": "https://www.uni.edu.pe/posgrado/"
    },
    {
        "name": "Maestría en Data Analytics & AI",
        "institution_slug": "esan",
        "price_pen": 0.0,
        "mode": "Híbrido",
        "address": "Santiago de Surco, Lima",
        "url": "https://www.esan.edu.pe/maestrias/data-analytics-artificial-intelligence/"
    },
    {
        "name": "Maestría en Ciencia de Datos para los Negocios",
        "institution_slug": "ulima",
        "price_pen": 0.0,
        "mode": "Híbrido",
        "address": "Santiago de Surco, Lima",
        "url": "https://www.ulima.edu.pe/posgrado/maestrias/ciencia-de-datos-para-los-negocios"
    },
    {
        "name": "Ingeniería en Inteligencia Artificial y Ciencia de Datos",
        "institution_slug": "cientifica",
        "price_pen": 0.0,
        "mode": "Presencial",
        "address": "Sede Villa, Chorrillos",
        "url": "https://cientifica.edu.pe/carreras/ingenieria-en-inteligencia-artificial-y-ciencia-de-datos"
    },
    {
        "name": "Programa especializado en Data Engineering",
        "institution_slug": "dsrp",
        "price_pen": 0.0,
        "mode": "Remoto",
        "address": "Online",
        "url": "https://datascience.pe/especializacion-data-engineering/"
    }
]

def integrate_courses():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        count = 0
        for item in COURSES:
            # Get institution_id
            cur.execute("SELECT id FROM institutions WHERE slug = %s", (item['institution_slug'],))
            result = cur.fetchone()
            if not result:
                print(f"Institution {item['institution_slug']} not found.")
                continue
            inst_id = result[0]
            
            # Simple slug generation from name
            course_slug = item['name'].lower().replace(" ", "-").replace("/", "-")[:255]
            
            # Upsert course
            cur.execute("""
                INSERT INTO courses (institution_id, name, slug, price_pen, mode, address, url, last_scraped_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (institution_id, name, slug) DO UPDATE SET
                    price_pen = EXCLUDED.price_pen,
                    mode = EXCLUDED.mode,
                    address = EXCLUDED.address,
                    url = EXCLUDED.url,
                    last_scraped_at = EXCLUDED.last_scraped_at
            """, (inst_id, item['name'], course_slug, item['price_pen'], item['mode'], item['address'], item['url'], datetime.now()))
            count += 1
            
        conn.commit()
        print(f"Successfully integrated {count} new courses.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error integrating courses: {e}")

if __name__ == "__main__":
    integrate_courses()
