# Setup Guide

Complete guide for setting up the School Network Monitor.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [First Run](#first-run)
6. [Verification](#verification)

## Prerequisites

### System Requirements

- **Operating System:** Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10/11
- **Python:** 3.12 or higher
- **PostgreSQL:** 16 or higher
- **RAM:** Minimum 2GB, Recommended 4GB+
- **Disk Space:** Minimum 1GB free space

### Software Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    libpq-dev \
    build-essential
```

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.12 postgresql
```

#### Windows
1. Download and install Python 3.12 from [python.org](https://www.python.org/downloads/)
2. Download and install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
3. Ensure Python and PostgreSQL are in your system PATH

## Installation Methods

### Method 1: Automated Setup (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd school-network-backend

# Make setup script executable
chmod +x setup_dev.sh

# Run setup
./setup_dev.sh
```

The script will:
- ✅ Check Python version
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Create .env file
- ✅ Setup database
- ✅ Run migrations

### Method 2: Manual Setup

#### Step 1: Clone Repository
```bash
git clone <repository-url>
cd school-network-backend
```

#### Step 2: Create Virtual Environment
```bash
python3.12 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

#### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
nano .env  # or use your preferred editor
```

#### Step 5: Setup Database
```bash
# Create database
createdb school_network

# Run migrations
alembic upgrade head
```

### Method 3: Docker Setup
```bash
# Build and start containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Configuration

### Environment Variables

Edit `.env` file:
```bash
# Application
APP_NAME="School Network Monitor"
DEBUG=False
LOG_LEVEL=INFO
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/school_network

# Security
SECRET_KEY=your-secret-key-change-this-in-production

# Network Discovery
DEFAULT_NETWORK_RANGE=192.168.1.0/24

# SNMP
SNMP_COMMUNITY=public
SNMP_VERSION=2c

# Monitoring Intervals (seconds)
MONITORING_INTERVAL=60
CABLE_HEALTH_INTERVAL=300
DISCOVERY_SCAN_INTERVAL=3600
```

### Important Settings

#### SECRET_KEY
Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Database URL Format
```
postgresql://username:password@host:port/database_name
```

#### Network Range
Use CIDR notation for your network:
- Small network: `192.168.1.0/24` (254 hosts)
- Medium network: `10.0.0.0/16` (65,534 hosts)
- Large network: `172.16.0.0/12` (1,048,574 hosts)

## Database Setup

### PostgreSQL Installation

#### Ubuntu/Debian
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

### Database Creation

#### Method 1: Using psql
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE school_network;

# Create user (optional)
CREATE USER netmon WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE school_network TO netmon;

# Exit
\q
```

#### Method 2: Using Python Script
```bash
python -c "
import psycopg
conn = psycopg.connect('postgresql://postgres@localhost/postgres')
conn.autocommit = True
cursor = conn.cursor()
cursor.execute('CREATE DATABASE school_network')
cursor.close()
conn.close()
print('Database created successfully!')
"
```

### Run Migrations
```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
alembic upgrade head

# Verify
alembic current
```

### Verify Database
```bash
psql -U postgres -d school_network -c "\dt"
```

You should see tables: devices, ports, links, events, cable_health_metrics

## First Run

### Development Mode
```bash
# Activate virtual environment
source venv/bin/activate

# Start development server
./run.sh -m dev -r

# Or manually
uvicorn main:app --reload
```

### Production Mode
```bash
# Start production server
./run.sh -m prod -w 4

# Or manually
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Mode
```bash
./run.sh -m docker

# Or manually
docker-compose up -d
```

## Verification

### 1. Check Application Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "app": "School Network Monitor",
  "version": "1.0.0"
}
```

### 2. Access API Documentation

Open in browser:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### 3. Test Database Connection
```bash
curl http://localhost:8000/health/detailed
```

### 4. Run Basic Tests
```bash
pytest tests/test_health.py -v
```

### 5. Check Logs
```bash
# View application logs
tail -f logs/app.log

# View error logs
tail -f logs/error.log
```

## Post-Installation

### Create Test Data (Optional)
```bash
python scripts/seed_database.py
```

### Configure Network Discovery

1. Update `DEFAULT_NETWORK_RANGE` in `.env`
2. Ensure network permissions for ARP scanning
3. Configure SNMP community strings

### Setup Monitoring
```bash
# Test device discovery
curl -X POST "http://localhost:8000/api/v1/discovery/scan?network_range=192.168.1.0/24"

# Check monitoring status
curl http://localhost:8000/api/v1/monitoring/status
```

## Troubleshooting Setup

### Common Issues

#### Python Version Error
```bash
# Check Python version
python3 --version

# Must be 3.12 or higher
```

#### PostgreSQL Connection Error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U postgres -c "SELECT version();"
```

#### Permission Errors
```bash
# Fix script permissions
chmod +x *.sh

# Fix virtual environment
rm -rf venv
python3 -m venv venv
```

#### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill process or use different port
./run.sh -m dev -p 8080
```

## Next Steps

1. ✅ [Read Architecture Documentation](ARCHITECTURE.md)
2. ✅ [Explore API Documentation](API.md)
3. ✅ [Setup Production Deployment](DEPLOYMENT.md)
4. ✅ [Configure Monitoring](TROUBLESHOOTING.md)

## Support

If you encounter issues:
1. Check [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review logs in `logs/` directory
3. Check GitHub Issues
4. Contact support team

---

**Setup Complete!** 🎉

Your School Network Monitor is ready to use.