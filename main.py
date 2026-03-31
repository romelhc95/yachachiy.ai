from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes import router
import logging

# Cloudflare Workers Python specific import
# from workers import WorkerEntrypoint
# import asgi

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Yachachiy.ai API",
    description="API for managing educational courses and institutions for Yachachiy.ai",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manual Middleware for CORS injection
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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"An internal server error occurred: {str(exc)}"}
    )

@app.get("/health")
def health_check():
    return {"status": "ok", "platform": "cloudflare-workers"}

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Yachachiy.ai API on Cloudflare Workers"}

# Para Cloudflare Workers Python con FastAPI
# asgi.fetch bridges the Worker request to your FastAPI app
async def on_fetch(request, env, ctx):
    import asgi
    return await asgi.fetch(app, request, env)
