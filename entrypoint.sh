#!/bin/bash

while ! nc -z db 5432; do
  echo "Waiting for the database to become available..."
  sleep 1
done

poetry run alembic upgrade head

poetry run uvicorn main:app --host 0.0.0.0 --port 8000
