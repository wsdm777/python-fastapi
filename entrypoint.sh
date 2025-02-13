#!/bin/sh

echo "Waiting for database to be ready..."

until nc -z $DB_HOST $DB_PORT; do
  echo $DB_HOST $DB_PORT
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is up - running migrations"
alembic upgrade head

echo "Starting background task for listening to expired keys..."
python -c "from src.services.redis import listen_for_expiration_keys; import asyncio; asyncio.run(listen_for_expiration_keys())" &

echo "Starting application..."
exec gunicorn src.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080