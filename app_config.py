"""
Construction AI Landing Page - Application Configuration

This module contains all configuration settings for the FastAPI application.

Configuration can be set via:
1. Environment variables (.env file)
2. Default values in this file
3. Command-line arguments (when using uvicorn directly)

Environment Variables:
    ENVIRONMENT - Application environment (development, production)
    DEBUG - Enable debug mode (True, False)
    DATABASE_URL - Database connection string
    SMTP_USER - Email sender address
    SMTP_PASSWORD - Email sender password
    SMTP_HOST - SMTP server host
    SMTP_PORT - SMTP server port
    ALLOWED_ORIGINS - CORS allowed origins (comma-separated)
    SECRET_KEY - Secret key for security
    ALGORITHM - JWT algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES - Token expiration time
    LOG_LEVEL - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    MAX_UPLOAD_SIZE - Maximum file upload size (bytes)
    TIMEZONE - Application timezone
    DEMO_DURATION_MINUTES - Demo slot duration
    BUSINESS_HOURS_START - Business hours start (hour)
    BUSINESS_HOURS_END - Business hours end (hour)
    AVAILABLE_DAYS_AHEAD - Number of days to show available slots
    DELAY_COST_PER_DAY - Cost per day of project delay ($)
    AI_SOLUTION_ANNUAL_COST - Annual cost of AI solution ($)
    ROI_REDUCTION_PERCENTAGE - Estimated delay reduction (%)
"""

import os
from typing import List, Optional
from pathlib import Path
from functools import lru_cache

# ============================================================================
# .env LOADING
# ============================================================================

# This project relies on environment variables for configuration.
# To support local development, we load a `.env` file (if present)
# without requiring external dependencies.

def _load_env_file() -> None:
    try:
        env_path = Path(__file__).resolve().parent / ".env"
        if not env_path.exists():
            return

        for raw_line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception:
        # Do not fail application startup if .env parsing fails
        return


_load_env_file()


# ============================================================================
# BASE PATHS
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = Path(__file__).resolve().parent

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

def get_env_bool(key: str, default: bool = False) -> bool:
    """
    Get boolean environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not set
        
    Returns:
        Boolean value
    """
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')


def get_env_list(key: str, default: Optional[str] = None) -> List[str]:
    """
    Get list environment variable (comma-separated).
    
    Args:
        key: Environment variable name
        default: Default value if not set
        
    Returns:
        List of values
    """
    value = os.getenv(key, default or "")
    if not value:
        return []
    return [item.strip() for item in value.split(",")]


def get_env_int(key: str, default: int = 0) -> int:
    """
    Get integer environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not set
        
    Returns:
        Integer value
    """
    try:
        return int(os.getenv(key, default))
    except (ValueError, TypeError):
        return default

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

class Settings:
    """
    Application settings and configuration.
    
    All settings can be overridden via environment variables.
    """
    
    # ========================================================================
    # ENVIRONMENT
    # ========================================================================
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    """Application environment: development, staging, production"""
    
    DEBUG: bool = get_env_bool("DEBUG", ENVIRONMENT == "development")
    """Enable debug mode"""
    
    # ========================================================================
    # APPLICATION
    # ========================================================================
    
    APP_NAME: str = os.getenv("APP_NAME", "Construction AI Landing Page")
    """Application name"""
    
    APP_VERSION: str = "1.0.0"
    """Application version"""
    
    APP_DESCRIPTION: str = os.getenv("APP_DESCRIPTION", "AI-powered demo booking system for construction contractors")
    """Application description"""
    
    # ========================================================================
    # SERVER
    # ========================================================================
    
    HOST: str = os.getenv("HOST", os.getenv("APP_HOST", "0.0.0.0"))
    """Server host"""
    
    PORT: int = get_env_int("PORT", get_env_int("APP_PORT", 8000))
    """Server port"""
    
    WORKERS: int = get_env_int("WORKERS", 1 if DEBUG else 4)
    """Number of worker processes"""
    
    RELOAD: bool = DEBUG
    """Auto-reload on code changes"""
    
    # ========================================================================
    # DATABASE
    # ========================================================================
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./contractors.db"
    )
    """Database connection URL"""
    
    DATABASE_ECHO: bool = DEBUG
    """Log all SQL queries"""
    
    DATABASE_POOL_SIZE: int = get_env_int("DATABASE_POOL_SIZE", 5)
    """Database connection pool size"""
    
    DATABASE_MAX_OVERFLOW: int = get_env_int("DATABASE_MAX_OVERFLOW", 10)
    """Database connection pool max overflow"""
    
    DATABASE_POOL_RECYCLE: int = get_env_int("DATABASE_POOL_RECYCLE", 3600)
    """Database connection pool recycle time (seconds)"""
    
    DATABASE_POOL_PRE_PING: bool = True
    """Test connections before using them"""
    
    # ========================================================================
    # SECURITY
    # ========================================================================
    
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-change-in-production"
    )
    """Secret key for security operations"""
    
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    """JWT algorithm"""
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = get_env_int("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    """Access token expiration time (minutes)"""

    HTTPS_REDIRECT: bool = get_env_bool("HTTPS_REDIRECT", False)
    """If true, redirect http:// requests to https:// (recommended behind TLS terminator)."""

    TRUST_PROXY_HEADERS: bool = get_env_bool("TRUST_PROXY_HEADERS", False)
    """If true, trust X-Forwarded-Proto / X-Forwarded-For headers from a reverse proxy."""
    
    # ========================================================================
    # CORS
    # ========================================================================
    
    ALLOWED_ORIGINS: List[str] = get_env_list(
        "ALLOWED_ORIGINS",
        os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000")
    )
    """CORS allowed origins"""
    
    ALLOW_CREDENTIALS: bool = True
    """Allow credentials in CORS"""
    
    ALLOW_METHODS: List[str] = ["*"]
    """CORS allowed methods"""
    
    ALLOW_HEADERS: List[str] = ["*"]
    """CORS allowed headers"""
    
    # ============================================================================
    # TRUSTED HOST
    # ============================================================================
    
    TRUSTED_HOSTS: List[str] = get_env_list(
        "TRUSTED_HOSTS",
        os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,*.localhost")
    )
    """Trusted hosts for Trusted Host middleware"""
    
    # ========================================================================
    # LOGGING
    # ========================================================================
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO" if not DEBUG else "DEBUG")
    """Logging level"""
    
    LOG_FILE: str = os.getenv("LOG_FILE", "app.log")
    """Log file path"""

    LOG_OUTPUT: str = os.getenv("LOG_FORMAT", "text").lower()
    """Log output format selector: 'text' or 'json' (uses env var LOG_FORMAT for backward compatibility)."""

    # ========================================================================
    # DATABASE MIGRATIONS / SCHEMA MANAGEMENT
    # ========================================================================

    AUTO_CREATE_SCHEMA: bool = os.getenv("AUTO_CREATE_SCHEMA", "false").lower() in {"1", "true", "yes", "y", "on"}
    """If true, create tables on startup (dev/tests only). Prefer Alembic migrations in production."""
    
    _LOG_FORMAT_RAW: str = os.getenv("LOG_MESSAGE_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    """Log message format for text logging (printf-style)."""

    @property
    def LOG_FORMAT(self) -> str:
        """Backward-compatible log format string.

        If LOG_FORMAT is set to 'json', the app will configure a JSON formatter.
        Otherwise, returns the text log format string.
        """

        return self._LOG_FORMAT_RAW
    
    # ========================================================================
    # EMAIL
    # ========================================================================
    
    SMTP_USER: str = os.getenv("SMTP_USER", "your-email@gmail.com")
    """Email sender address"""
    
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "your-app-password")
    """Email sender password"""
    
    SMTP_HOST: str = os.getenv("SMTP_HOST", os.getenv("SMTP_SERVER", "smtp.gmail.com"))
    """SMTP server host"""
    
    SMTP_PORT: int = get_env_int("SMTP_PORT", 587)
    """SMTP server port"""
    
    SMTP_TLS: bool = get_env_bool("SMTP_TLS", True)
    """Use TLS for SMTP"""
    
    SENDER_NAME: str = os.getenv("SENDER_NAME", "Construction AI")
    """Email sender name"""
    
    SENDER_EMAIL: str = os.getenv("FROM_EMAIL", SMTP_USER)
    """Email sender address (same as SMTP_USER)"""
    
    # ========================================================================
    # FILE UPLOAD
    # ========================================================================
    
    MAX_UPLOAD_SIZE: int = get_env_int("MAX_UPLOAD_SIZE", 10 * 1024 * 1024)
    """Maximum file upload size (bytes) - default 10MB"""
    
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", str(APP_DIR / "uploads"))
    """Upload directory"""
    
    # ========================================================================
    # TIMEZONE
    # ========================================================================
    
    TIMEZONE: str = os.getenv("TIMEZONE", "America/New_York")
    """Application timezone"""
    
    # ========================================================================
    # DEMO BOOKING SETTINGS
    # ========================================================================
    
    DEMO_DURATION_MINUTES: int = get_env_int("DEMO_DURATION_MINUTES", 30)
    """Demo slot duration (minutes)"""
    
    BUSINESS_HOURS_START: int = get_env_int("BUSINESS_HOURS_START", 9)
    """Business hours start (hour, 24-hour format)"""
    
    BUSINESS_HOURS_END: int = get_env_int("BUSINESS_HOURS_END", 17)
    """Business hours end (hour, 24-hour format)"""
    
    AVAILABLE_DAYS_AHEAD: int = get_env_int("AVAILABLE_DAYS_AHEAD", 14)
    """Number of days to show available slots"""
    
    DEMO_TIMEZONE: str = TIMEZONE
    """Timezone for demo scheduling"""
    
    # ========================================================================
    # ROI CALCULATOR SETTINGS
    # ========================================================================
    
    DELAY_COST_PER_DAY: float = float(os.getenv("DELAY_COST_PER_DAY", "45662"))
    """Cost per day of project delay ($)"""
    
    AI_SOLUTION_ANNUAL_COST: float = float(os.getenv("AI_SOLUTION_ANNUAL_COST", "5000"))
    """Annual cost of AI solution ($)"""
    
    ROI_REDUCTION_PERCENTAGE: float = float(os.getenv("ROI_REDUCTION_PERCENTAGE", "65"))
    """Estimated delay reduction percentage (%)"""
    
    # ========================================================================
    # PAGINATION
    # ========================================================================
    
    DEFAULT_PAGE_SIZE: int = get_env_int("DEFAULT_PAGE_SIZE", 10)
    """Default page size for list endpoints"""
    
    MAX_PAGE_SIZE: int = get_env_int("MAX_PAGE_SIZE", 100)
    """Maximum page size for list endpoints"""
    
    # ========================================================================
    # CACHE
    # ========================================================================
    
    CACHE_ENABLED: bool = get_env_bool("CACHE_ENABLED", not DEBUG)
    """Enable caching"""
    
    CACHE_TTL: int = get_env_int("CACHE_TTL", 300)
    """Cache time-to-live (seconds)"""

    STATIC_CACHE_MAX_AGE: int = get_env_int("STATIC_CACHE_MAX_AGE", 86400)
    """Cache-Control max-age (seconds) for /static assets when not in DEBUG."""
    
    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    
    RATE_LIMIT_ENABLED: bool = get_env_bool("RATE_LIMIT_ENABLED", not DEBUG)
    """Enable rate limiting"""
    
    RATE_LIMIT_REQUESTS: int = get_env_int("RATE_LIMIT_REQUESTS", 100)
    """Rate limit requests per window"""
    
    RATE_LIMIT_WINDOW: int = get_env_int("RATE_LIMIT_WINDOW", 60)
    """Rate limit window (seconds)"""
    
    # ========================================================================
    # VALIDATION
    # ========================================================================
    
    MIN_PASSWORD_LENGTH: int = get_env_int("MIN_PASSWORD_LENGTH", 8)
    """Minimum password length"""
    
    MAX_PASSWORD_LENGTH: int = get_env_int("MAX_PASSWORD_LENGTH", 128)
    """Maximum password length"""
    
    # ========================================================================
    # FEATURES
    # ========================================================================
    
    FEATURE_EMAIL_ENABLED: bool = get_env_bool("FEATURE_EMAIL_ENABLED", True)
    """Enable email functionality"""
    
    FEATURE_BOOKING_ENABLED: bool = get_env_bool("FEATURE_BOOKING_ENABLED", True)
    """Enable demo booking"""
    
    FEATURE_ROI_CALCULATOR_ENABLED: bool = get_env_bool("FEATURE_ROI_CALCULATOR_ENABLED", True)
    """Enable ROI calculator"""
    
    FEATURE_CONTACT_FORM_ENABLED: bool = get_env_bool("FEATURE_CONTACT_FORM_ENABLED", True)
    """Enable contact form"""
    
    # ========================================================================
    # METHODS
    # ========================================================================
    
    def __init__(self):
        """Initialize settings."""
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate critical settings."""
        # Validate database URL
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set")

        # Fail closed in production for host/origin allowlists
        if self.is_production():
            # CORS: FastAPI/Starlette treats '*' as allow-all.
            if not self.ALLOWED_ORIGINS:
                raise ValueError("In production, CORS_ORIGINS/ALLOWED_ORIGINS must be set")
            if any(origin.strip() == "*" for origin in self.ALLOWED_ORIGINS):
                raise ValueError("In production, CORS_ORIGINS/ALLOWED_ORIGINS must not include '*'")

            # Trusted hosts: reject the allow-all wildcard, but allow patterns like '*.example.com'.
            if not self.TRUSTED_HOSTS:
                raise ValueError("In production, ALLOWED_HOSTS/TRUSTED_HOSTS must be set")
            if any(host.strip() == "*" for host in self.TRUSTED_HOSTS):
                raise ValueError("In production, ALLOWED_HOSTS/TRUSTED_HOSTS must not include '*'")
        
        # Validate SMTP settings if email is enabled
        if self.FEATURE_EMAIL_ENABLED:
            smtp_host = (self.SMTP_HOST or "").strip().lower()
            is_local_smtp = smtp_host in {"", "localhost", "127.0.0.1", "::1"}
            if not is_local_smtp and (not self.SMTP_USER or not self.SMTP_PASSWORD):
                raise ValueError("SMTP_USER and SMTP_PASSWORD must be set for email")
        
        # Validate timezone
        try:
            import zoneinfo
            zoneinfo.ZoneInfo(self.TIMEZONE)
        except Exception as e:
            raise ValueError(f"Invalid timezone: {self.TIMEZONE}") from e
    
    def get_database_url(self) -> str:
        """
        Get the database URL.
        
        Returns:
            Database connection URL
        """
        return self.DATABASE_URL
    
    def get_cors_config(self) -> dict:
        """
        Get CORS configuration.
        
        Returns:
            CORS configuration dictionary
        """
        return {
            "allow_origins": self.ALLOWED_ORIGINS,
            "allow_credentials": self.ALLOW_CREDENTIALS,
            "allow_methods": self.ALLOW_METHODS,
            "allow_headers": self.ALLOW_HEADERS,
        }
    
    def get_email_config(self) -> dict:
        """
        Get email configuration.
        
        Returns:
            Email configuration dictionary
        """
        return {
            "smtp_user": self.SMTP_USER,
            "smtp_password": self.SMTP_PASSWORD,
            "smtp_host": self.SMTP_HOST,
            "smtp_port": self.SMTP_PORT,
            "smtp_tls": self.SMTP_TLS,
            "sender_name": self.SENDER_NAME,
            "sender_email": self.SENDER_EMAIL,
        }
    
    def get_booking_config(self) -> dict:
        """
        Get booking configuration.
        
        Returns:
            Booking configuration dictionary
        """
        return {
            "demo_duration_minutes": self.DEMO_DURATION_MINUTES,
            "business_hours_start": self.BUSINESS_HOURS_START,
            "business_hours_end": self.BUSINESS_HOURS_END,
            "available_days_ahead": self.AVAILABLE_DAYS_AHEAD,
            "timezone": self.DEMO_TIMEZONE,
        }
    
    def get_roi_config(self) -> dict:
        """
        Get ROI calculator configuration.
        
        Returns:
            ROI configuration dictionary
        """
        return {
            "delay_cost_per_day": self.DELAY_COST_PER_DAY,
            "ai_solution_annual_cost": self.AI_SOLUTION_ANNUAL_COST,
            "roi_reduction_percentage": self.ROI_REDUCTION_PERCENTAGE,
        }
    
    def is_production(self) -> bool:
        """
        Check if running in production.
        
        Returns:
            True if production environment
        """
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        """
        Check if running in development.
        
        Returns:
            True if development environment
        """
        return self.ENVIRONMENT == "development"
    
    def __repr__(self) -> str:
        """String representation of settings."""
        return (
            f"Settings(environment={self.ENVIRONMENT}, "
            f"debug={self.DEBUG}, "
            f"database={self.DATABASE_URL})"
        )

# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

@lru_cache()
def get_settings() -> Settings:
    """
    Get settings singleton instance.
    
    Uses LRU cache to ensure only one instance is created.
    
    Returns:
        Settings instance
    """
    return Settings()

# ============================================================================
# MODULE-LEVEL INSTANCE
# ============================================================================

settings = get_settings()

# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "Settings",
    "get_settings",
    "settings",
    "BASE_DIR",
    "APP_DIR",
]
