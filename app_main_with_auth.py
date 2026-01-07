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

Usage:
    uvicorn app.main:app --reload
"""

import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Response, status
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path

from app.config import settings
from app.database import init_db, get_db_info, check_db_connection
from app.security import get_security_headers, RateLimiter
from app.routes import auth, forms, roi, booking, contractor


class CacheControlStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 200 and not getattr(settings, "DEBUG", False):
            max_age = int(getattr(settings, "STATIC_CACHE_MAX_AGE", 86400))
            response.headers.setdefault("Cache-Control", f"public, max-age={max_age}")
        return response

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Create logger
logger = logging.getLogger(__name__)

_rate_limiter = RateLimiter(
    max_requests=getattr(settings, "RATE_LIMIT_REQUESTS", 100),
    window_seconds=getattr(settings, "RATE_LIMIT_WINDOW", 60),
)

# Configure logging
_handlers = [logging.StreamHandler(sys.stdout), logging.FileHandler(settings.LOG_FILE)]

if getattr(settings, "LOG_OUTPUT", "text") == "json":
    try:
        from pythonjsonlogger.jsonlogger import JsonFormatter

        formatter = JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        for h in _handlers:
            h.setFormatter(formatter)
        logging.basicConfig(level=settings.LOG_LEVEL, handlers=_handlers)
    except Exception:
        # Fall back to text logging if JSON formatter is unavailable
        logging.basicConfig(
            level=settings.LOG_LEVEL,
            format=settings.LOG_FORMAT,
            handlers=_handlers,
        )
else:
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
        handlers=_handlers,
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
        if settings.AUTO_CREATE_SCHEMA:
            logger.info("Initializing database schema (AUTO_CREATE_SCHEMA=true)...")
            init_db()
        else:
            logger.info("Skipping schema creation (use Alembic migrations)")
        
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
        
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {str(e)}")
        logger.error("=" * 80)
        raise

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan.

    Runs database initialization on startup.
    """

    initialize_database()
    yield

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
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
    GZipMiddleware,
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
async def https_redirect(request: Request, call_next):
    """Optionally redirect HTTP requests to HTTPS.

    Notes:
    - Skips /health so container health checks keep working.
    - Respects X-Forwarded-Proto for deployments behind a TLS-terminating proxy.
    """

    if not getattr(settings, "HTTPS_REDIRECT", False):
        return await call_next(request)

    if request.url.path == "/health":
        return await call_next(request)

    if getattr(settings, "TRUST_PROXY_HEADERS", False):
        forwarded_proto = request.headers.get("x-forwarded-proto")
        if forwarded_proto and forwarded_proto.lower() == "https":
            return await call_next(request)

    if request.url.scheme != "https":
        https_url = request.url.replace(scheme="https")
        return RedirectResponse(url=str(https_url), status_code=307)

    return await call_next(request)

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

    client_ip = request.client.host if request.client else "unknown"
    if getattr(settings, "TRUST_PROXY_HEADERS", False):
        xff = request.headers.get("x-forwarded-for")
        xri = request.headers.get("x-real-ip")
        if xff:
            client_ip = xff.split(",", 1)[0].strip() or client_ip
        elif xri:
            client_ip = xri.strip() or client_ip
    
    # Log request
    logger.debug(
        f"Request: {request.method} {request.url.path} "
        f"from {client_ip}"
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
async def rate_limit_requests(request: Request, call_next):
    """Apply a simple in-memory rate limit to sensitive endpoints.

    This is intentionally minimal and env-controlled:
    - Enabled when RATE_LIMIT_ENABLED=true
    - Targets only auth + contact form POST endpoints
    - Uses client IP (optionally from proxy headers) as identifier
    """

    if not getattr(settings, "RATE_LIMIT_ENABLED", False):
        return await call_next(request)

    if request.url.path == "/health":
        return await call_next(request)

    if request.method.upper() != "POST":
        return await call_next(request)

    limited_paths = {
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/refresh",
        "/api/auth/verify-email",
        "/api/auth/request-password-reset",
        "/api/auth/reset-password",
        "/api/auth/change-password",
        "/api/forms/contact",
    }
    if request.url.path not in limited_paths:
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    if getattr(settings, "TRUST_PROXY_HEADERS", False):
        xff = request.headers.get("x-forwarded-for")
        xri = request.headers.get("x-real-ip")
        if xff:
            client_ip = xff.split(",", 1)[0].strip() or client_ip
        elif xri:
            client_ip = xri.strip() or client_ip

    allowed = _rate_limiter.is_allowed(client_ip)
    limit = getattr(settings, "RATE_LIMIT_REQUESTS", 100)
    window = getattr(settings, "RATE_LIMIT_WINDOW", 60)
    remaining = _rate_limiter.get_remaining(client_ip) if allowed else 0

    if not allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too many requests"},
            headers={
                "Retry-After": str(window),
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Window": str(window),
            },
        )

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Window"] = str(window)
    return response


@app.middleware("http")
async def no_store_sensitive_responses(request: Request, call_next):
    """Prevent caching of sensitive API responses.

    Applies to:
    - /api/auth/*
    - /api/forms/contact
    """

    response = await call_next(request)

    path = request.url.path
    if path.startswith("/api/auth/") or path == "/api/forms/contact":
        response.headers["Cache-Control"] = "no-store"

    return response

# ============================================================================
# STATIC FILES
# ============================================================================

# Mount static files
static_dir = Path(__file__).parent / "app" / "static"
if static_dir.exists():
    app.mount("/static", CacheControlStaticFiles(directory=static_dir), name="static")
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
app.include_router(auth.router)
logger.info("✓ Authentication routes included")

# Include contact form routes
app.include_router(forms.router)
logger.info("✓ Contact form routes included")

# Include ROI calculator routes
app.include_router(roi.router)
logger.info("✓ ROI calculator routes included")

# Include demo booking routes
app.include_router(booking.router)
logger.info("✓ Demo booking routes included")

# Include contractor management routes
app.include_router(contractor.router)
logger.info("✓ Contractor management routes included")

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
    template_path = Path(__file__).parent / "app" / "templates" / "index.html"
    
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
    template_path = Path(__file__).parent / "app" / "templates" / "booking.html"
    
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
async def health_check():
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
        # Check database connection
        db_connected = check_db_connection()
        
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


@app.head(
    "/health",
    include_in_schema=False,
)
async def health_check_head():
    """HEAD variant of /health for load balancers and curl -I."""
    try:
        check_db_connection()
        return Response(status_code=status.HTTP_200_OK)
    except Exception:
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


@app.get(
    "/api/info",
    tags=["info"],
    summary="Application information",
    description="Get application information and available routes"
)
async def get_app_info():
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
                "tables": db_info.get("table_count", 0)
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
# ROOT ENDPOINT
# ============================================================================

@app.get(
    "/",
    include_in_schema=False
)
async def root():
    """Redirect to landing page."""
    return {"message": "Welcome to Construction AI Landing Page"}

# ============================================================================
# EXPORT
# ============================================================================

__all__ = ["app"]
