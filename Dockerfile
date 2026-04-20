FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libfreetype6-dev libjpeg-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/backend
ENV DATA_DIR=/data
ENV DATABASE_PATH=/data/posyandu.db

VOLUME ["/data"]

EXPOSE 8000

CMD uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}
