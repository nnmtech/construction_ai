# systemd templates

These templates schedule Postgres backups by running [scripts/postgres-backup.sh](../../scripts/postgres-backup.sh).

## Install (server)
Assumptions:
- Repo is deployed at `/opt/construction_ai_landing` (adjust paths if different)
- Production env file is `/opt/construction_ai_landing/.env.prod`
- Docker is installed and running

1) Create an on-host backup directory (recommended outside the repo):
- `sudo mkdir -p /opt/construction_ai_backups/postgres`
- `sudo chmod 700 /opt/construction_ai_backups/postgres`

2) Copy unit files:
- `sudo cp /opt/construction_ai_landing/deploy/systemd/construction-ai-postgres-backup.service /etc/systemd/system/`
- `sudo cp /opt/construction_ai_landing/deploy/systemd/construction-ai-postgres-backup.timer /etc/systemd/system/`

3) Optional: configure overrides
- `sudo cp /opt/construction_ai_landing/deploy/systemd/postgres-backup.env.example \
  /opt/construction_ai_landing/deploy/systemd/postgres-backup.env`
- Edit `BACKUP_DIR`, `KEEP_DAYS`, and `PROJECT` as needed.

4) Enable timer:
- `sudo systemctl daemon-reload`
- `sudo systemctl enable --now construction-ai-postgres-backup.timer`

## Verify
- `systemctl list-timers --all | grep construction-ai-postgres-backup`
- Run once immediately:
  - `sudo systemctl start construction-ai-postgres-backup.service`
- Inspect logs:
  - `journalctl -u construction-ai-postgres-backup.service -n 200 --no-pager`

## Notes
- The timer triggers **hourly**, but the service only performs the backup when the time in `America/New_York` is exactly **03:00**.
- This avoids depending on the server's local timezone and works even on older systemd builds that don't support `Timezone=` in timers.
- The service runs as root by default (system unit). If you prefer running as a non-root user, add `User=...` and ensure that user can run Docker (usually by being in the `docker` group).
- Backups created are plain SQL dumps compressed with gzip. You should copy them off-host (S3/rsync/etc.) as part of your ops process.
