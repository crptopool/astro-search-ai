FROM python:3.12.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Entrypoint is set by docker-compose command
EXPOSE 8000
EXPOSE 8501