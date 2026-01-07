"""
Construction AI Landing Page - FastAPI Application

Main application entry point that:
- Initializes FastAPI with configuration
- Sets up middleware and CORS
- Initializes database
- Includes all route blueprints
- Serves static files and templates
- Implements error handling
- Provides health checks and configuration endpoints

Usage:
    uvicorn app.main:app --reload
    
    Or with specific host/port:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
import os
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import init_db, engine, Base
from app.routes import forms, roi, booking

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Configure logging with detailed format
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('app.log')  # File output
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def initialize_database():
    """
    Initialize database tables on application startup.
    
    This function:
    - Creates all tables defined in models
    - Handles database connection errors gracefully
    - Logs initialization status
    """
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("✓ Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to initialize database: {str(e)}")
        logger.error("Database initialization failed. Check your DATABASE_URL configuration.")
        raise


# Initialize database before creating app
try:
    initialize_database()
except Exception as e:
    logger.critical(f"Cannot start application without database: {str(e)}")
    raise

# ============================================================================
# FASTAPI APPLICATION CREATION
# ============================================================================

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    debug=settings.debug
)

logger.info(f"FastAPI application created: {settings.app_name}")
logger.info(f"Debug mode: {settings.debug}")
logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# 1. GZIP Compression Middleware
# Compresses responses larger than 1000 bytes
app.add_middleware(
    GZIPMiddleware,
    minimum_size=1000
)
logger.info("✓ GZIP compression middleware added")

# 2. Trusted Host Middleware
# Prevents HTTP Host Header attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.CORS_ORIGINS.split(",") if isinstance(settings.CORS_ORIGINS, str) else ["*"]
)
logger.info("✓ Trusted Host middleware added")

# 3. CORS Middleware
# Enables Cross-Origin Resource Sharing
cors_origins = (
    settings.CORS_ORIGINS.split(",") 
    if isinstance(settings.CORS_ORIGINS, str) 
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600  # Cache preflight requests for 10 minutes
)
logger.info(f"✓ CORS middleware added - Allowed origins: {cors_origins}")

# ============================================================================
# STATIC FILES AND TEMPLATES
# ============================================================================

# Mount static files (CSS, JavaScript, images)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"✓ Static files mounted from {static_dir}")
else:
    logger.warning(f"⚠ Static files directory not found: {static_dir}")

# ============================================================================
# ROUTE INCLUSION
# ============================================================================

# Include all route blueprints
app.include_router(forms.router, tags=["forms"])
logger.info("✓ Contact form routes included")

app.include_router(roi.router, tags=["roi"])
logger.info("✓ ROI calculator routes included")

app.include_router(booking.router, tags=["booking"])
logger.info("✓ Demo booking routes included")

# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/", response_class=HTMLResponse, tags=["pages"])
async def root():
    """
    Serve the main landing page.
    
    Returns:
        HTML content of the landing page
    """
    try:
        templates_dir = Path(__file__).parent / "templates"
        index_path = templates_dir / "index.html"
        
        if index_path.exists():
            logger.debug(f"Serving landing page from {index_path}")
            return FileResponse(index_path)
        else:
            logger.warning(f"Landing page template not found: {index_path}")
            return """
            <html>
                <head>
                    <title>Construction AI Landing</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 40px; }
                        .error { color: #e74c3c; }
                        .info { color: #3498db; }
                    </style>
                </head>
                <body>
                    <h1>Construction AI Landing Page</h1>
                    <p class="error">⚠ Landing page template not found</p>
                    <p class="info">Please create <code>app/templates/index.html</code></p>
                    <p>In the meantime, you can:</p>
                    <ul>
                        <li>View API documentation: <a href="/api/docs">/api/docs</a></li>
                        <li>Check health status: <a href="/health">/health</a></li>
                        <li>Test contact form: POST /api/forms/contact</li>
                    </ul>
                </body>
            </html>
            """
    except Exception as e:
        logger.error(f"Error serving landing page: {str(e)}")
        return f"<h1>Error</h1><p>{str(e)}</p>"


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        Status information including app name, version, and debug mode
        
    Example Response:
        {
            "status": "healthy",
            "timestamp": "2026-01-05T10:30:00",
            "app": "Construction AI Landing",
            "version": "1.0.0",
            "debug": false,
            "database": "connected"
        }
    """
    try:
        # Test database connection
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "app": settings.app_name,
        "version": "1.0.0",
        "debug": settings.debug,
        "database": db_status,
        "environment": os.getenv("ENVIRONMENT", "development")
    }


@app.get("/health/ready", tags=["health"])
async def readiness_check():
    """
    Readiness check for Kubernetes or container orchestration.
    
    Returns:
        200 OK if application is ready to accept requests
        503 Service Unavailable if not ready
    """
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"ready": True}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"ready": False, "error": str(e)}
        )


@app.get("/health/live", tags=["health"])
async def liveness_check():
    """
    Liveness check for Kubernetes or container orchestration.
    
    Returns:
        200 OK if application is alive
    """
    return {"alive": True}


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@app.get("/api/config", tags=["config"])
async def get_config():
    """
    Get public configuration values.
    
    Returns:
        Public configuration that can be safely exposed to frontend
        
    Example Response:
        {
            "app_name": "Construction AI Landing",
            "app_description": "AI-powered project management for construction contractors",
            "debug": false,
            "cost_per_day_delay": 45662,
            "ai_solution_annual_cost": 5000,
            "delay_reduction_percentage": 0.65
        }
    """
    return {
        "app_name": settings.app_name,
        "app_description": settings.app_description,
        "debug": settings.debug,
        "cost_per_day_delay": settings.cost_per_day_delay,
        "ai_solution_annual_cost": settings.ai_solution_annual_cost,
        "delay_reduction_percentage": settings.delay_reduction_percentage,
        "avg_project_duration_days": settings.avg_project_duration_days
    }


@app.get("/api/version", tags=["config"])
async def get_version():
    """
    Get application version information.
    
    Returns:
        Version and build information
    """
    return {
        "version": "1.0.0",
        "app": settings.app_name,
        "build_date": "2026-01-05",
        "python_version": os.sys.version
    }


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.
    
    Returns:
        400 Bad Request with detailed validation error information
    """
    logger.warning(f"Validation error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions.
    
    Returns:
        500 Internal Server Error with error details (in debug mode)
    """
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True
    )
    
    if settings.debug:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "error": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )


# ============================================================================
# STARTUP AND SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Execute on application startup.
    
    Performs:
    - Database verification
    - Configuration validation
    - Resource initialization
    """
    logger.info("=" * 60)
    logger.info("APPLICATION STARTUP")
    logger.info("=" * 60)
    
    try:
        # Verify database connection
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("✓ Database connection verified")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")
        raise
    
    # Log configuration
    logger.info(f"✓ Application: {settings.app_name}")
    logger.info(f"✓ Debug mode: {settings.debug}")
    logger.info(f"✓ Database URL: {settings.database_url[:50]}...")
    logger.info(f"✓ SMTP Server: {settings.smtp_server}:{settings.smtp_port}")
    
    # Log ROI calculator settings
    logger.info(f"✓ Cost per day delay: ${settings.cost_per_day_delay:,.0f}")
    logger.info(f"✓ AI solution annual cost: ${settings.ai_solution_annual_cost:,.0f}")
    logger.info(f"✓ Delay reduction: {settings.delay_reduction_percentage * 100:.0f}%")
    
    logger.info("=" * 60)
    logger.info("APPLICATION READY")
    logger.info("=" * 60)
    logger.info(f"API Documentation: http://localhost:8000/api/docs")
    logger.info(f"Landing Page: http://localhost:8000/")
    logger.info(f"Health Check: http://localhost:8000/health")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute on application shutdown.
    
    Performs:
    - Resource cleanup
    - Database connection closure
    - Logging shutdown information
    """
    logger.info("=" * 60)
    logger.info("APPLICATION SHUTDOWN")
    logger.info("=" * 60)
    
    try:
        # Close database connections
        engine.dispose()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.error(f"✗ Error closing database: {str(e)}")
    
    logger.info("Application shutdown complete")
    logger.info("=" * 60)


# ============================================================================
# APPLICATION INFO ENDPOINT
# ============================================================================

@app.get("/api/info", tags=["info"])
async def get_app_info():
    """
    Get comprehensive application information.
    
    Returns:
        Detailed information about the application, configuration, and status
    """
    from app.database import SessionLocal
    
    try:
        db = SessionLocal()
        # Count contractors
        from app.models.contractor import Contractor
        contractor_count = db.query(Contractor).count()
        db.close()
    except Exception as e:
        logger.error(f"Error getting contractor count: {str(e)}")
        contractor_count = 0
    
    return {
        "application": {
            "name": settings.app_name,
            "description": settings.app_description,
            "version": "1.0.0",
            "debug": settings.debug
        },
        "endpoints": {
            "docs": "/api/docs",
            "redoc": "/api/redoc",
            "openapi": "/api/openapi.json",
            "health": "/health",
            "config": "/api/config"
        },
        "routes": {
            "forms": "/api/forms",
            "roi": "/api/roi",
            "booking": "/api/booking"
        },
        "database": {
            "type": "SQLite" if "sqlite" in settings.database_url else "PostgreSQL" if "postgresql" in settings.database_url else "Other",
            "contractors": contractor_count
        },
        "roi_calculator": {
            "cost_per_day_delay": settings.cost_per_day_delay,
            "ai_solution_annual_cost": settings.ai_solution_annual_cost,
            "delay_reduction_percentage": settings.delay_reduction_percentage,
            "avg_project_duration_days": settings.avg_project_duration_days
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# DOCUMENTATION ENDPOINT
# ============================================================================

@app.get("/api/endpoints", tags=["documentation"])
async def list_endpoints():
    """
    List all available API endpoints.
    
    Returns:
        Dictionary of all routes and their methods
    """
    routes = []
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name if hasattr(route, "name") else None
            })
    
    return {
        "total_routes": len(routes),
        "routes": sorted(routes, key=lambda x: x["path"])
    }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting FastAPI application...")
    
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.debug,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
