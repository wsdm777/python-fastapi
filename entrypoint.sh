#!/bin/sh

echo "Waiting for database to be ready..."

until nc -z $DB_HOST $DB_PORT; do
  echo $DB_HOST $DB_PORT
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is up - running migrations"
alembic upgrade head

echo "Starting application..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload