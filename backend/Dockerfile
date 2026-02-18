# ── Stage 1: build (компилируем C-расширения: pillow, bcrypt) ─────────────────
FROM python:3.12-slim AS builder
WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Устанавливаем в /install — скопируем в runtime
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: runtime (только нужные lib, без компилятора) ─────────────────────
FROM python:3.12-slim AS runtime
WORKDIR /app

# Только runtime-зависимости для Pillow (без gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    libpng16-16 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Копируем пакеты из builder
COPY --from=builder /install /usr/local

# Код приложения
COPY . .

RUN mkdir -p /app/uploads

# Запускаем не от root — безопасность
RUN adduser --disabled-password --gecos '' --uid 1001 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# 2 воркера — оптимум для 2GB VPS
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
