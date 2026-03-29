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

# --- CREDENCIALES DE PRODUCCIÓN (SUPABASE) ---
PROJECT_ID = "fmcxwoqvxatbrawwtqke"
DB_USER = f"postgres.{PROJECT_ID}"
DB_PASS = urllib.parse.quote_plus("2121146800R$.")
# Usamos el Pooler Host específico del proyecto para evitar el error 'Tenant not found'
DB_HOST = f"{PROJECT_ID}.pooler.supabase.com" 
DB_PORT = "6543"
DB_NAME = "postgres"

# Construcción de la URL de conexión robusta
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require&gssencmode=disable"

logger.info("--- INICIANDO MOTOR DE DATOS YACHACHIY V3 (POOLER ESPECÍFICO) ---")
logger.info(f"Conectando a Host Dedicado: {DB_HOST}")
logger.info(f"Identidad de Usuario: {DB_USER}")

try:
    # Motor de base de datos sin fallbacks a SQLite para evitar confusión con datos viejos
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
    # Verificación inmediata
    with engine.connect() as conn:
        logger.info("¡ALELUYA! CONEXIÓN ESTABLECIDA CON SUPABASE.")
except Exception as e:
    logger.error(f"FALLO DE RED/AUTENTICACIÓN: {str(e)}")
    # Creamos un motor vacío para que el build de Render no explote, 
    # pero la API dará error 500 hasta que conecte a la nube.
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
