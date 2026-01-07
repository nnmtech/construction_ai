"""
Construction AI Landing Page - FastAPI Application

Main application entry point with all routes, middleware, and configuration.

Features:
- JWT authentication system
- Contact form management
- ROI calculator
- Demo booking system
- Contractor management
- Security middleware
- CORS support
- Error handling
- Logging
- Health checks
- Database session management

Usage:
    uvicorn app.main:app --reload
"""

import logging
import sys
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from pathlib import Path

from app.config import settings
from app.database import init_db, get_db_info, check_db_connection, get_db, engine, Base
from app.security import get_security_headers
from app.routes import auth, forms, roi, booking, contractor

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Create logger
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.LOG_FILE)
    ]
)

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def initialize_database():
    """Initialize database tables on application startup."""
    logger.info("=" * 80)
    logger.info("DATABASE INITIALIZATION")
    logger.info("=" * 80)
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        
        # Verify connection
        if check_db_connection():
            logger.info("✓ Database connection verified")
        else:
            logger.error("✗ Database connection failed")
            raise RuntimeError("Database connection failed")
        
        # Get database info
        db_info = get_db_info()
        logger.info(f"✓ Database type: {db_info.get('database_type', 'unknown')}")
        logger.info(f"✓ Tables created: {db_info.get('table_count', 0)}")
        
        # List created tables
        tables = db_info.get('tables', [])
        if tables:
            logger.info(f"✓ Tables: {', '.join(tables)}")
        
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {str(e)}")
        logger.error("=" * 80)
        raise

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

# Initialize database before creating app
initialize_database()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

logger.info("=" * 80)
logger.info("FASTAPI APPLICATION SETUP")
logger.info("=" * 80)
logger.info(f"✓ Application: {settings.APP_NAME} v{settings.APP_VERSION}")
logger.info(f"✓ Environment: {settings.ENVIRONMENT}")
logger.info(f"✓ Debug mode: {settings.DEBUG}")

# ============================================================================
# MIDDLEWARE STACK
# ============================================================================

# 1. GZIP Compression Middleware
app.add_middleware(
    GZIPMiddleware,
    minimum_size=1000
)
logger.info("✓ GZIP compression middleware added")

# 2. Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.TRUSTED_HOSTS
)
logger.info("✓ Trusted Host middleware added")

# 3. CORS Middleware
cors_config = settings.get_cors_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["allow_origins"],
    allow_credentials=cors_config["allow_credentials"],
    allow_methods=cors_config["allow_methods"],
    allow_headers=cors_config["allow_headers"]
)
logger.info(f"✓ CORS middleware added (origins: {len(cors_config['allow_origins'])})")

# ============================================================================
# CUSTOM MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Add security headers
    security_headers = get_security_headers()
    for header, value in security_headers.items():
        response.headers[header] = value
    
    # Add custom headers
    response.headers["X-API-Version"] = settings.APP_VERSION
    response.headers["X-Environment"] = settings.ENVIRONMENT
    
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = datetime.now(timezone.utc)
    
    # Log request
    logger.debug(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Request error: {str(e)}")
        raise
    
    # Calculate duration
    duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    # Log response
    logger.debug(
        f"Response: {response.status_code} "
        f"({duration:.3f}s)"
    )
    
    # Add timing header
    response.headers["X-Process-Time"] = str(duration)
    
    return response


@app.middleware("http")
async def manage_db_session(request: Request, call_next):
    """Manage database session for each request."""
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        # Session will be automatically closed by dependency injection
        pass
    
    return response

# ============================================================================
# STATIC FILES
# ============================================================================

# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"✓ Static files mounted from {static_dir}")
else:
    logger.warning(f"⚠ Static files directory not found: {static_dir}")

# ============================================================================
# ROUTE REGISTRATION
# ============================================================================

logger.info("=" * 80)
logger.info("ROUTE REGISTRATION")
logger.info("=" * 80)

# Include authentication routes
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
logger.info("✓ Authentication routes included (/api/auth)")

# Include contact form routes
app.include_router(forms.router, prefix="/api/forms", tags=["forms"])
logger.info("✓ Contact form routes included (/api/forms)")

# Include ROI calculator routes
app.include_router(roi.router, prefix="/api/roi", tags=["roi"])
logger.info("✓ ROI calculator routes included (/api/roi)")

# Include demo booking routes
app.include_router(booking.router, prefix="/api/booking", tags=["booking"])
logger.info("✓ Demo booking routes included (/api/booking)")

# Include contractor management routes
app.include_router(contractor.router, prefix="/api/contractors", tags=["contractors"])
logger.info("✓ Contractor management routes included (/api/contractors)")

# ============================================================================
# FRONTEND PAGES
# ============================================================================

@app.get(
    "/",
    tags=["frontend"],
    summary="Landing page",
    description="Serve landing page HTML"
)
async def get_landing_page():
    """
    Serve landing page.
    
    Returns the main landing page HTML with contact form, ROI calculator, and booking system.
    """
    template_path = Path(__file__).parent / "templates" / "index.html"
    
    if template_path.exists():
        return FileResponse(template_path, media_type="text/html")
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Landing page not found"}
        )


@app.get(
    "/booking",
    tags=["frontend"],
    summary="Booking page",
    description="Serve booking page with demo scheduling interface"
)
async def get_booking_page():
    """
    Serve booking page.
    
    Returns the booking page HTML with available time slots and demo scheduling.
    """
    template_path = Path(__file__).parent / "templates" / "booking.html"
    
    if template_path.exists():
        return FileResponse(template_path, media_type="text/html")
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Booking page not found"}
        )

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Check application health status"
)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    
    Returns application health status and database connection status.
    
    **Response:**
    - status: Application status (ok, degraded, error)
    - timestamp: Current timestamp
    - version: Application version
    - database: Database connection status
    """
    try:
        # Check database connection by executing a simple query
        db.execute("SELECT 1")
        db_connected = True
        
        status_code = "ok" if db_connected else "degraded"
        
        return {
            "status": status_code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": settings.APP_VERSION,
            "database": "connected" if db_connected else "disconnected"
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": settings.APP_VERSION,
                "database": "error",
                "error": str(e)
            }
        )


@app.get(
    "/api/info",
    tags=["info"],
    summary="Application information",
    description="Get application information and available routes"
)
async def get_app_info(db: Session = Depends(get_db)):
    """
    Get application information.
    
    Returns application metadata, configuration, and available routes.
    
    **Response:**
    - name: Application name
    - version: Application version
    - environment: Environment type
    - debug: Debug mode status
    - database: Database information
    - routes: Available API routes
    - documentation: API documentation URLs
    """
    try:
        db_info = get_db_info()
        
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "description": settings.APP_DESCRIPTION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "database": {
                "type": db_info.get("database_type", "unknown"),
                "tables": db_info.get("table_count", 0),
                "table_list": db_info.get("tables", [])
            },
            "routes": {
                "authentication": "/api/auth",
                "forms": "/api/forms",
                "roi": "/api/roi",
                "booking": "/api/booking",
                "contractors": "/api/contractors"
            },
            "documentation": {
                "swagger": "/api/docs",
                "redoc": "/api/redoc",
                "openapi": "/api/openapi.json"
            },
            "features": {
                "email": settings.FEATURE_EMAIL_ENABLED,
                "booking": settings.FEATURE_BOOKING_ENABLED,
                "roi_calculator": settings.FEATURE_ROI_CALCULATOR_ENABLED,
                "contact_form": settings.FEATURE_CONTACT_FORM_ENABLED
            }
        }
    except Exception as e:
        logger.error(f"App info error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )


@app.get(
    "/api/config",
    tags=["info"],
    summary="Public configuration",
    description="Get public application configuration"
)
async def get_public_config():
    """
    Get public configuration.
    
    Returns non-sensitive configuration that can be shared with clients.
    
    **Response:**
    - booking: Booking configuration
    - roi: ROI calculator configuration
    - timezone: Application timezone
    """
    return {
        "booking": settings.get_booking_config(),
        "roi": settings.get_roi_config(),
        "timezone": settings.TIMEZONE
    }


@app.get(
    "/api/models",
    tags=["info"],
    summary="Database models information",
    description="Get information about database models"
)
async def get_models_info(db: Session = Depends(get_db)):
    """
    Get database models information.
    
    Returns information about all database models and their relationships.
    """
    try:
        db_info = get_db_info()
        
        return {
            "models": {
                "User": {
                    "table": "users",
                    "description": "User authentication and account management",
                    "relationships": [
                        "ContactFormSubmission (1:N)",
                        "ROICalculation (1:N)",
                        "DemoBooking (1:N)"
                    ]
                },
                "Contractor": {
                    "table": "contractors",
                    "description": "Construction contractor/company information",
                    "relationships": [
                        "ContactFormSubmission (1:N)",
                        "ROICalculation (1:N)",
                        "DemoBooking (1:N)"
                    ]
                },
                "ContactFormSubmission": {
                    "table": "contact_form_submissions",
                    "description": "Contact form submissions",
                    "relationships": [
                        "Contractor (N:1)",
                        "User (N:1)"
                    ]
                },
                "ROICalculation": {
                    "table": "roi_calculations",
                    "description": "ROI calculation results",
                    "relationships": [
                        "Contractor (N:1)",
                        "User (N:1)"
                    ]
                },
                "DemoBooking": {
                    "table": "demo_bookings",
                    "description": "Demo appointment bookings",
                    "relationships": [
                        "Contractor (N:1)",
                        "User (N:1)"
                    ]
                }
            },
            "tables_created": db_info.get("table_count", 0),
            "tables_list": db_info.get("tables", [])
        }
    except Exception as e:
        logger.error(f"Models info error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail} "
        f"(path: {request.url.path})"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database exceptions."""
    logger.error(f"Database error: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database error occurred",
            "status_code": 500,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error" if settings.ENVIRONMENT == "production" else str(exc),
            "status_code": 500,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

# ============================================================================
# STARTUP AND SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("=" * 80)
    logger.info("APPLICATION STARTUP")
    logger.info("=" * 80)
    logger.info(f"✓ Server started at {datetime.now(timezone.utc).isoformat()}")
    logger.info(f"✓ Host: {settings.HOST}:{settings.PORT}")
    logger.info(f"✓ Workers: {settings.WORKERS}")
    logger.info(f"✓ Reload: {settings.RELOAD}")
    logger.info("=" * 80)
    logger.info("AVAILABLE ENDPOINTS")
    logger.info("=" * 80)
    logger.info("Frontend:")
    logger.info("  GET  /                    - Landing page")
    logger.info("  GET  /booking             - Booking page")
    logger.info("API Documentation:")
    logger.info("  GET  /api/docs            - Swagger UI")
    logger.info("  GET  /api/redoc           - ReDoc")
    logger.info("  GET  /api/openapi.json    - OpenAPI schema")
    logger.info("Utility Endpoints:")
    logger.info("  GET  /health              - Health check")
    logger.info("  GET  /api/info            - Application info")
    logger.info("  GET  /api/config          - Public config")
    logger.info("  GET  /api/models          - Models info")
    logger.info("Authentication:")
    logger.info("  POST /api/auth/register   - Register user")
    logger.info("  POST /api/auth/login      - Login user")
    logger.info("  POST /api/auth/refresh    - Refresh token")
    logger.info("  GET  /api/auth/me         - Get user info")
    logger.info("Forms:")
    logger.info("  POST /api/forms/contact   - Submit contact form")
    logger.info("ROI Calculator:")
    logger.info("  POST /api/roi/calculate   - Calculate ROI")
    logger.info("Booking:")
    logger.info("  GET  /api/booking/available-slots  - Get available slots")
    logger.info("  POST /api/booking/schedule-demo    - Schedule demo")
    logger.info("Contractors:")
    logger.info("  GET  /api/contractors     - List contractors")
    logger.info("  POST /api/contractors     - Create contractor")
    logger.info("  GET  /api/contractors/{id} - Get contractor")
    logger.info("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("=" * 80)
    logger.info("APPLICATION SHUTDOWN")
    logger.info("=" * 80)
    logger.info(f"✓ Server stopped at {datetime.now(timezone.utc).isoformat()}")
    logger.info("=" * 80)

# ============================================================================
# EXPORT
# ============================================================================

__all__ = ["app"]
