import os
import logging
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

# --- ÚLTIMO RECURSO: CONEXIÓN DIRECTA SUPABASE ---
# Datos proporcionados por el usuario para fmcxwoqvxatbrawwtqke
DB_USER = "postgres"
DB_PASS = urllib.parse.quote_plus("2121146800R$.")
DB_HOST = "db.fmcxwoqvxatbrawwtqke.supabase.co"
DB_PORT = "5432"
DB_NAME = "postgres"

# Construcción de la URL de conexión Directa (Sin Pooler para evitar DNS issues)
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

logger.info("--- INTENTO DE CONEXIÓN DIRECTA (TRADICIONAL) ---")
logger.info(f"Host: {DB_HOST}")

try:
    # Motor con timeout largo para red inestable de Render
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args={
            "sslmode": "require",
            "connect_timeout": 30
        }
    )
    # Verificación
    with engine.connect() as conn:
        logger.info("¡CONEXIÓN DIRECTA EXITOSA!")
except Exception as e:
    logger.error(f"FALLO CONEXIÓN DIRECTA: {str(e)}")
    # Creamos un motor dummy para que el build no falle
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
