from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
import models, schemas, database, utils

router = APIRouter()

@router.get("/institutions", response_model=None)
async def get_institutions(db: Session = Depends(database.get_db)):
    from fastapi.responses import JSONResponse
    try:
        results = db.query(models.Institution).all()
        # Convert to list of dicts for JSONResponse
        processed = []
        for inst in results:
            processed.append({
                "id": str(inst.id),
                "name": inst.name,
                "slug": inst.slug,
                "website_url": inst.website_url,
                "address": inst.address
            })
        return processed
    except Exception as e:
        return JSONResponse(
            status_code=200, 
            content={"error": "db_connection_failed", "detail": str(e)}
        )

@router.get("/courses", response_model=None) # Changed to None to allow flexible error responses
async def get_courses(
    request: Request,
    name: Optional[str] = Query(None, description="Case-insensitive search by name"),
    mode: Optional[str] = Query(None, description="Filter by modality (Presencial, Híbrido, Remoto)"),
    max_price: Optional[Decimal] = Query(None, description="Maximum price in PEN"),
    db: Session = Depends(database.get_db)
):
    import logging
    from fastapi.responses import JSONResponse
    logger = logging.getLogger(__name__)

    logger.info("Intentando conectar a DB para obtener cursos...")
    try:
        query = db.query(
            models.Course.id,
            models.Course.institution_id,
            models.Course.name,
            models.Course.slug,
            models.Course.price_pen,
            models.Course.mode,
            models.Course.address,
            models.Course.duration,
            models.Course.category,
            models.Course.url,
            models.Course.expected_monthly_salary,
            models.Course.last_scraped_at,
            models.Course.created_at,
            models.Course.updated_at,
            models.Institution.name.label("institution_name"),
            models.Institution.location_lat,
            models.Institution.location_long
        ).join(models.Institution, models.Course.institution_id == models.Institution.id)

        if name:
            query = query.filter(models.Course.name.ilike(f"%{name}%"))
        
        if mode:
            query = query.filter(models.Course.mode == mode)
        
        if max_price is not None:
            query = query.filter(models.Course.price_pen <= max_price)

        results = query.all()
        logger.info(f"Datos recuperados: {len(results)} registros encontrados.")

        # IP Geolocation Logic
        client_ip = request.client.host
        client_coords = await utils.get_client_coordinates(client_ip)

        processed_results = []
        for row in results:
            # Convert row to dict for manipulation
            if hasattr(row, "_fields"):
                course_dict = dict(zip(row._fields, row))
            else:
                # Handle cases where row might already be a dict (like in some tests)
                course_dict = dict(row)
            
            # Geolocation distance
            distance = None
            if client_coords and course_dict.get("location_lat") and course_dict.get("location_long"):
                inst_coords = (float(course_dict["location_lat"]), float(course_dict["location_long"]))
                distance = utils.calculate_distance(client_coords, inst_coords)
            
            course_dict["distance_km"] = distance

            # ROI Calculation (Months to recover investment)
            # Formula: total_price / expected_salary
            roi_months = None
            price = course_dict.get("price_pen") or 0
            salary = course_dict.get("expected_monthly_salary") or 0
            
            if salary and salary > 0:
                roi_months = float(price / salary)
            
            course_dict["roi_months"] = roi_months

            processed_results.append(course_dict)

        # Sort by distance if available, otherwise just return results
        if client_coords:
            processed_results.sort(key=lambda x: x["distance_km"] if x["distance_km"] is not None else float('inf'))

        return processed_results
    except Exception as e:
        logger.error(f"DATABASE CONNECTION ERROR in get_courses: {e}", exc_info=True)
        # Devolvemos 200 con el error incrustado para saltar el CORS block y ver el error real en el frontend
        return JSONResponse(
            status_code=200, 
            content={"error": "db_connection_failed", "detail": str(e)}
        )

@router.get("/courses/{slug}", response_model=schemas.CourseResponse)
async def get_course_detail(
    slug: str,
    request: Request,
    db: Session = Depends(database.get_db)
):
    row = db.query(
        models.Course.id,
        models.Course.institution_id,
        models.Course.name,
        models.Course.slug,
        models.Course.price_pen,
        models.Course.mode,
        models.Course.address,
        models.Course.duration,
        models.Course.category,
        models.Course.url,
        models.Course.expected_monthly_salary,
        models.Course.last_scraped_at,
        models.Course.created_at,
        models.Course.updated_at,
        models.Institution.name.label("institution_name"),
        models.Institution.location_lat,
        models.Institution.location_long
    ).join(models.Institution, models.Course.institution_id == models.Institution.id)\
     .filter(models.Course.slug == slug).first()

    if not row:
        raise HTTPException(status_code=404, detail="Course not found")

    course_dict = dict(zip(row._fields, row))
    
    # Geolocation distance
    client_ip = request.client.host
    client_coords = await utils.get_client_coordinates(client_ip)
    
    distance = None
    if client_coords and course_dict.get("location_lat") and course_dict.get("location_long"):
        inst_coords = (float(course_dict["location_lat"]), float(course_dict["location_long"]))
        distance = utils.calculate_distance(client_coords, inst_coords)
    
    course_dict["distance_km"] = distance

    # ROI Calculation
    roi_months = None
    price = course_dict.get("price_pen") or 0
    salary = course_dict.get("expected_monthly_salary") or 0
    
    if salary and salary > 0:
        roi_months = float(price / salary)
    
    course_dict["roi_months"] = roi_months

    return course_dict

@router.post("/leads", response_model=schemas.LeadResponse)
async def create_lead(
    lead: schemas.LeadCreate,
    db: Session = Depends(database.get_db)
):
    # Check if course exists
    course = db.query(models.Course).filter(models.Course.id == lead.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db_lead = models.Lead(**lead.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead
