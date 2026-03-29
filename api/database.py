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

# Parámetros Base de Supabase (fmcxwoqvxatbrawwtqke)
PROJECT_ID = "fmcxwoqvxatbrawwtqke"
DB_USER = "postgres.fmcxwoqvxatbrawwtqke"
DB_PASS = "2121146800R$."
DB_HOST = "db.fmcxwoqvxatbrawwtqke.supabase.co"  # Host del Pooler IPv4
DB_PORT = "6543"
DB_NAME = "postgres"

def get_connection_url():
    """
    Construye la URL de conexión perfecta para el Pooler de Supabase en Render.
    """
    logger.info("INTENTANDO CONEXIÓN NATIVA CON IDENTIDAD FORZADA...")
    
    # Intentamos obtener la URL de Render para extraer la contraseña si fuera distinta
    env_url = os.getenv("DATABASE_URL", "")
    password = DB_PASS
    
    if env_url:
        try:
            # Limpieza básica
            env_url = env_url.strip().replace(" ", "")
            if "@" in env_url:
                # Intentamos extraer la contraseña real de la variable de entorno por seguridad
                parts = env_url.split("@")[0].split(":")
                if len(parts) > 2:
                    password = parts[2]
        except:
            pass

    # Codificar la contraseña para evitar errores con caracteres especiales ($ y .)
    encoded_pass = urllib.parse.quote_plus(password)
    
    # URL Final optimizada para IPv4 y Autenticación de Inquilino (Tenant)
    final_url = f"postgresql://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require&gssencmode=disable"
    
    logger.info(f"--- INICIO MOTOR DE DATOS YACHACHIY ---")
    logger.info(f"Conectando a Supabase Pooler: {DB_HOST}:{DB_PORT}")
    logger.info(f"Usuario Proyecto: {DB_USER}")
    
    return final_url

DATABASE_URL = get_connection_url()

# Creamos el motor con parámetros de resiliencia (SIN FALLBACK A SQLITE)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "sslmode": "require",
        "connect_timeout": 15
    }
)

# Prueba rápida de conexión obligatoria
with engine.connect() as conn:
    logger.info("¡CONEXIÓN EXITOSA CON SUPABASE!")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
