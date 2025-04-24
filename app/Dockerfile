# Используем официальный Python образ как базовый
FROM python:3.12.4-slim
# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы приложения в контейнер
COPY . .

RUN pip3 install --upgrade pip
# Устанавливаем зависимости
RUN pip3 install --no-cache-dir -r requirements.txt

# Устанавливаем PostgreSQL клиент для работы с базой данных
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Экспонируем порт, на котором будет работать приложение
EXPOSE 8501

# Запускаем приложение
CMD ["streamlit", "run", "app.py", "--server.maxUploadSize", "5"]
