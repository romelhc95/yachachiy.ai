from fastapi import FastAPI, Request, status, APIRouter, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import Column, String, DECIMAL, ForeignKey, TIMESTAMP, Text, CheckConstraint, UniqueConstraint, Uuid, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from decimal import Decimal
import os
import logging
import urllib.parse
import uuid
import httpx
import math

# --- CONFIGURATION & LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Yachachiy.ai Cloudflare API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATABASE SETUP ---
Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # During local development without environment variables set in the shell
    try:
        from dotenv import load_dotenv
        load_dotenv()
        DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    except ImportError:
        pass

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- MODELS ---
class Institution(Base):
    __tablename__ = "institutions"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    website_url = Column(Text)
    location_lat = Column(DECIMAL(10, 8))
    location_long = Column(DECIMAL(11, 8))
    address = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    courses = relationship("Course", back_populates="institution")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(Uuid(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(255))
    price_pen = Column(DECIMAL(12, 2))
    mode = Column(String(50))
    address = Column(Text)
    duration = Column(String(100))
    category = Column(String(100), server_default="Curso")
    url = Column(Text)
    description = Column(Text)
    syllabus = Column(Text)
    target_audience = Column(Text)
    requirements = Column(Text)
    certification = Column(Text)
    start_date = Column(String(100))
    benefits = Column(Text)
    expected_monthly_salary = Column(DECIMAL(12, 2), default=0.00)
    last_scraped_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    institution = relationship("Institution", back_populates="courses")

# --- SCHEMAS ---
class CourseResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    name: str
    slug: str
    price_pen: Optional[float]
    mode: Optional[str]
    duration: Optional[str]
    category: Optional[str]
    institution_name: str
    roi_months: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)

# --- ROUTES ---
@app.get("/health")
def health():
    return {"status": "ok", "engine": "cloudflare-workers-python"}

@app.get("/institutions")
async def get_institutions(db: Session = Depends(get_db)):
    try:
        results = db.query(Institution).all()
        return [{"id": str(i.id), "name": i.name, "slug": i.slug} for i in results]
    except Exception as e:
        return JSONResponse(status_code=200, content={"error": "db_fail", "detail": str(e)})

@app.get("/courses")
async def get_courses(
    name: Optional[str] = Query(None),
    mode: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(
            Course.id, Course.name, Course.slug, Course.price_pen, Course.mode, 
            Course.category, Institution.name.label("institution_name"),
            Course.expected_monthly_salary
        ).join(Institution, Course.institution_id == Institution.id)
        
        if name: query = query.filter(Course.name.ilike(f"%{name}%"))
        if mode: query = query.filter(Course.mode == mode)
        
        results = query.all()
        processed = []
        for r in results:
            d = dict(zip(r._fields, r))
            # Basic ROI
            price = float(d["price_pen"] or 0)
            salary = float(d["expected_monthly_salary"] or 0)
            d["roi_months"] = price / salary if salary > 0 else None
            processed.append(d)
        return processed
    except Exception as e:
        return JSONResponse(status_code=200, content={"error": "db_fail", "detail": str(e)})

@app.get("/")
def root():
    return {"message": "Yachachiy API Cloudflare"}

# Worker Entrypoint
async def on_fetch(request, env, ctx):
    import asgi
    return await asgi.fetch(app, request, env)
