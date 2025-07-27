#!/bin/bash

# Default values
PORT=${PORT:-9395}
WORKERS=${WORKERS:-4}
TIMEOUT=${TIMEOUT:-120}
KEEPALIVE=${KEEPALIVE:-2}
MAX_REQUESTS=${MAX_REQUESTS:-1000}
MAX_REQUESTS_JITTER=${MAX_REQUESTS_JITTER:-50}

echo "Starting Wargos with Gunicorn..."
echo "Port: $PORT"
echo "Workers: $WORKERS"
echo "Timeout: $TIMEOUT"
echo "Keep-alive: $KEEPALIVE"
echo "Max requests: $MAX_REQUESTS"
echo "Max requests jitter: $MAX_REQUESTS_JITTER"

# Run Gunicorn with Uvicorn workers
gunicorn app.main:app \
    --bind 0.0.0.0:$PORT \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout $TIMEOUT \
    --keep-alive $KEEPALIVE \
    --max-requests $MAX_REQUESTS \
    --max-requests-jitter $MAX_REQUESTS_JITTER \
    --reload
