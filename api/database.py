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

def transform_supabase_url(url: str) -> str:
    """
    Detecta si la URL es de Supabase y fuerza el uso de pooling (IPv4),
    inyectando el ID del proyecto en el usuario para el Pooler.
    """
    if not url or ("supabase.co" not in url and "pooler.supabase.com" not in url):
        return url
    
    logger.info("--- INICIO REPARACIÓN IDENTIDAD SUPABASE POOLER ---")
    
    project_id = "fmcxwoqvxatbrawwtqke"
    pooling_host = "aws-0-us-east-1.pooler.supabase.com"
    target_host = f"db.{project_id}.supabase.co"
    
    # 1. Asegurar protocolo postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    # 2. Reemplazar host por el pooler si es necesario
    if target_host in url:
        logger.info(f"Detectado hostname original: {target_host}. Cambiando a pooler: {pooling_host}")
        url = url.replace(target_host, pooling_host)
    
    # 3. Forzar puerto 6543 para el Pooler (Transaction mode)
    if ":5432" in url:
        logger.info("Cambiando puerto 5432 a 6543.")
        url = url.replace(":5432", ":6543")
    elif ":6543" not in url:
        logger.info("Asegurando puerto 6543 en el host.")
        url = re.sub(r'(@[^/:]+)(/|$)', r'\1:6543\2', url)

    # 4. Reparación de Identidad: Inyectar project_id en el usuario
    # postgres -> postgres.fmcxwoqvxatbrawwtqke
    if f"postgres.{project_id}" not in url:
        logger.info(f"Inyectando ID de proyecto '{project_id}' en el usuario 'postgres'.")
        url = url.replace("postgresql://postgres:", f"postgresql://postgres.{project_id}:")

    # 5. Parámetros de conexión críticos
    params_to_add = ["sslmode=require", "gssencmode=disable"]
    for param in params_to_add:
        if param not in url:
            separator = "&" if "?" in url else "?"
            url += f"{separator}{param}"
            logger.info(f"Añadido parámetro: {param}")

    safe_url = url.split("@")[-1] if "@" in url else url
    logger.info(f"URL Procesada (Host/Port/Params): {safe_url}")
    logger.info("--- FIN REPARACIÓN IDENTIDAD ---")
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
