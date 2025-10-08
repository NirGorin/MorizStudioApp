#!/usr/bin/env bash
set -euo pipefail

echo "Waiting for database to be ready..."
ATTEMPTS=0
until nc -z "${DB_HOST:-db}" "${DB_PORT:-5432}"; do
  ATTEMPTS=$((ATTEMPTS+1))
  if [ "$ATTEMPTS" -ge "${DB_WAIT_MAX_ATTEMPTS:-60}" ]; then
    echo "DB not ready after ${DB_WAIT_MAX_ATTEMPTS:-60}s"
    exit 1
  fi
  echo "Waiting (${ATTEMPTS}/${DB_WAIT_MAX_ATTEMPTS:-60}) for ${DB_HOST:-db}:${DB_PORT:-5432} ..."
  sleep 1
done
echo "Database is up."

if command -v alembic >/dev/null 2>&1 && [ -d "alembic" ]; then
  echo "Running Alembic migrations..."
  alembic upgrade head || { echo "Alembic failed"; exit 1; }
else
  echo "Alembic not found or no 'alembic' dir — skipping migrations."
fi

APP_IMPORT_PATH="${APP_IMPORT_PATH:-app.main:app}"   
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-1}"        
RELOAD="${RELOAD:-false}"      

echo "Starting Uvicorn (${APP_IMPORT_PATH}) on ${HOST}:${PORT} (workers=${WORKERS}, reload=${RELOAD})..."
if [ "$RELOAD" = "true" ]; then
  exec uvicorn "$APP_IMPORT_PATH" \
    --host "$HOST" --port "$PORT" \
    --proxy-headers \
    --forwarded-allow-ips="*" \
    --reload \
    --reload-dir "/app/app" \
    --reload-include "**/*.py" \
    --reload-exclude ".git/*" \
    --reload-exclude ".pytest_cache/*" \
    --reload-exclude "__pycache__/*" \
    --reload-exclude "venv/*" \
    --reload-exclude ".venv/*" \
    --reload-exclude "node_modules/*"
else
  exec uvicorn "$APP_IMPORT_PATH" \
    --host "$HOST" --port "$PORT" \
    --proxy-headers \
    --forwarded-allow-ips="*" \
    --workers "$WORKERS"
fi

