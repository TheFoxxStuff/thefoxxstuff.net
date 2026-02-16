# TheFoxxStuff Website

Fullstack-приложение: **FastAPI** (Backend) + **Svelte** (Frontend).

## 📂 Структура проекта
* `backend/` — API на Python (FastAPI).
* `frontend/` — Интерфейс на Svelte.
* `docker-compose.yml` — Конфигурация для быстрого развертывания.

---

cd backend
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
pip install -r requirements.txt
# Создайте .env файл на основе .env.example
cp .env.example .env 
python main.py

pip freeze > requirements.txt - создание requirements.txt
python version 3.14.0

choco install ffmpeg




VPS (Beget 1GB)
Считаем математику потребления:

ОС Linux: ~200–300 МБ
FastAPI: ~150–200 МБ
Svelte (Runtime/Nginx): ~50 МБ (но 800 МБ во время сборки!)
Redis: ~150 МБ
Итого: У тебя остается около 300 МБ «свободного воздуха».







VPS

Создание Swap-файла (если RAM < 2 Гб)
fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile

Создание нового пользователя
adduser myusername
usermod -aG sudo myusername



Установка полезных утилит

htop — красивый мониторинг ресурсов (процессор, память).
curl или wget — для скачивания файлов.
git — чтобы клонировать свой проект с GitHub.

apt install htop git curl -y



установка докера
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

установка nginx
sudo apt update
sudo apt install nginx -y
systemctl status nginx



sudo certbot --nginx -d api.thefoxxstuff.net -d front.thefoxxstuff.net