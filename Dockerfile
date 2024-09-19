# Используем базовый образ Python
FROM python:3.9-slim

# Установим системные зависимости
# RUN apt-get update && apt-get install -y \
#     libxkbcommon-x11-0 \
#     libgl1-mesa-glx \
#     libglib2.0-0 \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

RUN pip3 install opencv-python-headless

# Установим рабочую директорию
WORKDIR /app

# Скопируем и установим зависимости
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Скопируем код приложения
COPY . .

# Запуск приложения
CMD ["python", "app/init.py"]
