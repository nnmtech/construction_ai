#!/usr/bin/env sh
set -eu

# Production preflight checks for the "nginx owns 80/443 -> Traefik 9080/9443" topology.
#
# Usage:
#   ./scripts/prod-preflight.sh
#
# Reads env from .env.prod by default.

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env.prod}"

if [ ! -f "$ENV_FILE" ]; then
  echo >&2 "[preflight] Missing env file: $ENV_FILE"
  exit 1
fi

# shellcheck disable=SC1090
. "$ENV_FILE"

fail() { echo >&2 "[preflight] FAIL: $*"; exit 1; }
warn() { echo >&2 "[preflight] WARN: $*"; }
info() { echo "[preflight] $*"; }

require_nonempty() {
  var_name="$1"
  eval "val=\${$var_name:-}"
  [ -n "$val" ] || fail "$var_name must be set"
}

require_not_placeholder() {
  var_name="$1"
  placeholder="$2"
  eval "val=\${$var_name:-}"
  [ -n "$val" ] || fail "$var_name must be set"
  [ "$val" != "$placeholder" ] || fail "$var_name must not be '$placeholder'"
}

info "Checking required env vars"
require_nonempty DOMAIN
require_nonempty TRAEFIK_ACME_EMAIL
require_not_placeholder SECRET_KEY change-me
require_not_placeholder POSTGRES_PASSWORD change-me
require_nonempty POSTGRES_USER
require_nonempty POSTGRES_DB
require_nonempty DATABASE_URL

info "Checking production topology flags"
: "${PROXY_HTTP_PORT:=9080}"
: "${PROXY_HTTPS_PORT:=9443}"
: "${PROXY_BEHIND_LB:=true}"
: "${EXTERNAL_HTTP_PORT:=80}"
: "${EXTERNAL_HTTPS_PORT:=443}"

[ "$PROXY_BEHIND_LB" = "true" ] || fail "PROXY_BEHIND_LB must be true for nginx/LB-forward topology"
[ "$EXTERNAL_HTTP_PORT" = "80" ] || fail "EXTERNAL_HTTP_PORT must be 80"
[ "$EXTERNAL_HTTPS_PORT" = "443" ] || fail "EXTERNAL_HTTPS_PORT must be 443"

info "Checking local ports (Traefik should listen on $PROXY_HTTP_PORT/$PROXY_HTTPS_PORT)"
if ! ss -ltn 2>/dev/null | grep -q ":$PROXY_HTTP_PORT\b"; then
  warn "Port $PROXY_HTTP_PORT is not listening (Traefik may be down)"
fi
if ! ss -ltn 2>/dev/null | grep -q ":$PROXY_HTTPS_PORT\b"; then
  warn "Port $PROXY_HTTPS_PORT is not listening (Traefik may be down)"
fi

info "Checking nginx owns 80/443"
if ! ss -ltn 2>/dev/null | grep -q ":80\b"; then
  warn "Port 80 is not listening (nginx/LB may be missing)"
fi
if ! ss -ltn 2>/dev/null | grep -q ":443\b"; then
  warn "Port 443 is not listening (nginx/LB may be missing)"
fi

info "Checking nginx stream module support (best-effort)"
NGINX_BIN="${NGINX_BIN:-}"
if [ -z "$NGINX_BIN" ]; then
  if command -v nginx >/dev/null 2>&1; then
    NGINX_BIN="nginx"
  elif [ -x /usr/sbin/nginx ]; then
    NGINX_BIN="/usr/sbin/nginx"
  fi
fi

if [ -n "$NGINX_BIN" ]; then
  if "$NGINX_BIN" -V 2>&1 | tr ' ' '\n' | grep -q '^--with-stream'; then
    info "nginx stream module: present"
  else
    warn "nginx stream module not detected. If you want nginx 443 passthrough -> Traefik TLS, you need stream support."
  fi
else
  warn "nginx binary not found in PATH; cannot check stream module"
fi

info "Checking Traefik routing locally (expects /health to work via HTTPS entrypoint)"
if command -v curl >/dev/null 2>&1; then
  if curl -skI --resolve "$DOMAIN:$PROXY_HTTPS_PORT:127.0.0.1" "https://$DOMAIN:$PROXY_HTTPS_PORT/health" | head -n 1 | grep -q ' 200 '; then
    info "Traefik /health: OK"
  else
    warn "Traefik /health check did not return 200; investigate app/proxy logs"
  fi
else
  warn "curl not installed; skipping HTTP checks"
fi

info "Preflight checks complete"
