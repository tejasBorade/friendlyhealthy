from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
from app.core.config import settings
from app.core.database import engine
from app.api.routes import (
    auth, doctors, appointments, prescriptions, patients,
    reports, billing, notifications, onboarding, medical_records
    # Commented out - tables don't exist: templates, favorites, signatures, tests, reminders, notification_preferences
    # Commented out -  routes moved to prescriptions.py: medical_history
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Healthcare Management Platform API")
    yield
    # Shutdown
    logger.info("Shutting down Healthcare Management Platform API")
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Comprehensive Healthcare Management Platform API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": exc.errors()
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # In development, return detailed error for debugging
    error_detail = str(exc) if settings.DEBUG else "An internal error occurred"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": error_detail,
                "type": type(exc).__name__ if settings.DEBUG else None
            }
        }
    )


# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(onboarding.router, prefix="/api/v1")
app.include_router(doctors.router, prefix="/api/v1")
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(appointments.router, prefix="/api/v1")
app.include_router(prescriptions.router, prefix="/api/v1")  # includes medical-history
app.include_router(medical_records.router, prefix="/api/v1/medical-records", tags=["Medical Records"])
# Commented out - tables don't exist:
# app.include_router(templates.router, prefix="/api/v1")
# app.include_router(favorites.router, prefix="/api/v1")
# app.include_router(signatures.router, prefix="/api/v1")
# app.include_router(tests.router, prefix="/api/v1")
# app.include_router(reminders.router, prefix="/api/v1")
# app.include_router(notification_preferences.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Healthcare Management Platform API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
