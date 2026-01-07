#!/usr/bin/env sh
set -eu

# Runs the Postgres backup only at 03:00 America/New_York (US/Eastern), once per day.
# Intended to be called by systemd on an hourly timer.

NOW="$(TZ=America/New_York date +%H:%M)"
if [ "$NOW" != "03:00" ]; then
  exit 0
fi

STAMP_DIR=/var/lib/construction-ai
mkdir -p "$STAMP_DIR"

DAY="$(TZ=America/New_York date +%F)"
STAMP="$STAMP_DIR/postgres-backup-$DAY.done"

if [ -f "$STAMP" ]; then
  exit 0
fi

/usr/bin/env sh /opt/construction_ai_landing/scripts/postgres-backup.sh

touch "$STAMP"
