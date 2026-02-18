#!/bin/bash

# TheFoxxStuff VPS Setup Script
# Run this script on your Ubuntu VPS to set up the project

set -e

echo "=== TheFoxxStuff VPS Setup ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Update system
echo -e "${YELLOW}Updating system...${NC}"
apt update && apt upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose plugin if not installed
if ! docker compose version &> /dev/null; then
    echo -e "${YELLOW}Installing Docker Compose plugin...${NC}"
    apt install docker-compose-plugin -y
fi

# Install Nginx if not installed
if ! command -v nginx &> /dev/null; then
    echo -e "${YELLOW}Installing Nginx...${NC}"
    apt install nginx -y
    systemctl enable nginx
fi

# Install Certbot for SSL
if ! command -v certbot &> /dev/null; then
    echo -e "${YELLOW}Installing Certbot...${NC}"
    apt install certbot python3-certbot-nginx -y
fi

# Install Git
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}Installing Git...${NC}"
    apt install git -y
fi

# Create project directory
PROJECT_DIR="/opt/thefoxxstuff"
echo -e "${YELLOW}Creating project directory at ${PROJECT_DIR}...${NC}"
mkdir -p $PROJECT_DIR

# Clone or update repository
if [ -d "$PROJECT_DIR/.git" ]; then
    echo -e "${YELLOW}Updating repository...${NC}"
    cd $PROJECT_DIR
    git pull origin main
else
    echo -e "${YELLOW}Cloning repository...${NC}"
    echo "Enter your GitHub repository URL:"
    read REPO_URL
    git clone $REPO_URL $PROJECT_DIR
fi

cd $PROJECT_DIR

# Create .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
    echo -e "${GREEN}.env file created with secure SECRET_KEY${NC}"
fi

# Setup Nginx
echo -e "${YELLOW}Setting up Nginx...${NC}"
cp nginx/thefoxxstuff.conf /etc/nginx/sites-available/thefoxxstuff
ln -sf /etc/nginx/sites-available/thefoxxstuff /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
nginx -t && systemctl reload nginx

echo -e "${GREEN}Nginx configured!${NC}"

# Get SSL certificates
echo -e "${YELLOW}Setting up SSL certificates...${NC}"
echo "Make sure your domains (front.thefoxxstuff.net and api.thefoxxstuff.net) point to this server!"
echo "Press Enter to continue or Ctrl+C to cancel..."
read

certbot --nginx -d front.thefoxxstuff.net -d api.thefoxxstuff.net

# Build and start Docker containers
echo -e "${YELLOW}Building and starting Docker containers...${NC}"
docker compose build
docker compose up -d

# Show status
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
docker compose ps
echo ""
echo -e "${GREEN}Your site should be available at:${NC}"
echo "  Frontend: https://front.thefoxxstuff.net"
echo "  API: https://api.thefoxxstuff.net"
echo ""
echo -e "${YELLOW}To view logs:${NC}"
echo "  docker compose logs -f"
echo ""
echo -e "${YELLOW}To restart services:${NC}"
echo "  docker compose restart"
