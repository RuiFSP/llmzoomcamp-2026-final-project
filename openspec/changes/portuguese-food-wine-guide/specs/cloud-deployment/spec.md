## ADDED Requirements

### Requirement: System deploys to a cloud VM
The system SHALL provide deployment scripts to run the full docker-compose stack on a single cloud VM (e.g., DigitalOcean, AWS EC2).

#### Scenario: Provision VM
- **WHEN** `deploy/provision.sh <host>` runs against a fresh VM
- **THEN** Docker Engine and docker-compose-plugin are installed on the VM

#### Scenario: Deploy stack
- **WHEN** `deploy/deploy.sh <host>` runs
- **THEN** the project files are rsynced to the VM and `docker compose up -d` is executed

### Requirement: Cloud mode adds HTTPS
The system SHALL include a Caddy reverse proxy behind `COMPOSE_PROFILES=cloud` so local dev remains unchanged.

#### Scenario: Local dev (default)
- **WHEN** `docker compose up` runs without COMPOSE_PROFILES
- **THEN** only api, qdrant, postgres, and grafana start; Caddy is excluded

#### Scenario: Cloud mode
- **WHEN** `COMPOSE_PROFILES=cloud docker compose up` runs
- **THEN** Caddy starts as a reverse proxy and provisions Let's Encrypt TLS for the configured domain
