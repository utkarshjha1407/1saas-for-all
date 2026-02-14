#!/bin/bash
# Development startup script

echo "Starting CareOps Backend Development Environment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Copy .env.example to .env and configure it."
    exit 1
fi

# Start services with docker-compose
docker-compose up --build

# Alternative: Run locally without Docker
# echo "Starting API server..."
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
# 
# echo "Starting Celery worker..."
# celery -A app.tasks.celery_app worker --loglevel=info &
# 
# echo "Starting Celery beat..."
# celery -A app.tasks.celery_app beat --loglevel=info &
# 
# wait
