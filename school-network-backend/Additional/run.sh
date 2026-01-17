#!/bin/bash

# run.sh - Production/Development server runner
# This script runs the application with proper configuration

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
MODE="dev"
PORT=8000
HOST="0.0.0.0"
WORKERS=4
RELOAD=false

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_banner() {
    echo -e "${BLUE}"
    cat << "EOF"
   _____      __                __   _   __     __                      __  
  / ___/_____/ /_  ____  ____  / /  / | / /__  / /__      ______  _____/ /__
  \__ \/ ___/ __ \/ __ \/ __ \/ /  /  |/ / _ \/ __/ | /| / / __ \/ ___/ //_/
 ___/ / /__/ / / / /_/ / /_/ / /  / /|  /  __/ /_ | |/ |/ / /_/ / /  / ,<   
/____/\___/_/ /_/\____/\____/_/  /_/ |_/\___/\__/ |__/|__/\____/_/  /_/|_|  
                                                                              
                    M O N I T O R   S Y S T E M
EOF
    echo -e "${NC}"
}

show_help() {
    cat << EOF
Usage: ./run.sh [OPTIONS]

Options:
    -m, --mode MODE         Run mode: dev, prod, docker (default: dev)
    -p, --port PORT         Port to run on (default: 8000)
    -h, --host HOST         Host to bind to (default: 0.0.0.0)
    -w, --workers NUM       Number of worker processes (default: 4)
    -r, --reload            Enable auto-reload (dev mode only)
    --help                  Show this help message

Modes:
    dev     - Development mode with auto-reload
    prod    - Production mode with multiple workers
    docker  - Docker mode (uses docker-compose)
    test    - Run tests

Examples:
    ./run.sh                           # Run in dev mode
    ./run.sh -m prod -w 8              # Run in production with 8 workers
    ./run.sh -m dev -r -p 3000         # Dev mode with reload on port 3000
    ./run.sh -m docker                 # Run with docker-compose
    ./run.sh -m test                   # Run tests

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -r|--reload)
            RELOAD=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Show banner
show_banner

# Check if .env exists
if [ ! -f ".env" ]; then
    log_warn ".env file not found!"
    if [ -f ".env.example" ]; then
        log_info "Creating .env from .env.example..."
        cp .env.example .env
        log_warn "Please update .env with your configuration before running in production!"
    else
        log_error "No .env.example found. Please create .env file manually."
        exit 1
    fi
fi

# Source environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check Python virtual environment
if [ ! -d "venv" ]; then
    log_warn "Virtual environment not found. Please run setup_dev.sh first."
    exit 1
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Run based on mode
case $MODE in
    dev)
        log_info "Starting in DEVELOPMENT mode..."
        log_info "Port: $PORT"
        log_info "Host: $HOST"
        log_info "Auto-reload: $RELOAD"
        echo ""
        
        if [ "$RELOAD" = true ]; then
            uvicorn main:app --host $HOST --port $PORT --reload --log-level debug
        else
            uvicorn main:app --host $HOST --port $PORT --log-level debug
        fi
        ;;
        
    prod)
        log_info "Starting in PRODUCTION mode..."
        log_info "Port: $PORT"
        log_info "Host: $HOST"
        log_info "Workers: $WORKERS"
        echo ""
        
        # Run database migrations
        log_info "Running database migrations..."
        alembic upgrade head
        
        # Start production server
        uvicorn main:app \
            --host $HOST \
            --port $PORT \
            --workers $WORKERS \
            --log-level info \
            --access-log \
            --use-colors
        ;;
        
    docker)
        log_info "Starting with DOCKER COMPOSE..."
        
        # Check if docker-compose is installed
        if ! command -v docker-compose &> /dev/null; then
            log_error "docker-compose is not installed!"
            exit 1
        fi
        
        # Build and start containers
        log_info "Building Docker images..."
        docker-compose build
        
        log_info "Starting containers..."
        docker-compose up -d
        
        log_info "Waiting for services to be ready..."
        sleep 5
        
        # Show status
        docker-compose ps
        
        echo ""
        log_info "Application is running!"
        log_info "API: http://localhost:$PORT"
        log_info "Docs: http://localhost:$PORT/api/docs"
        echo ""
        log_info "View logs: docker-compose logs -f"
        log_info "Stop: docker-compose down"
        ;;
        
    test)
        log_info "Running TESTS..."
        echo ""
        
        # Run tests with coverage
        pytest -v --cov=. --cov-report=html --cov-report=term-missing
        
        log_info "Coverage report generated in htmlcov/index.html"
        ;;
        
    *)
        log_error "Unknown mode: $MODE"
        show_help
        exit 1
        ;;
esac