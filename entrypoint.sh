#!/bin/bash
set -e

# 1. Wait for postgres
echo "Waiting for postgres at db:5432..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "Connection to db succeeded!"

# 2. ONLY run migrations if the command is starting the app
# We check if the first argument starts with 'uvicorn'
if [[ "$1" == "uvicorn"* ]]; then
  echo "Applying database migrations..."
  alembic upgrade head
fi

echo "Starting command: $@"
exec "$@"