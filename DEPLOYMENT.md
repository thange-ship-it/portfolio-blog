# Deployment & Operations Runbook

Notes on how `timhange.com` is hosted, plus a log of issues we've hit and how we
fixed them. Keep this updated as things change.

## Architecture

- **Server:** `srv1284050` (Hostinger VPS).
- **Hosting model:** a Docker Compose stack at `/docker/n8n/docker-compose.yml`
  (project name `n8n`). It runs several sites on one server.
- **Reverse proxy:** a **Traefik** container owns ports **80** and **443**,
  terminates TLS (Let's Encrypt certs, auto-renewed), redirects HTTP→HTTPS, and
  routes requests to each app container by hostname.
- **This app:** `portfolio-blog` — a Flask app served by **gunicorn** on port
  5000 inside its container, built from `/home/portfolio-blog` (this folder).

Hostname routing (set via Traefik labels in the compose file):

| Hostname                   | Container      | Source dir              |
| -------------------------- | -------------- | ----------------------- |
| `timhange.com`             | portfolio-blog | `/home/portfolio-blog`  |
| `cudata.timhange.com`      | frcs-app       | `/home/cudata/frcs-app` |
| `midwestfest.timhange.com` | mcsf-app       | `/home/mcsf-app`        |
| `sashachat.timhange.com`   | esl-chatbot    | `/home/esl-chatbot`     |
| `<subdomain>.timhange.com` | n8n            | (n8n image)             |

## Common operations

Run these from `/docker/n8n` (where the compose file lives).

```bash
# See what's running
docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'

# Deploy code changes to this site (rebuild + restart just this app)
cd /docker/n8n && docker compose up -d --build portfolio-blog

# Restart the reverse proxy (see the port-80 issue below)
cd /docker/n8n && docker compose up -d --force-recreate traefik

# Logs
docker logs --tail 50 n8n-portfolio-blog-1
docker logs --tail 50 n8n-traefik-1
```

Quick health check:

```bash
curl -sS -I https://timhange.com          # expect: HTTP/2 200, server: gunicorn
curl -sS -I http://timhange.com           # expect: 308 redirect to https
```

## Issue log

### 2026-07-07 — Site showed "Welcome to nginx!" / HTTPS down

**Symptom:** `http://timhange.com` returned the default nginx welcome page;
`https://timhange.com` wouldn't connect at all. Same for the other subdomains.

**Cause:** The server had rebooted. A **system `nginx` service** (separate from
Docker, `enabled` at boot, serving only a placeholder page) started first and
grabbed port 80. Traefik then couldn't bind port 80 and died:

```
failed to bind host port 0.0.0.0:80/tcp: address already in use   (exit 128)
```

With Traefik down, nothing routed traffic to the app containers and there was no
HTTPS.

**Fix:**

```bash
systemctl disable --now nginx     # stop it AND stop it auto-starting on reboot
cd /docker/n8n && docker compose up -d --force-recreate traefik
```

**Gotcha:** `docker start n8n-traefik-1` alone was *not* enough — the container
came up "running" but never published ports 80/443. Recreating it via
`docker compose up -d --force-recreate traefik` fixed the port publishing.

**Prevention:** nginx is now disabled, so it won't steal port 80 on future
reboots. If the site ever shows a generic "Welcome to nginx!" page again, check
whether nginx got re-enabled (`systemctl is-enabled nginx`) and whether Traefik
is up (`docker ps | grep traefik`).
