#!/bin/bash

# stop.sh - Stop all running services

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "Stopping School Network Monitor..."

# Check if running with docker-compose
if docker-compose ps 2>/dev/null | grep -q "Up"; then
    log_info "Stopping Docker containers..."
    docker-compose down
    log_info "Docker containers stopped ✓"
fi

# Kill any running uvicorn processes
if pgrep -f "uvicorn main:app" > /dev/null; then
    log_info "Stopping uvicorn processes..."
    pkill -f "uvicorn main:app"
    log_info "Uvicorn processes stopped ✓"
fi

log_info "All services stopped!"