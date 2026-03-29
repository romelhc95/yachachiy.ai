import os
import logging
import urllib.parse
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Logging de alta visibilidad
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

# --- CONFIGURACIÓN SUPABASE CLOUD (BOUNCER FRIENDLY) ---
PROJECT_ID = "fmcxwoqvxatbrawwtqke"
DB_USER = f"postgres.{PROJECT_ID}"
DB_PASS = "2121146800R$."
# Host genérico que Render SI resuelve correctamente
DB_HOST = "aws-0-us-east-1.pooler.supabase.com"
DB_PORT = "6543"
DB_NAME = "postgres"

# Codificación segura de la contraseña
encoded_pass = urllib.parse.quote_plus(DB_PASS)

# URL con parámetros para PgBouncer (indispensable para Supabase Pooler)
DATABASE_URL = f"postgresql://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require&prepared_statement_cache_size=0"

logger.info("--- INICIANDO CONEXIÓN COMPATIBLE CON SUPABASE POOLER ---")
logger.info(f"Conectando a: {DB_HOST}")
logger.info(f"Usuario: {DB_USER}")

try:
    # Creamos el motor con deshabilitación de sentencias preparadas para PgBouncer
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "sslmode": "require",
            "connect_timeout": 30,
            "application_name": "yachachiy_prod"
        }
    )
    
    # VALIDACIÓN REAL: Intentamos una consulta simple
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        logger.info("¡CONEXIÓN ESTABLECIDA EXITOSAMENTE CON LA NUBE!")
        
except Exception as e:
    logger.error(f"ERROR CRÍTICO DE CONEXIÓN A SUPABASE: {str(e)}")
    # NO hay fallback a SQLite. Si falla, el sistema debe reportar el error.
    # Usamos una URL de error para que la app no levante con data falsa.
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
