# TheFoxxStuff

Personal portfolio/blog website with music, arts, and blog sections.

## Tech Stack

- **Frontend**: SvelteKit + TailwindCSS
- **Backend**: FastAPI + MongoDB
- **Deployment**: Docker + Nginx

## Production Deployment

### Prerequisites on VPS
- Ubuntu 20.04+
- Docker & Docker Compose
- Nginx
- Node.js 20+ (for building frontend)
- Domains configured: `front.thefoxxstuff.net`, `api.thefoxxstuff.net`

### Quick Deploy

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/thefoxxstuff.git /opt/thefoxxstuff
cd /opt/thefoxxstuff

# 2. Fix DNS if needed (common on some VPS)
echo "nameserver 8.8.8.8" > /etc/resolv.conf

# 3. Create .env file
cat > .env << 'EOF'
SECRET_KEY=$(openssl rand -hex 32)
FRONTEND_URL=https://front.thefoxxstuff.net
EOF
# Generate real secret key
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/\$(openssl rand -hex 32)/$SECRET_KEY/" .env

# 4. Build frontend (do this on VPS to avoid RAM issues in Docker)
cd frontend
npm install
NODE_OPTIONS="--max-old-space-size=1024" VITE_API_BASE=https://api.thefoxxstuff.net/api npm run build
cd ..

# 5. Start Docker containers
docker compose up -d

# 6. Setup Nginx reverse proxy
cat > /etc/nginx/sites-available/thefoxxstuff << 'NGINX'
server {
    listen 80;
    server_name front.thefoxxstuff.net;
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name api.thefoxxstuff.net;
    client_max_body_size 100M;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/thefoxxstuff /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 7. Get SSL certificates
certbot --nginx -d front.thefoxxstuff.net -d api.thefoxxstuff.net
```

### Verify Deployment

```bash
# Check containers
docker compose ps

# Check API health
curl https://api.thefoxxstuff.net/api/health

# Check logs
docker compose logs -f
```

### Useful Commands

```bash
# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Restart services
docker compose restart

# Rebuild backend after changes
docker compose build --no-cache backend
docker compose up -d backend

# Rebuild frontend after changes
cd frontend
npm run build
cd ..
docker compose restart frontend
```

## Local Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
thefoxxstuff/
├── backend/
│   ├── routers/        # API endpoints
│   ├── main.py         # FastAPI app
│   ├── config.py       # Settings
│   ├── database.py     # MongoDB connection
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── routes/     # Pages
│   │   └── lib/        # Components, stores, API
│   ├── nginx.conf      # Nginx config for SPA
│   └── Dockerfile      # Optional Docker build
├── nginx/              # VPS Nginx configs
├── docker-compose.yml
└── .env.example
```
