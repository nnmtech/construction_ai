# Construction AI Landing Page - Quick Start Guide

## Overview

This guide will help you set up and run the Construction AI landing page application locally in minutes.

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13 (recommended/tested)** - [Download](https://www.python.org/downloads/)
- **pip** - Python package manager (comes with Python)
- **Git** - [Download](https://git-scm.com/)
- **Gmail Account** - For email functionality (optional for development)

Verify installation:
```bash
python --version
pip --version
git --version
```

---

## Step 1: Clone or Extract Project

```bash
# If using Git
git clone <repository-url>
cd construction_ai_landing

# Or extract the provided files to a directory
cd construction_ai_landing
```

---

## Step 2: Create Virtual Environment

A virtual environment isolates project dependencies from your system Python.

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

You should see `(.venv)` prefix in your terminal.

---

## Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies (prefer the lockfile if present)
pip install -r requirements.lock || pip install -r requirements.txt
```

This installs all required packages including FastAPI, SQLAlchemy, Pydantic, and more.

---

## Step 4: Configure Environment Variables

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env with your settings
# On Windows:
notepad .env

# On macOS/Linux:
nano .env
```

### Minimal Configuration (Development)

For local development, you only need to set:

```env
DATABASE_URL=sqlite:///./contractors.db
DEBUG=True
SECRET_KEY=your-secret-key-12345
```

### Email Configuration (Optional)

To enable email functionality, configure Gmail:

1. **Enable 2-Factor Authentication:**
   - Go to [myaccount.google.com/security](https://myaccount.google.com/security)
   - Enable 2-Step Verification

2. **Generate App Password:**
   - Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Windows Computer"
   - Copy the 16-character password

3. **Update .env:**
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx
   FROM_EMAIL=noreply@constructionai.com
   ```

---

## Step 5: Initialize Database

This project uses Alembic migrations as the source of truth.

```bash
# Apply migrations
alembic upgrade head
```

If you are doing quick local prototyping/tests only, you can also set `AUTO_CREATE_SCHEMA=true`
to let the app auto-create tables on startup (not recommended for production).

---

## Step 6: Run the Application

```bash
# Start the development server
uvicorn app.main:app --reload

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

The `--reload` flag automatically restarts the server when you make code changes.

---

## Step 7: Access the Application

Open your browser and navigate to:

- **Landing Page:** http://localhost:8000
- **API Documentation:** http://localhost:8000/api/docs
- **Alternative Docs:** http://localhost:8000/api/redoc
- **Health Check:** http://localhost:8000/health

---

## Testing the Application

### 1. Test Contact Form

```bash
curl -X POST http://localhost:8000/api/forms/contact \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "ABC Construction",
    "contact_name": "John Smith",
    "email": "john@example.com",
    "phone": "404-555-0123",
    "company_size": "medium",
    "annual_revenue": 5000000,
    "current_challenges": "Schedule delays and subcontractor coordination"
  }'
```

Expected response (201 Created):
```json
{
  "id": 1,
  "company_name": "ABC Construction",
  "contact_name": "John Smith",
  "email": "john@example.com",
  "phone": "404-555-0123",
  "company_size": "medium",
  "annual_revenue": 5000000,
  "current_challenges": "Schedule delays and subcontractor coordination",
  "estimated_annual_savings": null,
  "demo_scheduled": false,
  "demo_date": null,
  "created_at": "2026-01-05T10:30:00",
  "updated_at": "2026-01-05T10:30:00"
}
```

### 2. Test ROI Calculator

```bash
curl -X POST http://localhost:8000/api/roi/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "avg_project_value": 500000,
    "avg_delay_percentage": 25,
    "num_projects_per_year": 12
  }'
```

Expected response (200 OK):
```json
{
  "avg_project_value": 500000,
  "avg_delay_percentage": 25,
  "num_projects_per_year": 12,
  "cost_per_day_delay": 45662,
  "annual_delay_cost": 24656880,
  "estimated_savings_with_ai": 16026972,
  "payback_period_months": 0.004,
  "roi_percentage": 320539
}
```

### 3. Test Available Slots

```bash
curl http://localhost:8000/api/booking/available-slots
```

Expected response (200 OK):
```json
{
  "available_slots": [
    {
      "date": "2026-01-06",
      "time": "09:00",
      "datetime": "2026-01-06T09:00:00"
    },
    {
      "date": "2026-01-06",
      "time": "09:30",
      "datetime": "2026-01-06T09:30:00"
    }
    // ... more slots
  ]
}
```

### 4. Test Demo Booking

```bash
curl -X POST http://localhost:8000/api/booking/schedule-demo \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "preferred_date": "2026-01-06",
    "preferred_time": "14:00"
  }'
```

Expected response (200 OK):
```json
{
  "success": true,
  "message": "Demo scheduled successfully!",
  "demo_date": "2026-01-06T14:00:00",
  "confirmation_email_sent": true
}
```

---

## Interactive API Documentation

FastAPI provides interactive API documentation at http://localhost:8000/api/docs

You can:
- View all endpoints
- See request/response schemas
- Test endpoints directly in the browser
- View example requests and responses

---

## Project Structure

```
construction_ai_landing/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database setup
│   ├── models/
│   │   ├── __init__.py
│   │   └── contractor.py       # Database models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── contractor.py       # Pydantic schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── forms.py            # Contact form endpoints
│   │   ├── roi.py              # ROI calculator endpoints
│   │   └── booking.py          # Booking endpoints
│   ├── utils/
│   │   ├── __init__.py
│   │   └── email.py            # Email utilities
│   ├── templates/
│   │   └── index.html          # Landing page
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── .env                        # Your configuration (create from .env.example)
├── contractors.db              # SQLite database (created on first run)
└── README.md                   # Project documentation
```

---

## Common Issues & Solutions

### Issue: `ModuleNotFoundError: No module named 'fastapi'`

**Solution:** Make sure your virtual environment is activated and dependencies are installed:
```bash
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.lock || pip install -r requirements.txt
```

### Issue: `Database is locked`

**Solution:** SQLite has limitations with concurrent access. For development, this is normal. For production, use PostgreSQL:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/construction_ai
```

### Issue: Email not sending

**Solution:** Check your .env configuration:
```bash
# Test SMTP connection
python -c "
import smtplib
from app.config import settings
try:
    server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
    server.starttls()
    server.login(settings.smtp_user, settings.smtp_password)
    print('SMTP connection successful!')
    server.quit()
except Exception as e:
    print(f'SMTP error: {e}')
"
```

### Issue: Port 8000 already in use

**Solution:** Use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

### Issue: CORS errors in browser

**Solution:** CORS is already configured to allow all origins in development. If issues persist, check browser console for specific errors.

---

## Development Workflow

### Making Code Changes

1. Edit files in the `app/` directory
2. The server automatically reloads (with `--reload` flag)
3. Refresh your browser to see changes

### Database Changes

If you modify models:

1. Create a migration:
  ```bash
  alembic revision --autogenerate -m "update schema"
  ```

2. Apply it:
  ```bash
  alembic upgrade head
  ```

### Adding New Endpoints

1. Create a new route file in `app/routes/`
2. Define your endpoints
3. Include the router in `app/main.py`:
   ```python
   from app.routes import your_new_route
   app.include_router(your_new_route.router)
   ```

---

## Production Deployment

### Using Gunicorn

```bash
# Run with Gunicorn (recommended: use the included config)
gunicorn -c gunicorn.conf.py app.main:app
```

Note: if you run SQLite with `AUTO_CREATE_SCHEMA=true`, multiple Gunicorn workers may contend
on DDL at startup. The included Gunicorn config automatically forces a single worker in that
specific case.

### Using Docker

```bash
# Build image
docker build -t construction-ai:local .

# Run container
docker run --rm -p 8010:8000 \
  -v "$PWD/.data:/data" \
  -e DATABASE_URL=sqlite:////data/contractors.db \
  -e ALLOWED_HOSTS='example.com,www.example.com' \
  -e CORS_ORIGINS='https://example.com,https://www.example.com' \
  construction-ai:local

# Verify it started (first boot can briefly reset connections; retries handle that)
curl -fsS --retry 20 --retry-all-errors --retry-delay 1 http://127.0.0.1:8010/health && echo

# If you need to initialize the DB via migrations for a fresh volume
docker run --rm \
  -v "$PWD/.data:/data" \
  -e DATABASE_URL=sqlite:////data/contractors.db \
  construction-ai:local alembic upgrade head

# Or enable auto-migrations at container startup
docker run --rm -p 8010:8000 \
  -v "$PWD/.data:/data" \
  -e DATABASE_URL=sqlite:////data/contractors.db \
  -e RUN_MIGRATIONS_ON_STARTUP=true \
  construction-ai:local
```

If port `8000` is already in use on your machine, map a different host port (like `8010:8000`).

### Using FastMCP Cloud

```bash
# Deploy
fastmcp deploy --name construction-ai-landing

# Set environment variables
fastmcp env set SMTP_USER your-email@gmail.com
fastmcp env set SMTP_PASSWORD your-app-password
fastmcp env set DATABASE_URL postgresql://...
```

---

## Next Steps

1. **Customize the landing page:** Edit `app/templates/index.html` and `app/static/css/style.css`
2. **Add more fields:** Modify schemas in `app/schemas/contractor.py`
3. **Integrate with CRM:** Add API calls to your CRM system
4. **Set up analytics:** Add Google Analytics or Mixpanel tracking
5. **Deploy to production:** Use Docker, Heroku, Railway, or FastMCP Cloud

---

## Useful Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.lock || pip install -r requirements.txt

# Initialize database
alembic upgrade head

# (Dev/tests only) Auto-create schema on startup
# export AUTO_CREATE_SCHEMA=true

# Run development server
uvicorn app.main:app --reload

# Run production server (recommended: use the included Gunicorn config)
gunicorn -c gunicorn.conf.py app.main:app

# Docker build & run
docker build -t construction-ai:local .
docker run --rm -p 8010:8000 \
  -e DATABASE_URL=sqlite:////data/contractors.db \
  -e ALLOWED_HOSTS='example.com,www.example.com' \
  -e CORS_ORIGINS='https://example.com,https://www.example.com' \
  -v "$PWD/.data:/data" \
  construction-ai:local

# Health check with retries (handles first-boot connection resets)
curl -fsS --retry 20 --retry-all-errors --retry-delay 1 http://127.0.0.1:8010/health && echo

# Docker Compose
# (Compose enables RUN_MIGRATIONS_ON_STARTUP=true by default in docker-compose.yml)
docker compose up --build

# Format code
black app/

# Check code style
flake8 app/

# Type checking
mypy app/

# Run tests
python -m pytest

# Regenerate the lockfile (requires pip-tools)
pip install -U pip-tools
pip-compile --output-file requirements.lock requirements.txt

# Deactivate virtual environment
deactivate
```

---

## Getting Help

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### Troubleshooting
- Check logs in terminal where server is running
- Use browser DevTools to check network requests
- Test endpoints with curl or Postman

### Support
- Review error messages carefully
- Check `.env` configuration
- Verify database connection
- Test SMTP settings separately

---

## Summary

You now have a fully functional Construction AI landing page with:

✅ Contact form with email capture
✅ ROI calculator with financial analysis
✅ Demo booking system with time slots
✅ Professional landing page UI
✅ Complete API documentation
✅ Production-ready code

Start the server and begin capturing contractor leads!

```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000 to see your application live.
