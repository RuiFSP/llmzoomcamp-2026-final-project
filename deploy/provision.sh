#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <host>"
    echo "Example: $0 root@123.456.78.90"
    exit 1
fi

HOST=$1

echo "==> Installing Docker on $HOST ..."
ssh "$HOST" "
    apt-get update -qq
    apt-get install -y -qq ca-certificates curl
    UBUNTU_CODENAME=\$(grep -oP 'VERSION_CODENAME=\K.*' /etc/os-release || echo "jammy")
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | tee /etc/apt/keyrings/docker.asc > /dev/null
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \${UBUNTU_CODENAME} stable" > /etc/apt/sources.list.d/docker.list
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-compose-plugin
    systemctl enable docker
    systemctl start docker
    echo 'Docker installed successfully'
"

echo "==> Done. Now run: ./deploy/deploy.sh $HOST"
