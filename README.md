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