import os
import logging
import urllib.parse
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

# --- CONFIGURACIÓN DE BASE DE DATOS YACHACHIY (ESTANDARIZADA) ---
# Se prefiere el uso de DATABASE_URL desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)

if not DATABASE_URL:
    # Fallback para construcción manual si no existe DATABASE_URL completa
    PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID", "fmcxwoqvxatbrawwtqke")
    DB_USER = os.getenv("DB_USER", f"postgres.{PROJECT_ID}")
    DB_PASS = urllib.parse.quote(os.getenv("DB_PASS", "2121146800R$."))
    DB_HOST = os.getenv("DB_HOST", "aws-0-us-east-1.pooler.supabase.com")
    DB_PORT = os.getenv("DB_PORT", "6543")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    
    DATABASE_URL = f"postgresql+pg8000://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

logger.info(f"--- INICIALIZANDO CONEXIÓN A DB ---")

try:
    # Motor configurado para máxima compatibilidad con Supabase (PgBouncer)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "sslmode": "require",
            "connect_timeout": 30
        }
    )
    # Test opcional de lectura (solo loguea, no detiene si falla en init)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        logger.info("¡CONEXIÓN EXITOSA CON LA BASE DE DATOS!")
except Exception as e:
    logger.error(f"ERROR AL CONECTAR CON LA DB: {str(e)}")
    # Creamos un motor residual para evitar fallos catastróficos al importar
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
