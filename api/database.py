import os
import logging
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Configuración de logging profesional
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

# --- CREDENCIALES DE PRODUCCIÓN DEFINITIVA (SUPABASE IPv4) ---
# Usamos el Pooler Host específico para garantizar IPv4 y resolver error de Tenant
DB_HOST = "fmcxwoqvxatbrawwtqke.pooler.supabase.com"
DB_USER = "postgres.fmcxwoqvxatbrawwtqke"
DB_PASS = urllib.parse.quote("2121146800R$.")
DB_PORT = "6543"
DB_NAME = "postgres"

# Construcción de la URL de conexión robusta
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

logger.info("MODO PRODUCCIÓN: CONECTADO AL HOST DE PROYECTO SUPABASE")

try:
    # Motor de base de datos SIN SQLITE - Solo conexión real a la nube
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "sslmode": "require",
            "connect_timeout": 30,
            "application_name": "yachachiy_api"
        }
    )
    # Verificación de conexión inmediata
    with engine.connect() as conn:
        logger.info("¡CONEXIÓN EXITOSA CON SUPABASE!")
except Exception as e:
    logger.error(f"ERROR CRÍTICO DE CONEXIÓN: {str(e)}")
    # Fallback preventivo pero sin SQLite
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
