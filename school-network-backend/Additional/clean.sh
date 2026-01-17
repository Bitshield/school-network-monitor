#!/bin/bash

# clean.sh - Clean up generated files and caches

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo "Cleaning up..."

# Python cache
log_info "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Pytest cache
log_info "Removing pytest cache..."
rm -rf .pytest_cache 2>/dev/null || true
rm -rf htmlcov 2>/dev/null || true
rm -f .coverage 2>/dev/null || true

# Logs
log_warn "Clearing log files..."
rm -f logs/*.log 2>/dev/null || true

# Build artifacts
log_info "Removing build artifacts..."
rm -rf build/ 2>/dev/null || true
rm -rf dist/ 2>/dev/null || true
rm -rf *.egg-info 2>/dev/null || true

# Database (optional)
read -p "Remove database file? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f *.db *.sqlite *.sqlite3 2>/dev/null || true
    log_info "Database files removed"
fi

log_info "Cleanup complete!"