#!/usr/bin/env sh
set -eu

# Simple Postgres backup (pg_dump) for the production compose stack.
#
# Usage:
#   ./scripts/postgres-backup.sh
#
# Env overrides:
#   ENV_FILE=.env.prod
#   BACKUP_DIR=./backups/postgres
#   KEEP_DAYS=14
#   PROJECT=construction_ai_landing_prod

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env.prod}"
BACKUP_DIR="${BACKUP_DIR:-$ROOT_DIR/backups/postgres}"
KEEP_DAYS="${KEEP_DAYS:-14}"
PROJECT="${PROJECT:-construction_ai_landing_prod}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/docker-compose.prod.yml}"
POST_BACKUP_HOOK="${POST_BACKUP_HOOK:-$ROOT_DIR/scripts/post-backup-hook.sh}"

if [ ! -f "$ENV_FILE" ]; then
  echo >&2 "[pg-backup] Missing env file: $ENV_FILE"
  exit 1
fi

# shellcheck disable=SC1090
. "$ENV_FILE"

: "${POSTGRES_DB:?POSTGRES_DB must be set}"
: "${POSTGRES_USER:?POSTGRES_USER must be set}"

mkdir -p "$BACKUP_DIR"

stamp=$(date -u +%Y%m%dT%H%M%SZ)
out="$BACKUP_DIR/${POSTGRES_DB}_${stamp}.sql.gz"

echo "[pg-backup] Writing $out"

docker compose -p "$PROJECT" -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T db \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-privileges \
  | gzip -c > "$out"

echo "[pg-backup] Pruning backups older than $KEEP_DAYS days"
find "$BACKUP_DIR" -type f -name "${POSTGRES_DB}_*.sql.gz" -mtime "+$KEEP_DAYS" -print -delete || true

if [ -f "$POST_BACKUP_HOOK" ]; then
  if [ -x "$POST_BACKUP_HOOK" ]; then
    echo "[pg-backup] Running post-backup hook: $POST_BACKUP_HOOK"
    BACKUP_FILE="$out" \
    BACKUP_DIR="$BACKUP_DIR" \
    POSTGRES_DB="$POSTGRES_DB" \
    POSTGRES_USER="$POSTGRES_USER" \
      "$POST_BACKUP_HOOK"
  else
    echo >&2 "[pg-backup] WARN: post-backup hook exists but is not executable: $POST_BACKUP_HOOK"
  fi
fi

echo "[pg-backup] Done"
