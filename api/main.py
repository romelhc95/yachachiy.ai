from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .routes import router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Yachachiy.ai API",
    description="API for managing educational courses and institutions for Yachachiy.ai",
    version="1.0.0"
)

# CORS Configuration - Updated for robustness with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yachachiy-ai.pages.dev",
        "https://yachachiy-ai.pages.dev/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standard error handler to avoid exposing internal traces
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."}
    )

@app.on_event("startup")
async def startup_event():
    """
    Optimización de inicio para evitar bloqueos en el despliegue (Render).
    La conexión a la base de datos es perezosa (lazy) pero verificamos el conteo inicial para diagnóstico.
    """
    from .database import SessionLocal
    from .models import Institution, Course
    
    logger.info("Yachachiy.ai API startup initiated. Database connection is lazy.")
    
    db = SessionLocal()
    try:
        inst_count = db.query(Institution).count()
        course_count = db.query(Course).count()
        logger.info(f"DATOS CARGADOS: {inst_count} instituciones y {course_count} cursos encontrados en la base de datos.")
    except Exception as e:
        logger.error(f"Error al verificar la base de datos al inicio: {e}")
    finally:
        db.close()

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Yachachiy.ai API"}
