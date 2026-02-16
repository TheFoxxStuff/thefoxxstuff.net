# TheFoxxStuff

Personal portfolio/blog website with music, arts, and blog sections.

## Tech Stack

- **Frontend**: SvelteKit + TailwindCSS
- **Backend**: FastAPI + MongoDB
- **Deployment**: Docker + Nginx

## Quick Start (Development)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Production Deployment

### Prerequisites on VPS
- Ubuntu 20.04+
- Docker & Docker Compose
- Nginx
- Domain configured (front.thefoxxstuff.net, api.thefoxxstuff.net)

### Initial Setup

1. **SSH into your VPS and clone the repository:**
```bash
sudo git clone https://github.com/YOUR_USERNAME/thefoxxstuff.git /opt/thefoxxstuff
cd /opt/thefoxxstuff
```

2. **Run the setup script:**
```bash
sudo chmod +x scripts/setup-vps.sh
sudo ./scripts/setup-vps.sh
```

Or manually:

3. **Create environment file:**
```bash
cp .env.example .env
# Edit .env and set SECRET_KEY
nano .env
```

4. **Setup Nginx:**
```bash
sudo cp nginx/thefoxxstuff.conf /etc/nginx/sites-available/thefoxxstuff
sudo ln -s /etc/nginx/sites-available/thefoxxstuff /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

5. **Get SSL certificates:**
```bash
sudo certbot --nginx -d front.thefoxxstuff.net -d api.thefoxxstuff.net
```

6. **Build and start:**
```bash
docker compose up -d --build
```

### CI/CD Setup (GitHub Actions)

Add these secrets to your GitHub repository (Settings → Secrets → Actions):

| Secret | Description |
|--------|-------------|
| `VPS_HOST` | Your VPS IP address or hostname |
| `VPS_USER` | SSH username (usually `root` or your user) |
| `VPS_SSH_KEY` | Private SSH key for authentication |

To generate SSH key:
```bash
ssh-keygen -t ed25519 -C "github-actions"
# Add public key to VPS: ~/.ssh/authorized_keys
# Copy private key to GitHub secrets
```

Now every push to `main` branch will automatically deploy!

## Useful Commands

```bash
# View logs
docker compose logs -f

# Restart services
docker compose restart

# Rebuild and restart
docker compose up -d --build

# Stop all
docker compose down

# Database backup
docker exec thefoxxstuff-mongo mongodump --out /data/backup
docker cp thefoxxstuff-mongo:/data/backup ./backup

# Enter container shell
docker exec -it thefoxxstuff-api bash
docker exec -it thefoxxstuff-front sh
```

## Project Structure

```
thefoxxstuff/
├── backend/           # FastAPI backend
│   ├── routers/       # API endpoints
│   ├── models.py      # Pydantic models
│   ├── database.py    # MongoDB connection
│   ├── config.py      # Settings
│   └── Dockerfile
├── frontend/          # SvelteKit frontend
│   ├── src/
│   │   ├── routes/    # Pages
│   │   └── lib/       # Components, stores, API
│   └── Dockerfile
├── nginx/             # Nginx configs
├── scripts/           # Deployment scripts
├── docker-compose.yml
└── .github/workflows/ # CI/CD
```
