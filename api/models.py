from sqlalchemy import Column, String, DECIMAL, ForeignKey, TIMESTAMP, Text, CheckConstraint, UniqueConstraint, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .database import Base

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
    category = Column(String(100), server_default="Curso") # 'Maestría', 'Doctorado', 'Especialidad', 'Curso'
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

    __table_args__ = (
        CheckConstraint("price_pen >= 0", name="price_pen_positive"),
        CheckConstraint("mode IN ('Presencial', 'Híbrido', 'Remoto')", name="mode_check"),
        UniqueConstraint("institution_id", "name", "slug", name="unique_institution_course_slug"),
    )

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(Uuid(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    message = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
