# Nginx fronting Traefik (production topology)

Goal: **nginx owns external ports 80/443** and forwards to **Traefik on 9080/9443** on the same host.

This matches:
- External: `80 -> nginx -> 9080 -> Traefik`
- External: `443 -> nginx -> 9443 -> Traefik`

## Why this exists
On many hosts, something already owns privileged ports (80/443) or you prefer to keep Traefik unprivileged. This lets you do that while still serving the public site on standard ports.

## Files
- `construction-ai-http.conf`: nginx **HTTP** reverse proxy `:80 -> 127.0.0.1:9080`
- `construction-ai-stream.conf`: nginx **TCP passthrough** `:443 -> 127.0.0.1:9443` (Traefik terminates TLS)

## What you must set in the app stack
In your `.env.prod` on the host:
- `PROXY_HTTP_PORT=9080`
- `PROXY_HTTPS_PORT=9443`
- `PROXY_BEHIND_LB=true`
- `EXTERNAL_HTTP_PORT=80`
- `EXTERNAL_HTTPS_PORT=443`

## Nginx install/enable (typical Ubuntu layout)
1) Put the HTTP config where nginx includes it:
- `/etc/nginx/sites-available/construction-ai.conf` (or `/etc/nginx/conf.d/construction-ai.conf`)

2) Replace `YOUR_DOMAIN_HERE` with your real domain.

3) Enable it (sites-available layout):
- `ln -s /etc/nginx/sites-available/construction-ai.conf /etc/nginx/sites-enabled/`

4) Enable stream passthrough include (one-time):
- Edit `/etc/nginx/nginx.conf` and add:
  ```
  stream {
      include /etc/nginx/stream-enabled/*.conf;
  }
  ```
- Create directory: `mkdir -p /etc/nginx/stream-enabled`
- Place `construction-ai-stream.conf` into `/etc/nginx/stream-enabled/construction-ai-stream.conf`

5) Validate + reload:
- `nginx -t`
- `systemctl reload nginx`

## Notes / constraints
- With TCP passthrough on 443, nginx cannot add `X-Forwarded-*` headers for HTTPS; Traefik will see the client IP as nginx unless you add Proxy Protocol support end-to-end.
- Let’s Encrypt HTTP-01 requires port 80 publicly reachable.
