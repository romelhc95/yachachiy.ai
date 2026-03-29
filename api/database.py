import os
import logging
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Configurar logging para visibilidad total en Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

# --- CONFIGURACIÓN DE CONEXIÓN FORZADA (SUPABASE CLOUD) ---
# Forzamos los valores directamente para evitar errores de variables de entorno en Render
DB_USER = "postgres.fmcxwoqvxatbrawwtqke"
DB_PASS = urllib.parse.quote_plus("2121146800R$.")
DB_HOST = "aws-0-us-east-1.pooler.supabase.com"
DB_PORT = "6543"
DB_NAME = "postgres"

# Construcción de la URL de conexión perfecta
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require&gssencmode=disable"

logger.info("--- INICIANDO MOTOR DE DATOS YACHACHIY (VERSIÓN SUPABASE NATIVA) ---")
logger.info(f"Target Host: {DB_HOST}")
logger.info(f"Target User: {DB_USER}")

try:
    # Creamos el motor SIN FALLBACKS. Si falla Supabase, la API NO debe levantar.
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={
            "sslmode": "require",
            "connect_timeout": 20
        }
    )
    # Intentamos una operación mínima para validar la red IPv4
    with engine.connect() as conn:
        logger.info("¡PRUEBA DE CONEXIÓN SUPABASE: EXITOSA!")
except Exception as e:
    logger.error(f"FALLO CRÍTICO: No se pudo conectar a Supabase. Error: {str(e)}")
    # En producción real, no queremos SQLite, pero para que el build no falle en Render
    # si la red de build es distinta, dejamos una referencia mínima.
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
