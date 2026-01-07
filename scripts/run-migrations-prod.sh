#!/usr/bin/env sh
set -eu

# Run Alembic migrations as an explicit, one-off job for the production stack.
#
# Usage:
#   ./scripts/run-migrations-prod.sh

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env.prod}"
PROJECT="${PROJECT:-construction_ai_landing_prod}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/docker-compose.prod.yml}"

echo "[migrations] Running: alembic upgrade head"
docker compose -p "$PROJECT" -f "$COMPOSE_FILE" --env-file "$ENV_FILE" run --rm \
  -e RUN_MIGRATIONS_ON_STARTUP=true \
  app alembic upgrade head
