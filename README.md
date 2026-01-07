# Construction AI Landing Page

A production-ready FastAPI application for a construction AI service landing page with booking, ROI calculator, contractor management, and authentication.

## Features

- **Landing Page** - Modern responsive design with service showcase
- **ROI Calculator** - Interactive calculator for construction cost savings
- **Demo Booking** - Schedule demos with available time slots
- **Contact Forms** - Lead capture with email notifications
- **Contractor Management** - CRUD operations for contractor profiles
- **User Authentication** - JWT-based auth with secure password handling
- **API Documentation** - Auto-generated OpenAPI/Swagger docs

## Tech Stack

- **Backend**: FastAPI + Gunicorn with Uvicorn workers
- **Database**: PostgreSQL (production) / SQLite (development)
- **Migrations**: Alembic
- **Reverse Proxy**: Traefik v2.11 with automatic HTTPS (Let's Encrypt)
- **Deployment**: Docker + Docker Compose
- **Security**: Rate limiting, CORS, trusted hosts, HSTS, Docker socket proxy

## Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- Docker and Docker Compose (for production deployment)

### Setup

1. **Clone the repository**
```bash
git clone git@github.com:nnmtech/construction_ai.git
cd construction_ai
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
alembic upgrade head
```

6. **Run verification**
```bash
python verify_setup.py
```

7. **Start development server**
```bash
uvicorn app.main:app --reload
```

Visit:
- Application: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Alternative API Docs: http://localhost:8000/redoc

## Production Deployment

Full production deployment guide: [deploy/PRODUCTION.md](deploy/PRODUCTION.md)

### Architecture

**Recommended topology**: nginx/LB owns external ports 80/443 and forwards to Traefik on internal ports 9080/9443.

```
Internet (80/443)
    ↓
nginx/LB (TLS passthrough for 443, HTTP forward for 80)
    ↓
Traefik (9080/9443 - terminates TLS, handles ACME)
    ↓
FastAPI app (8000)
    ↓
PostgreSQL (5432)
```

### Quick Production Setup

1. **Prepare server**
```bash
# Deploy repo to /opt/construction_ai_landing
git clone git@github.com:nnmtech/construction_ai.git /opt/construction_ai_landing
cd /opt/construction_ai_landing
```

2. **Configure secrets**
```bash
cp .env.prod.example .env.prod
# Edit .env.prod - replace ALL placeholder values
nano .env.prod
```

3. **Run preflight checks**
```bash
./scripts/prod-preflight.sh
```

4. **Run migrations**
```bash
./scripts/run-migrations-prod.sh
```

5. **Start production stack**
```bash
docker compose -f docker-compose.prod.yml up -d
```

6. **Set up nginx forwarding**
See [deploy/nginx/README.md](deploy/nginx/README.md)

7. **Set up automated backups**
See [deploy/systemd/README.md](deploy/systemd/README.md)

## Project Structure

```
.
├── app/                      # Application code
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # API route handlers
│   ├── schemas/             # Pydantic schemas
│   ├── utils/               # Utilities (email, etc.)
│   ├── static/              # Static assets (CSS, JS)
│   └── templates/           # Jinja2 templates
├── alembic/                 # Database migrations
├── scripts/                 # Operational scripts
│   ├── prod-preflight.sh    # Production checks
│   ├── postgres-backup.sh   # Database backup
│   ├── full-backup.sh       # Full system backup
│   └── run-migrations-prod.sh
├── deploy/                  # Deployment resources
│   ├── PRODUCTION.md        # Production guide
│   ├── GITHUB.md            # GitHub setup
│   ├── nginx/               # Nginx templates
│   └── systemd/             # Systemd timer/service
├── docker-compose.yml       # Local development stack
├── docker-compose.prod.yml  # Production stack
├── Dockerfile               # Application container
├── requirements.txt         # Python dependencies
├── requirements.lock        # Locked dependencies
└── gunicorn.conf.py         # Gunicorn config
```

## Configuration

### Environment Variables

Key variables (see `.env.example` and `.env.prod.example` for complete list):

- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT signing key (must be random in production)
- `DEBUG` - Enable debug mode (false in production)
- `DOMAIN` - Your domain name
- `TRAEFIK_ACME_EMAIL` - Email for Let's Encrypt
- `POSTGRES_PASSWORD` - Database password
- `SMTP_*` - Email configuration (if using email features)

### Security Settings

- `TRUSTED_HOSTS` - Comma-separated list of allowed hosts
- `CORS_ORIGINS` - Allowed CORS origins
- `HTTPS_REDIRECT` - Force HTTPS (true in production)
- `TRUST_PROXY_HEADERS` - Trust X-Forwarded-* headers
- `FORWARDED_ALLOW_IPS` - IPs allowed to set forwarded headers

## Backups

### Postgres Backups
```bash
# One-time backup
./scripts/postgres-backup.sh

# Automated (scheduled at 3 AM Eastern)
# See deploy/systemd/README.md
```

### Full System Backup
```bash
# Includes source + volumes + database
./scripts/full-backup.sh
```

Backups are stored in `backups/` with SHA256 checksums.

## API Endpoints

### Public Endpoints
- `GET /` - Landing page
- `GET /booking` - Booking page
- `POST /api/forms/contact` - Submit contact form
- `POST /api/roi/calculate` - Calculate ROI
- `GET /api/booking/available-slots` - Get available booking slots
- `POST /api/booking/schedule-demo` - Schedule a demo
- `GET /health` - Health check

### Protected Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/contractors` - List contractors (requires auth)
- `POST /api/contractors` - Create contractor (requires auth)
- More in `/docs`

## Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
The project uses:
- Type hints throughout
- Pydantic for validation
- SQLAlchemy 2.x with type annotations
- Pylance strict mode (no errors)

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Troubleshooting

### Check application logs
```bash
docker compose -f docker-compose.prod.yml logs app
```

### Check Traefik logs
```bash
docker compose -f docker-compose.prod.yml logs proxy
```

### Check database connectivity
```bash
docker compose -f docker-compose.prod.yml exec db psql -U <user> -d <database>
```

### Run preflight checks
```bash
./scripts/prod-preflight.sh
```

## Documentation

- [Production Deployment Guide](deploy/PRODUCTION.md)
- [GitHub Setup Guide](deploy/GITHUB.md)
- [Nginx Configuration](deploy/nginx/README.md)
- [Systemd Backup Scheduling](deploy/systemd/README.md)

## License

Copyright © 2026. All rights reserved.

## Support

For issues and questions, please open an issue on GitHub.
