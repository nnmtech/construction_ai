FROM python:3.13-slim

# System deps (minimal)
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first for better layer caching
COPY requirements.lock requirements.txt ./
RUN pip install --no-cache-dir -U pip \
  && pip install --no-cache-dir -r requirements.lock

# Copy app source
COPY . .

RUN chmod +x /app/scripts/docker-entrypoint.sh

# Sensible container defaults (override via env)
ENV HOST=0.0.0.0 \
    PORT=8000 \
    LOG_FORMAT=json \
    ENVIRONMENT=production \
    DEBUG=false

EXPOSE 8000

# Optional container healthcheck (hits /health)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:${PORT}/health || exit 1

ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
