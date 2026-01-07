#!/usr/bin/env sh
set -eu

# Backup a Docker named volume to a tar.gz archive.
#
# Usage:
#   ./scripts/docker-volume-backup.sh <volume_name> [output_dir]

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
  echo >&2 "Usage: $0 <volume_name> [output_dir]"
  exit 2
fi

VOLUME_NAME="$1"
OUT_DIR="${2:-}"

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUT_DIR="${OUT_DIR:-$ROOT_DIR/backups/volumes}"

mkdir -p "$OUT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo >&2 "[vol-backup] docker not found"
  exit 1
fi

if ! docker volume inspect "$VOLUME_NAME" >/dev/null 2>&1; then
  echo >&2 "[vol-backup] Volume not found: $VOLUME_NAME"
  exit 1
fi

stamp=$(date -u +%Y%m%dT%H%M%SZ)
archive="$OUT_DIR/${VOLUME_NAME}_${stamp}.tar.gz"

echo "[vol-backup] Backing up volume $VOLUME_NAME -> $archive"

docker run --rm \
  -v "$VOLUME_NAME":/volume:ro \
  -v "$OUT_DIR":/backup \
  alpine:3.20 \
  sh -ec "cd /volume && tar -czf /backup/$(basename -- \"$archive\") ."

sha256sum "$archive" | tee "${archive}.sha256" >/dev/null

echo "[vol-backup] Done"
