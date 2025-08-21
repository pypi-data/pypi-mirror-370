#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p ./cerry_test/logs

# Start high priority worker with 4 processes
celery -A cerry_test.celery_app worker \
    --loglevel=info \
    --hostname=high_priority@%h \
    --queues=high_priority \
    --concurrency=4 \
    --logfile=./cerry_test/logs/high_priority.log &

# Start default worker with 2 processes
celery -A cerry_test.celery_app worker \
    --loglevel=info \
    --hostname=default@%h \
    --queues=default \
    --concurrency=2 \
    --logfile=./cerry_test/logs/default.log &

# Start flower for monitoring with API access enabled
export FLOWER_UNAUTHENTICATED_API=true
celery -A cerry_test.celery_app flower \
    --port=5555 \
    --basic_auth=admin:admin \
    --logging-level=info \
    --logfile=./cerry_test/logs/flower.log &

echo "All workers and Flower have been started!"
echo "Monitor at http://localhost:5555"
echo "Flower credentials: admin/admin" 