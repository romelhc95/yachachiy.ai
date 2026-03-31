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

# Detectar entorno local (MySQL) o cloud (Postgres)
LOCAL_DB = os.getenv("LOCAL_DB", "false").lower() == "true"
DB_HOST = os.getenv("DB_HOST", "localhost")

if LOCAL_DB or DB_HOST in ["localhost", "127.0.0.1"]:
    # --- CONFIGURACIÓN LOCAL (MySQL 3307) ---
    DB_USER = "root"
    DB_PASS = ""
    DB_PORT = "3307"
    DB_NAME = "yachachiy"
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    logger.info("--- INICIANDO CONEXIÓN LOCAL (MySQL 3307) ---")
    engine_args = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
else:
    # --- CONFIGURACIÓN SUPABASE CLOUD ---
    PROJECT_ID = "fmcxwoqvxatbrawwtqke"
    DB_USER = f"postgres.{PROJECT_ID}"
    DB_PASS = "2121146800R$."
    DB_HOST = "aws-0-us-east-1.pooler.supabase.com"
    DB_PORT = "5432"
    DB_NAME = "postgres"
    
    encoded_pass = urllib.parse.quote_plus(DB_PASS)
    DATABASE_URL = f"postgresql://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
    
    logger.info("--- INICIANDO CONEXIÓN SUPABASE CLOUD ---")
    engine_args = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {
            "sslmode": "require",
            "connect_timeout": 30,
            "application_name": "yachachiy_prod"
        }
    }

logger.info(f"Conectando a: {DB_HOST}")

try:
    engine = create_engine(DATABASE_URL, **engine_args)
    
    # VALIDACIÓN REAL: Intentamos una consulta simple
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        logger.info(f"¡CONEXIÓN ESTABLECIDA EXITOSAMENTE EN {'LOCAL' if (LOCAL_DB or DB_HOST in ['localhost', '127.0.0.1']) else 'NUBE'}!")
        
except Exception as e:
    logger.error(f"ERROR CRÍTICO DE CONEXIÓN: {str(e)}")
    # Fallback to current DATABASE_URL to avoid breaking downstream
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
