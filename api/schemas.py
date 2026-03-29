from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

class InstitutionBase(BaseModel):
    name: str

class InstitutionResponse(InstitutionBase):
    model_config = ConfigDict(from_attributes=True)

class CourseBase(BaseModel):
    name: str
    slug: Optional[str] = None
    price_pen: Optional[Decimal] = None
    mode: Optional[str] = None
    address: Optional[str] = None
    duration: Optional[str] = None
    category: Optional[str] = "Curso"
    url: Optional[str] = None
    expected_monthly_salary: Optional[Decimal] = 0.00

class CourseResponse(CourseBase):
    id: UUID
    institution_id: UUID
    institution_name: str
    last_scraped_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    distance_km: Optional[float] = None
    roi_months: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class LeadCreate(BaseModel):
    course_id: UUID
    name: str
    email: str
    phone: str
    message: Optional[str] = None

class LeadResponse(LeadCreate):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
