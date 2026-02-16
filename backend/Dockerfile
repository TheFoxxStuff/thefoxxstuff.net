# Этап 1: Сборка зависимостей
FROM python:3.11-alpine as builder

WORKDIR /app

# Устанавливаем системные зависимости для компиляции (если нужны)
RUN apk add --no-cache gcc musl-dev libffi-dev

COPY requirements.txt .
# Устанавливаем библиотеки в отдельную папку
RUN pip install --user --no-cache-dir -r requirements.txt

# Этап 2: Финальный образ
FROM python:3.11-alpine

WORKDIR /app

# Копируем только установленные библиотеки из этапа сборки
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

# Запуск через gunicorn или uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]