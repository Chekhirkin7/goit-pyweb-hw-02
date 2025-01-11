# Базовий образ Python
FROM python:3.10-slim

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# Встановлюємо Poetry
RUN pip install poetry

# Створюємо робочу директорію в контейнері
WORKDIR /app

# Копіюємо проект до контейнера
COPY . /app

# Встановлюємо залежності через Poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Вказуємо команду за замовчуванням для запуску програми
CMD ["python", "main.py"]
