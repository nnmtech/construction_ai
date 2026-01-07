#!/usr/bin/env sh
set -eu

# Restore a Docker named volume from a tar.gz archive.
#
# WARNING: This will DELETE current contents of the volume.
# Stop any containers using the volume before restoring.
#
# Usage:
#   ./scripts/docker-volume-restore.sh <volume_name> <archive_path>

if [ $# -ne 2 ]; then
  echo >&2 "Usage: $0 <volume_name> <archive_path>"
  exit 2
fi

VOLUME_NAME="$1"
ARCHIVE_PATH="$2"

if ! command -v docker >/dev/null 2>&1; then
  echo >&2 "[vol-restore] docker not found"
  exit 1
fi

if [ ! -f "$ARCHIVE_PATH" ]; then
  echo >&2 "[vol-restore] Archive not found: $ARCHIVE_PATH"
  exit 1
fi

if ! docker volume inspect "$VOLUME_NAME" >/dev/null 2>&1; then
  echo >&2 "[vol-restore] Volume not found: $VOLUME_NAME"
  exit 1
fi

ARCHIVE_DIR=$(CDPATH= cd -- "$(dirname -- "$ARCHIVE_PATH")" && pwd)
ARCHIVE_BASE=$(basename -- "$ARCHIVE_PATH")

echo "[vol-restore] Restoring $ARCHIVE_PATH -> volume $VOLUME_NAME"

docker run --rm \
  -v "$VOLUME_NAME":/volume \
  -v "$ARCHIVE_DIR":/backup:ro \
  alpine:3.20 \
  sh -ec "find /volume -mindepth 1 -maxdepth 1 -exec rm -rf {} +; tar -xzf /backup/\"$ARCHIVE_BASE\" -C /volume"

echo "[vol-restore] Done"
