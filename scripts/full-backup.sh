#!/usr/bin/env sh
set -eu

# Full-restore backup.
# - Includes the whole repo contents (including .venv/caches/logs if present)
# - Excludes nested tarballs to avoid huge recursive archives
# - Optionally runs a fresh Postgres dump first (best-effort)
#
# Usage:
#   ./scripts/full-backup.sh
#
# Env overrides:
#   OUT_DIR=./backups/full
#   RUN_DB_DUMP=true|false
#   ENV_FILE=.env.prod

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUT_DIR="${OUT_DIR:-$ROOT_DIR/backups/full}"
RUN_DB_DUMP="${RUN_DB_DUMP:-true}"
RUN_VOLUME_BACKUP="${RUN_VOLUME_BACKUP:-true}"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env.prod}"

mkdir -p "$OUT_DIR"

stamp=$(date -u +%Y%m%dT%H%M%SZ)
out="$OUT_DIR/Construction_AI_full_${stamp}.tar.gz"

if [ "$RUN_DB_DUMP" = "true" ]; then
  if command -v docker >/dev/null 2>&1; then
    echo "[full-backup] Running Postgres dump (best-effort)"
    # If compose isn't up, this will fail; we don't block the full backup.
    ENV_FILE="$ENV_FILE" "$ROOT_DIR/scripts/postgres-backup.sh" || echo >&2 "[full-backup] WARN: Postgres dump failed; continuing"
  else
    echo >&2 "[full-backup] WARN: docker not found; skipping Postgres dump"
  fi
fi

if [ "$RUN_VOLUME_BACKUP" = "true" ]; then
  if command -v docker >/dev/null 2>&1; then
    echo "[full-backup] Running raw volume backups (best-effort)"
    "$ROOT_DIR/scripts/backup-prod-volumes.sh" || echo >&2 "[full-backup] WARN: volume backup failed; continuing"
  else
    echo >&2 "[full-backup] WARN: docker not found; skipping volume backup"
  fi
fi

echo "[full-backup] Writing $out"

# Avoid including this archive or other tarballs inside backups.
# Keep .sql.gz dumps (Postgres logical backups).
(
  cd "$ROOT_DIR"
  tar -czf "$out" \
    --exclude='./backups/full' \
    .
)

sha256sum "$out" | tee "${out}.sha256"
echo "[full-backup] Done"
