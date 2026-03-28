import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Limpiamos explícitamente cualquier rastro de la variable de entorno previa si contiene 'db'
if os.getenv("DATABASE_URL") and "@db:" in os.getenv("DATABASE_URL"):
    os.environ.pop("DATABASE_URL")

load_dotenv(override=True)

# Priorizamos la variable de entorno del .env, con fallback a SQLite local para exploración segura
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./yachachiy.db")

# Configuración específica para SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
  )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
