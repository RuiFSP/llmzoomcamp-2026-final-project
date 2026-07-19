# Cloud Deployment

The same Docker Compose stack runs on a cloud VM with Caddy for automatic TLS termination and a reverse proxy on port 80/443.

## Requirements

- A DigitalOcean $6/mo droplet (or equivalent), Ubuntu 22.04+
- A domain name pointing to the VM's IP (required for HTTPS)
- An OpenAI API key (set in `.env` before deploying)

## Quick Deploy

```bash
# 1. Provision the VM (installs Docker)
./deploy/provision.sh root@<vm-ip>

# 2. Deploy the stack (rsync + docker compose up)
./deploy/deploy.sh root@<vm-ip> your-domain.com
```

## Manual Steps

```bash
export COMPOSE_PROFILES=cloud
export DOMAIN=your-domain.com
docker compose up -d --build
```

## Endpoints

| Service | URL |
|---|---|
| Chat UI | `http://<vm-ip>:5000` or `https://your-domain.com` |
| API health | `http://<vm-ip>:5000/api/health` |
| Grafana | `http://<vm-ip>:3000` (admin / admin) |

## Scripts

- `deploy/provision.sh` — Installs Docker Engine on a fresh Ubuntu VM via SSH. Auto-detects the Ubuntu codename.
- `deploy/deploy.sh` — Rsyncs the project to `/opt/food-wine-guide/` and runs `docker compose up -d` with the cloud profile. Accepts an optional domain argument for HTTPS.
