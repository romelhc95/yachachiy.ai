import os
import logging
import re
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Configurar logging para visibilidad en Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

# Priorizamos la variable de entorno del .env, con fallback a SQLite local
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./yachachiy.db")

# Limpieza profunda de la URL
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip().replace(" ", "")

# Si la URL de la base de datos es Postgres (como en Render/Supabase), nos aseguramos de usar el protocolo correcto
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def transform_supabase_url(url: str) -> str:
    """
    Detecta si la URL es de Supabase y fuerza el uso de pooling (IPv4),
    aplicando codificación de contraseña y usuario extendido.
    """
    if not url or ("supabase.co" not in url and "pooler.supabase.com" not in url):
        return url
    
    logger.info("--- REPARACIÓN DEFINITIVA IDENTIDAD SUPABASE POOLER ---")
    
    try:
        # Descomponer la DATABASE_URL de Render
        current_url = url.replace("postgres://", "postgresql://", 1) if url.startswith("postgres://") else url
        parsed = urllib.parse.urlparse(current_url)
        
        # Extraer dbname (path sin el leading slash)
        dbname = parsed.path.lstrip('/')
        if not dbname:
            dbname = "postgres"
            
        # Valores forzados para Reparación de Identidad
        user = "postgres.fmcxwoqvxatbrawwtqke"
        password_raw = "2121146800R$."
        password_encoded = urllib.parse.quote_plus(password_raw)
        host = "aws-0-us-east-1.pooler.supabase.com"
        port = "6543"
        
        # Reconstruir la URL con el host del pooler, puerto 6543 y sslmode=require
        new_url = f"postgresql://{user}:{password_encoded}@{host}:{port}/{dbname}?sslmode=require"
        
        logger.info("CONEXIÓN ESTABLECIDA CON EL POOLER DE AWS (IPv4)")
        return new_url
        
    except Exception as e:
        logger.error(f"Error transformando URL de identidad: {e}")
        return url

# Reparación FORZADA de conexión Supabase (Puerto 6543 + IPv4)
if DATABASE_URL:
    DATABASE_URL = transform_supabase_url(DATABASE_URL)

try:
    # Configuración específica para SQLite
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(
            DATABASE_URL, connect_args={"check_same_thread": False}
        )
    else:
        # Usamos la URL ya procesada
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600
        )
except Exception as e:
    logger.error(f"CRITICAL: Failed to initialize database engine: {str(e)}")
    engine = None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    if engine is None:
        logger.error("get_db called but engine is None")
        return
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()
