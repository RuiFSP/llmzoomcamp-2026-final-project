#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <host> [domain]"
    echo "Example: $0 root@123.456.78.90 foodwine.example.com"
    exit 1
fi

HOST=$1
DOMAIN=${2:-$HOST}

echo "==> Copying project files to $HOST ..."
rsync -avz --exclude '.venv' --exclude '__pycache__' --exclude '.git' --exclude '.env' --exclude 'data/raw' . "$HOST":/opt/food-wine-guide/

echo "==> Starting stack on $HOST ..."
ssh "$HOST" "
    cd /opt/food-wine-guide
    export COMPOSE_PROFILES=cloud
    export DOMAIN=$DOMAIN
    docker compose pull
    docker compose up -d --build
    echo 'Stack started successfully'
    docker compose ps
"

echo "==> Done! Access at https://$DOMAIN"
