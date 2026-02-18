#!/bin/bash
# Закрывает прямой доступ к backend/frontend портам
# Запускать от root / sudo

echo "Setting up UFW firewall..."

ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw deny 8000   # Backend — только через Nginx
ufw deny 3000   # Frontend — только через Nginx

ufw --force enable
ufw status verbose

echo "UFW configured!"
