# Используем официальный Python образ как базовый
FROM python:3.10-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы приложения в контейнер
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем PostgreSQL клиент для работы с базой данных
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Экспонируем порт, на котором будет работать приложение
EXPOSE 8501

# Запускаем приложение
CMD ["streamlit", "run", "app.py"]
