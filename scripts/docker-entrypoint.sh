#!/usr/bin/env sh
set -eu

# Optional: run Alembic migrations at container startup.
# For production with multiple replicas, you may prefer running migrations as a separate job.
RUN_MIGRATIONS_ON_STARTUP="${RUN_MIGRATIONS_ON_STARTUP:-false}"

if [ "$RUN_MIGRATIONS_ON_STARTUP" = "true" ] || [ "$RUN_MIGRATIONS_ON_STARTUP" = "1" ] || [ "$RUN_MIGRATIONS_ON_STARTUP" = "yes" ] || [ "$RUN_MIGRATIONS_ON_STARTUP" = "on" ]; then
  echo "[entrypoint] Running migrations: alembic upgrade head"
  alembic upgrade head
else
  echo "[entrypoint] Skipping migrations (set RUN_MIGRATIONS_ON_STARTUP=true to enable)"
fi

exec "$@"
