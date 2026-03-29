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

# CORS Configuration - Updated for robustness
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for debugging purposes
    allow_credentials=False, # Must be False if using "*" for allow_origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manual Middleware for CORS injection in ALL responses (including errors)
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    try:
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    except Exception as e:
        logger.error(f"Error in manual CORS middleware: {e}", exc_info=True)
        return JSONResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            },
            content={"error": "internal_server_error", "detail": str(e)}
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
