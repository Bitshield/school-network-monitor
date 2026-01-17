#!/bin/bash

# logs.sh - View application logs

MODE="${1:-app}"

case $MODE in
    app)
        echo "Viewing application logs..."
        tail -f logs/app.log
        ;;
    error)
        echo "Viewing error logs..."
        tail -f logs/error.log
        ;;
    access)
        echo "Viewing access logs..."
        tail -f logs/access.log
        ;;
    docker)
        echo "Viewing Docker logs..."
        docker-compose logs -f
        ;;
    *)
        echo "Usage: ./logs.sh [app|error|access|docker]"
        exit 1
        ;;
esac