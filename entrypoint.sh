#!/bin/sh

echo "Waiting for database to be ready..."

until nc -z db 5432; do
  echo db 5432
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is up - running migrations"
alembic upgrade head

echo "Starting background task for listening to expired keys..."
python -c "from src.services.redis import listen_for_expiration_keys; import asyncio; asyncio.run(listen_for_expiration_keys())" &

UVICORN_WORKERS=${UVICORN_WORKERS:-1}

echo "Starting application with $UVICORN_WORKERS workers..."
exec gunicorn src.main:app --workers "$UVICORN_WORKERS" --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000