from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from brotli_asgi import BrotliMiddleware
from app.api.v1.router import api_router
from app.core import setup_logging, get_logger, AppException, ValidationMiddleware
import time
import os

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level=log_level)
logger = get_logger(__name__)

app = FastAPI(
    title="Surat Sertif PKL Service",
    description="""
API untuk generating dokumen PDF terkait PKL (Praktik Kerja Lapangan).

## Endpoints

### Letters
- **POST /api/v1/letters/surat-tugas** - Generate Surat Tugas PDF
- **POST /api/v1/letters/lembar-persetujuan** - Generate Lembar Persetujuan PKL
- **GET /api/v1/letters/download/{filename}** - Download generated PDF

### Health
- **GET /health** - Health check endpoint

## Features
- PDF generation dengan WeasyPrint
- Jinja2 templating
- Brotli compression
- Structured logging
- Request validation
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "API Support",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "letters",
            "description": "PDF letter generation endpoints"
        },
        {
            "name": "health",
            "description": "Health check and monitoring endpoints"
        }
    ]
)

# Track startup time
startup_time = time.time()


# Exception handler for custom exceptions
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    logger.error(f"{exc.code}: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )

# CORS configuration - environment-based
# Set CORS_ORIGINS env var (comma-separated) or use "*" for all origins
cors_origins_str = os.getenv("CORS_ORIGINS", "*")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",")] if cors_origins_str != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request validation middleware
app.add_middleware(ValidationMiddleware)

# Brotli compression for faster response delivery
app.add_middleware(BrotliMiddleware, minimum_size=500, gzip_fallback=True)

# Mount static files for logos/assets if needed
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"], summary="Health check")
async def health_check():
    """
    Check API health status.

    Returns the current status, version, and uptime of the service.
    Use this endpoint for monitoring and load balancer health checks.
    """
    uptime = time.time() - startup_time
    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime_seconds": round(uptime, 2)
    }

