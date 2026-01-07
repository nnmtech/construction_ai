# Production checklist (required)

This repo supports a production topology where **nginx/LB owns external ports 80/443** and forwards to **Traefik on host ports 9080/9443**.

## 1) DNS + domain
- Point `DOMAIN` (A/AAAA) at your server/LB public IP.

## 2) Ports + forwarding
- External `80` must reach nginx/LB.
- External `443` must reach nginx/LB.
- nginx/LB must forward:
  - `80 -> 127.0.0.1:9080` (Traefik HTTP)
  - `443 -> 127.0.0.1:9443` (Traefik TLS, via TCP passthrough)

Nginx templates are in [deploy/nginx/README.md](deploy/nginx/README.md).

## 3) Secrets (must not be placeholders)
In `.env.prod`:
- `SECRET_KEY`: strong random value
- `POSTGRES_PASSWORD`: strong random value
- SMTP credentials if you use email (non-local SMTP requires creds)

## 4) Migrations
Recommended: run migrations as an explicit step:
- `./scripts/run-migrations-prod.sh`

If you keep `RUN_MIGRATIONS_ON_STARTUP=true`, startup will fail if migrations fail.

## 5) Backups
- Run backups periodically:
  - `./scripts/postgres-backup.sh`
- Store backups off-host and set retention.

## 6) Preflight checks
- Run:
  - `./scripts/prod-preflight.sh`

## 7) Go-live verification
From a machine on the public Internet:
- `curl -I http://DOMAIN/health` (should redirect to HTTPS)
- `curl -I https://DOMAIN/health` (should be 200)
