FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода и скриптов
COPY ./app ./app
COPY ./scripts/wait-for-it.sh /wait-for-it.sh

# Создание пользователя без прав root и настройка прав
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app && \
    chmod +x /wait-for-it.sh

# Переключение на непривилегированного пользователя
USER appuser

# Команда запуска приложения с ожиданием базы данных
ENTRYPOINT ["/wait-for-it.sh", "db"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 