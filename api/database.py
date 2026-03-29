import os
import logging
import re
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

# Reparación FORZADA de conexión Supabase (Puerto 6543 + IPv4)
if DATABASE_URL:
    # Reemplazo directo solicitado
    if 'db.fmcxwoqvxatbrawwtqke.supabase.co:5432' in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace('db.fmcxwoqvxatbrawwtqke.supabase.co:5432', 'db.fmcxwoqvxatbrawwtqke.supabase.co:6543')
    
    # Asegurar que el puerto 6543 esté presente si es Supabase
    if "supabase.co" in DATABASE_URL and ":6543" not in DATABASE_URL:
        DATABASE_URL = re.sub(r'(@[^/:]+)(/|$)', r'\1:6543\2', DATABASE_URL)
        
    # Añadir explícitamente '?sslmode=require' si no está presente
    if "sslmode=require" not in DATABASE_URL:
        if "?" in DATABASE_URL:
            DATABASE_URL += "&sslmode=require"
        else:
            DATABASE_URL += "?sslmode=require"

# Imprimir un log claro según lo solicitado
safe_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
print(f"DATABASE_URL FINAL: {safe_url}")
logger.info(f"DATABASE_URL FINAL: {safe_url}")

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
