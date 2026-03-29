import os
import logging
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

# Compatibilidad IPv4 para Supabase en Render (Puerto 6543)
if DATABASE_URL and "supabase.co" in DATABASE_URL:
    if ":5432" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace(":5432", ":6543")
        logger.info("Supabase detected: Forcing port 6543 (Transaction Pooler) for IPv4 compatibility")
    elif ":6543" not in DATABASE_URL:
        # Inyectar puerto 6543 si no hay puerto definido
        import re
        DATABASE_URL = re.sub(r'(@[^/:]+)(/|$)', r'\1:6543\2', DATABASE_URL)
        logger.info("Supabase detected: Injecting port 6543 for IPv4 compatibility")

# Log seguro (sin password)
safe_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
logger.info(f"DATABASE_URL protocol: {'PostgreSQL' if 'postgresql' in DATABASE_URL else 'SQLite'}")
logger.info(f"Connecting to: {safe_url}")

try:
    # Configuración específica para SQLite
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(
            DATABASE_URL, connect_args={"check_same_thread": False}
        )
    else:
        # Añadimos sslmode, connect_timeout y pool_pre_ping para estabilidad en la nube
        engine = create_engine(
            DATABASE_URL,
            connect_args={
                "sslmode": "require",
                "connect_timeout": 10
            },
            pool_pre_ping=True,
            pool_recycle=3600
        )
except Exception as e:
    logger.error(f"CRITICAL: Failed to initialize database engine: {str(e)}")
    # No levantamos excepción aquí para permitir que la app inicie y muestre errores controlados
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
