import os

# Bind to 0.0.0.0 by default for containers
HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", os.getenv("APP_PORT", "8000"))
bind = f"{HOST}:{PORT}"

# Worker settings
# NOTE: When using SQLite and AUTO_CREATE_SCHEMA=true, multiple Gunicorn workers may
# concurrently attempt DDL at startup (create_all), which can trip SQLite's locking.
# To keep `docker run`/fresh-start behavior reliable, force a single worker in that
# specific configuration.
_database_url = os.getenv("DATABASE_URL", "").strip().lower()
_auto_create_schema = os.getenv("AUTO_CREATE_SCHEMA", "").strip().lower() in {"1", "true", "yes", "on"}

_default_workers = os.getenv("WEB_CONCURRENCY", os.getenv("WORKERS", "2"))
workers = int(_default_workers)
if _auto_create_schema and _database_url.startswith("sqlite"):
	workers = 1
worker_class = os.getenv("WORKER_CLASS", "uvicorn.workers.UvicornWorker")

# Timeouts
timeout = int(os.getenv("TIMEOUT", "60"))
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.getenv("KEEPALIVE", "5"))

# Logging
loglevel = os.getenv("LOG_LEVEL", "info").lower()
accesslog = os.getenv("ACCESS_LOG", "-")  # '-' => stdout
errorlog = os.getenv("ERROR_LOG", "-")    # '-' => stderr

# If running behind a proxy/load balancer, trust X-Forwarded-* headers
#
# IMPORTANT: Default to fail-closed. Only trust proxy headers when explicitly enabled
# via TRUST_PROXY_HEADERS=true, or when FORWARDED_ALLOW_IPS is explicitly provided.
_trust_proxy_headers = os.getenv("TRUST_PROXY_HEADERS", "").strip().lower() in {"1", "true", "yes", "on"}

_forwarded_allow_ips_env = os.getenv("FORWARDED_ALLOW_IPS")
if _forwarded_allow_ips_env is not None and _forwarded_allow_ips_env.strip() != "":
	forwarded_allow_ips = _forwarded_allow_ips_env.strip()
else:
	forwarded_allow_ips = "*" if _trust_proxy_headers else "127.0.0.1"

proxy_allow_ips = forwarded_allow_ips

# Preload improves memory sharing, but can complicate startup side-effects
preload_app = os.getenv("PRELOAD_APP", "false").lower() in {"1", "true", "yes", "on"}
