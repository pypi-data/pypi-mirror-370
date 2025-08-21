#!/bin/bash

# Set environment variable for Flower API access
export FLOWER_UNAUTHENTICATED_API=true

case "$1" in
    "status")
        echo "Checking Celery worker status..."
        celery -A cerry_test.celery_app status
        ;;
    "inspect")
        echo "Inspecting active workers..."
        celery -A cerry_test.celery_app inspect active
        echo -e "\nWorker statistics:"
        celery -A cerry_test.celery_app inspect stats
        ;;
    "stop")
        echo "Stopping all Celery workers..."
        pkill -f 'celery worker'
        pkill -f 'flower'
        echo "All workers and flower have been stopped."
        ;;
    "stop-graceful")
        echo "Gracefully stopping all Celery workers..."
        celery -A cerry_test.celery_app control shutdown
        pkill -f 'flower'
        echo "All workers and flower are being stopped gracefully."
        ;;
    *)
        echo "Usage: $0 {status|inspect|stop|stop-graceful}"
        echo "  status        - Show basic worker status"
        echo "  inspect       - Show detailed worker information"
        echo "  stop         - Force stop all workers immediately"
        echo "  stop-graceful - Gracefully stop workers (wait for tasks to complete)"
        exit 1
        ;;
esac 