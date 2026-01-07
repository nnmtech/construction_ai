# app/config.py - Configuration Guide

## Overview

The `config.py` file contains all application configuration settings and can be overridden via environment variables.

**Purpose:**
- Centralize configuration management
- Support multiple environments (development, staging, production)
- Allow environment-specific settings
- Provide sensible defaults
- Enable easy configuration via environment variables

---

## Configuration Methods

### 1. Environment Variables (.env file)

Create a `.env` file in the project root:

```bash
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=sqlite:///./construction_ai.db
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 2. Default Values

Hardcoded defaults in `config.py`:

```python
DEBUG: bool = get_env_bool("DEBUG", ENVIRONMENT == "development")
```

### 3. Command-line Arguments

When using uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Configuration Categories

### 1. Environment Settings

| Setting | Default | Description |
|---------|---------|-------------|
| ENVIRONMENT | development | Environment type |
| DEBUG | True (dev) | Enable debug mode |

**Usage:**
```python
from app.config import settings

if settings.is_production():
    # Production-specific code
    pass
```

### 2. Application Settings

| Setting | Default | Description |
|---------|---------|-------------|
| APP_NAME | Construction AI Landing Page | Application name |
| APP_VERSION | 1.0.0 | Application version |
| APP_DESCRIPTION | AI-powered demo booking... | Application description |

### 3. Server Settings

| Setting | Default | Description |
|---------|---------|-------------|
| HOST | 0.0.0.0 | Server host |
| PORT | 8000 | Server port |
| WORKERS | 1 (dev) / 4 (prod) | Worker processes |
| RELOAD | True (dev) | Auto-reload on changes |

**Usage:**
```bash
# Development
uvicorn app.main:app --host localhost --port 8000 --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Database Settings

| Setting | Default | Description |
|---------|---------|-------------|
| DATABASE_URL | sqlite:///./construction_ai.db | Database connection URL |
| DATABASE_ECHO | True (dev) | Log SQL queries |
| DATABASE_POOL_SIZE | 5 | Connection pool size |
| DATABASE_MAX_OVERFLOW | 10 | Connection pool overflow |
| DATABASE_POOL_RECYCLE | 3600 | Connection recycle time (sec) |
| DATABASE_POOL_PRE_PING | True | Test connections before use |

**Database URL Examples:**

**SQLite (Development):**
```
sqlite:///./construction_ai.db
```

**PostgreSQL (Production):**
```
postgresql://user:password@localhost:5432/construction_ai
```

**MySQL:**
```
mysql+pymysql://user:password@localhost:3306/construction_ai
```

**Usage:**
```python
from app.config import settings

db_url = settings.get_database_url()
```

### 5. Security Settings

| Setting | Default | Description |
|---------|---------|-------------|
| SECRET_KEY | your-secret-key-... | Secret key for security |
| ALGORITHM | HS256 | JWT algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | 30 | Token expiration (minutes) |

**Important:** Change SECRET_KEY in production!

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. CORS Settings

| Setting | Default | Description |
|---------|---------|-------------|
| ALLOWED_ORIGINS | localhost:3000, localhost:8000 | CORS allowed origins |
| ALLOW_CREDENTIALS | True | Allow credentials |
| ALLOW_METHODS | * | Allowed HTTP methods |
| ALLOW_HEADERS | * | Allowed headers |

**Development (.env):**
```
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000
```

**Production (.env):**
```
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

**Production note:** Do not use `*` for origins/hosts. When `ENVIRONMENT=production`, the app will reject wildcard (`*`) and empty allowlists at startup.

This project also supports `CORS_ORIGINS` as an alias for `ALLOWED_ORIGINS`.

**Usage:**
```python
from app.config import settings

cors_config = settings.get_cors_config()
```

### 7. Trusted Host Settings

| Setting | Default | Description |
|---------|---------|-------------|
| TRUSTED_HOSTS | localhost, 127.0.0.1 | Trusted hosts |

**Production (.env):**
```
TRUSTED_HOSTS=your-domain.com,www.your-domain.com
```

This project also supports `ALLOWED_HOSTS` as an alias for `TRUSTED_HOSTS`.

### 8. Logging Settings

| Setting | Default | Description |
|---------|---------|-------------|
| LOG_LEVEL | INFO (prod) / DEBUG (dev) | Logging level |
| LOG_FILE | app.log | Log file path |
| LOG_FORMAT | Standard format | Log message format |

**Log Levels:**
- DEBUG: Detailed information
- INFO: General information
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

### 9. Email Settings

| Setting | Default | Description |
|---------|---------|-------------|
| SMTP_USER | your-email@gmail.com | Email sender address |
| SMTP_PASSWORD | your-app-password | Email password |
| SMTP_HOST | smtp.gmail.com | SMTP server host |
| SMTP_PORT | 587 | SMTP server port |
| SMTP_TLS | True | Use TLS |
| SENDER_NAME | Construction AI | Sender name |
| SENDER_EMAIL | (same as SMTP_USER) | Sender email |

**Gmail Setup:**

1. Enable 2-factor authentication
2. Generate app password: https://myaccount.google.com/apppasswords
3. Set environment variables:

```bash
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=True
```

**SendGrid Setup:**

```bash
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_TLS=True
```

**AWS SES Setup:**

```bash
SMTP_USER=your-aws-access-key
SMTP_PASSWORD=your-aws-secret-key
SMTP_HOST=email-smtp.region.amazonaws.com
SMTP_PORT=587
SMTP_TLS=True
```

**Usage:**
```python
from app.config import settings

email_config = settings.get_email_config()
```

### 10. File Upload Settings

| Setting | Default | Description |
|---------|---------|-------------|
| MAX_UPLOAD_SIZE | 10MB | Maximum file upload size |
| UPLOAD_DIR | app/uploads | Upload directory |

### 11. Timezone Settings

| Setting | Default | Description |
|---------|---------|-------------|
| TIMEZONE | America/New_York | Application timezone |

**Common Timezones:**
- America/New_York (EST)
- America/Chicago (CST)
- America/Denver (MST)
- America/Los_Angeles (PST)
- Europe/London (GMT)
- Europe/Paris (CET)
- Asia/Tokyo (JST)
- Australia/Sydney (AEDT)

### 12. Demo Booking Settings

| Setting | Default | Description |
|---------|---------|-------------|
| DEMO_DURATION_MINUTES | 30 | Demo slot duration |
| BUSINESS_HOURS_START | 9 | Business hours start (hour) |
| BUSINESS_HOURS_END | 17 | Business hours end (hour) |
| AVAILABLE_DAYS_AHEAD | 14 | Days to show slots |
| DEMO_TIMEZONE | (same as TIMEZONE) | Demo scheduling timezone |

**Usage:**
```python
from app.config import settings

booking_config = settings.get_booking_config()
```

### 13. ROI Calculator Settings

| Setting | Default | Description |
|---------|---------|-------------|
| DELAY_COST_PER_DAY | 45662 | Cost per day of delay ($) |
| AI_SOLUTION_ANNUAL_COST | 5000 | Annual AI solution cost ($) |
| ROI_REDUCTION_PERCENTAGE | 65 | Estimated delay reduction (%) |

**Usage:**
```python
from app.config import settings

roi_config = settings.get_roi_config()
```

### 14. Pagination Settings

| Setting | Default | Description |
|---------|---------|-------------|
| DEFAULT_PAGE_SIZE | 10 | Default items per page |
| MAX_PAGE_SIZE | 100 | Maximum items per page |

### 15. Cache Settings

| Setting | Default | Description |
|---------|---------|-------------|
| CACHE_ENABLED | True (prod) / False (dev) | Enable caching |
| CACHE_TTL | 300 | Cache time-to-live (seconds) |

### 16. Rate Limiting Settings

| Setting | Default | Description |
|---------|---------|-------------|
| RATE_LIMIT_ENABLED | True (prod) / False (dev) | Enable rate limiting |
| RATE_LIMIT_REQUESTS | 100 | Requests per window |
| RATE_LIMIT_WINDOW | 60 | Window duration (seconds) |

### 17. Validation Settings

| Setting | Default | Description |
|---------|---------|-------------|
| MIN_PASSWORD_LENGTH | 8 | Minimum password length |
| MAX_PASSWORD_LENGTH | 128 | Maximum password length |

### 18. Feature Flags

| Setting | Default | Description |
|---------|---------|-------------|
| FEATURE_EMAIL_ENABLED | True | Enable email functionality |
| FEATURE_BOOKING_ENABLED | True | Enable demo booking |
| FEATURE_ROI_CALCULATOR_ENABLED | True | Enable ROI calculator |
| FEATURE_CONTACT_FORM_ENABLED | True | Enable contact form |

**Usage:**
```python
from app.config import settings

if settings.FEATURE_EMAIL_ENABLED:
    # Send emails
    pass
```

---

## Environment Files

### .env.example

Create a template file for developers:

```bash
# Environment
ENVIRONMENT=development
DEBUG=True

# Database
DATABASE_URL=sqlite:///./construction_ai.db

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Email
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Booking
DEMO_DURATION_MINUTES=30
BUSINESS_HOURS_START=9
BUSINESS_HOURS_END=17

# ROI Calculator
DELAY_COST_PER_DAY=45662
AI_SOLUTION_ANNUAL_COST=5000
ROI_REDUCTION_PERCENTAGE=65
```

### .env (Development)

```bash
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=sqlite:///./construction_ai.db
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### .env (Production)

```bash
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://user:password@db.example.com:5432/construction_ai
SECRET_KEY=your-generated-secret-key
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
TRUSTED_HOSTS=your-domain.com,www.your-domain.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
RATE_LIMIT_ENABLED=True
CACHE_ENABLED=True
```

---

## Usage Examples

### In FastAPI Routes

```python
from app.config import settings

@app.get("/api/info")
async def get_info():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }
```

### In Database Setup

```python
from app.config import settings
from sqlalchemy import create_engine

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    pool_pre_ping=settings.DATABASE_POOL_PRE_PING
)
```

### In Email Configuration

```python
from app.config import settings

email_config = settings.get_email_config()

# Use in email service
smtp_user = email_config["smtp_user"]
smtp_password = email_config["smtp_password"]
```

### In Booking Configuration

```python
from app.config import settings

booking_config = settings.get_booking_config()

# Use in booking service
demo_duration = booking_config["demo_duration_minutes"]
business_hours_start = booking_config["business_hours_start"]
```

### In ROI Configuration

```python
from app.config import settings

roi_config = settings.get_roi_config()

# Use in ROI calculator
delay_cost = roi_config["delay_cost_per_day"]
ai_cost = roi_config["ai_solution_annual_cost"]
```

### Environment Checks

```python
from app.config import settings

if settings.is_production():
    # Production-specific code
    pass

if settings.is_development():
    # Development-specific code
    pass
```

---

## Helper Functions

### get_env_bool(key, default)
Get boolean environment variable.

```python
DEBUG = get_env_bool("DEBUG", False)
```

### get_env_list(key, default)
Get list environment variable (comma-separated).

```python
ORIGINS = get_env_list("ALLOWED_ORIGINS", "localhost")
```

### get_env_int(key, default)
Get integer environment variable.

```python
PORT = get_env_int("PORT", 8000)
```

---

## Settings Methods

### get_database_url()
Get database connection URL.

```python
db_url = settings.get_database_url()
```

### get_cors_config()
Get CORS configuration dictionary.

```python
cors_config = settings.get_cors_config()
```

### get_email_config()
Get email configuration dictionary.

```python
email_config = settings.get_email_config()
```

### get_booking_config()
Get booking configuration dictionary.

```python
booking_config = settings.get_booking_config()
```

### get_roi_config()
Get ROI calculator configuration dictionary.

```python
roi_config = settings.get_roi_config()
```

### is_production()
Check if running in production.

```python
if settings.is_production():
    # Production code
    pass
```

### is_development()
Check if running in development.

```python
if settings.is_development():
    # Development code
    pass
```

---

## File Placement

```
app/
├── __init__.py
├── config.py                    # ← This file
├── main.py
├── database.py
├── models/
├── routes/
├── schemas/
├── utils/
├── templates/
└── static/
```

---

## Validation

The Settings class validates critical settings:

```python
def _validate_settings(self):
    """Validate critical settings."""
    # Validate database URL
    if not self.DATABASE_URL:
        raise ValueError("DATABASE_URL must be set")
    
    # Validate SMTP settings if email is enabled
    if self.FEATURE_EMAIL_ENABLED:
        if not self.SMTP_USER or not self.SMTP_PASSWORD:
            raise ValueError("SMTP_USER and SMTP_PASSWORD must be set")
    
    # Validate timezone
    try:
        import zoneinfo
        zoneinfo.ZoneInfo(self.TIMEZONE)
    except Exception as e:
        raise ValueError(f"Invalid timezone: {self.TIMEZONE}")
```

---

## Loading Order

Settings are loaded in this order (first match wins):

1. Environment variables (.env file)
2. Default values in Settings class
3. Hardcoded defaults

---

## Summary

The `app/config.py` file provides:

✅ **Centralized configuration** - All settings in one place
✅ **Environment variables** - Override via .env file
✅ **Multiple environments** - Development, staging, production
✅ **Sensible defaults** - Works out of the box
✅ **Type safety** - Proper type hints
✅ **Validation** - Critical settings validated
✅ **Helper methods** - Easy access to config groups
✅ **Singleton pattern** - Only one instance created
✅ **LRU cache** - Efficient access
✅ **Well-documented** - Comprehensive docstrings
✅ **Production-ready** - Secure defaults

Everything is production-ready and fully documented!
