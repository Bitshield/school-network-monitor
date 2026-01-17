#!/bin/bash

# setup_dev.sh - Development environment setup script
# This script sets up the complete development environment

set -e  # Exit on error

echo "=================================="
echo "School Network Monitor - Dev Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Check Python version
log_info "Checking Python version..."
if ! command_exists python3; then
    log_error "Python 3 is not installed. Please install Python 3.12 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.12"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    log_error "Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

log_info "Python version: $PYTHON_VERSION ✓"

# Step 2: Check PostgreSQL
log_info "Checking PostgreSQL..."
if ! command_exists psql; then
    log_warn "PostgreSQL client not found. Please install PostgreSQL."
    log_warn "Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    log_warn "macOS: brew install postgresql"
    log_warn "Windows: Download from https://www.postgresql.org/download/"
fi

# Step 3: Create virtual environment
log_info "Creating virtual environment..."
if [ -d "venv" ]; then
    log_warn "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    log_info "Virtual environment created ✓"
fi

# Step 4: Activate virtual environment
log_info "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix/Linux/macOS
    source venv/bin/activate
fi

# Step 5: Upgrade pip
log_info "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Step 6: Install dependencies
log_info "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    log_info "Dependencies installed ✓"
else
    log_error "requirements.txt not found!"
    exit 1
fi

# Step 7: Install development dependencies
log_info "Installing development dependencies..."
pip install pytest pytest-asyncio pytest-cov black flake8 mypy isort

# Step 8: Setup environment file
log_info "Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        log_info "Created .env from .env.example"
        log_warn "Please update .env with your configuration!"
    else
        log_warn ".env.example not found. Creating basic .env..."
        cat > .env << EOF
# Application
APP_NAME="School Network Monitor"
APP_VERSION="1.0.0"
DEBUG=True
LOG_LEVEL=DEBUG
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://postgres@localhost:5432/school_network

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=dev-secret-key-change-in-production

# Network Discovery
DEFAULT_NETWORK_RANGE=192.168.1.0/24

# SNMP
SNMP_COMMUNITY=public
SNMP_VERSION=2c

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:4200,http://localhost:8080
EOF
        log_info "Basic .env file created. Please update as needed."
    fi
else
    log_info ".env file already exists ✓"
fi

# Step 9: Create necessary directories
log_info "Creating necessary directories..."
mkdir -p logs
mkdir -p static/uploads
mkdir -p tests
mkdir -p alembic/versions
touch static/uploads/.gitkeep
log_info "Directories created ✓"

# Step 10: Check PostgreSQL database
log_info "Checking database connection..."
DB_EXISTS=$(PGPASSWORD="" psql -U postgres -h localhost -lqt 2>/dev/null | cut -d \| -f 1 | grep -w school_network | wc -l)

if [ "$DB_EXISTS" -eq 0 ]; then
    log_warn "Database 'school_network' does not exist."
    read -p "Would you like to create it now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PGPASSWORD="" psql -U postgres -h localhost -c "CREATE DATABASE school_network;" 2>/dev/null
        if [ $? -eq 0 ]; then
            log_info "Database created successfully ✓"
        else
            log_error "Failed to create database. Please create it manually:"
            log_error "psql -U postgres -c 'CREATE DATABASE school_network;'"
        fi
    fi
else
    log_info "Database 'school_network' exists ✓"
fi

# Step 11: Run database migrations
log_info "Running database migrations..."
if command_exists alembic; then
    alembic upgrade head
    log_info "Database migrations completed ✓"
else
    log_warn "Alembic not found. Skipping migrations."
fi

# Step 12: Run code formatting
log_info "Formatting code with black and isort..."
if command_exists black; then
    black . --exclude venv 2>/dev/null || true
fi
if command_exists isort; then
    isort . --skip venv 2>/dev/null || true
fi

# Step 13: Create sample test file if tests directory is empty
if [ ! "$(ls -A tests)" ]; then
    log_info "Creating sample test file..."
    cat > tests/test_health.py << 'EOF'
"""Sample test file."""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
EOF
    touch tests/__init__.py
    log_info "Sample test file created ✓"
fi

# Step 14: Display summary
echo ""
echo "=================================="
log_info "Development environment setup complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "     source venv/Scripts/activate"
else
    echo "     source venv/bin/activate"
fi
echo ""
echo "  2. Update .env file with your configuration"
echo ""
echo "  3. Start the development server:"
echo "     python main.py"
echo "     or"
echo "     uvicorn main:app --reload"
echo ""
echo "  4. Access the API documentation:"
echo "     http://localhost:8000/api/docs"
echo ""
echo "  5. Run tests:"
echo "     pytest"
echo ""
echo "=================================="

# Optional: Start the server
read -p "Would you like to start the development server now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Starting development server..."
    python main.py
fi