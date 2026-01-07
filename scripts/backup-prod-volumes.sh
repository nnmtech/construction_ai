#!/usr/bin/env sh
set -eu

# Backup the production compose named volumes (raw data) for full restore.
#
# Defaults match docker-compose.prod.yml when run with project name:
#   construction_ai_landing_prod
#
# Usage:
#   ./scripts/backup-prod-volumes.sh
#
# Env overrides:
#   PROJECT=construction_ai_landing_prod
#   OUT_DIR=./backups/volumes

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PROJECT="${PROJECT:-construction_ai_landing_prod}"
OUT_DIR="${OUT_DIR:-$ROOT_DIR/backups/volumes}"

mkdir -p "$OUT_DIR"

backup_one() {
  logical="$1"
  vol="${PROJECT}_${logical}"
  if docker volume inspect "$vol" >/dev/null 2>&1; then
    "$ROOT_DIR/scripts/docker-volume-backup.sh" "$vol" "$OUT_DIR"
  else
    echo >&2 "[backup-vols] WARN: volume not found (skipping): $vol"
  fi
}

if ! command -v docker >/dev/null 2>&1; then
  echo >&2 "[backup-vols] docker not found; skipping"
  exit 0
fi

backup_one postgres_data
backup_one letsencrypt
backup_one app_data

echo "[backup-vols] Complete"
