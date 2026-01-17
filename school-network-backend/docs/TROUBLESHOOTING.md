# 🔧 Troubleshooting Guide

Comprehensive troubleshooting guide for School Network Monitor.

## 📋 Table of Contents

1. [Quick Diagnostics](#-quick-diagnostics)
2. [Installation Issues](#-installation-issues)
3. [Database Problems](#-database-problems)
4. [Application Errors](#-application-errors)
5. [Network Discovery Issues](#-network-discovery-issues)
6. [SNMP Problems](#-snmp-problems)
7. [Performance Issues](#-performance-issues)
8. [API Errors](#-api-errors)
9. [Docker Issues](#-docker-issues)
10. [Common Error Messages](#-common-error-messages)
11. [Logs and Debugging](#-logs-and-debugging)
12. [Recovery Procedures](#-recovery-procedures)

---

## 🚀 Quick Diagnostics

### Health Check Commands

Run these commands first to identify the problem area:
```bash
# 1. Check if application is running
curl http://localhost:8000/health

# 2. Check detailed health (includes database)
curl http://localhost:8000/health/detailed

# 3. Check system resources
htop  # or top

# 4. Check disk space
df -h

# 5. Check memory
free -h

# 6. Check database connection
psql -U netmon -d school_network -c "SELECT version();"

# 7. Check application logs
tail -f logs/app.log

# 8. Check error logs
tail -f logs/error.log

# 9. Check systemd service (if using systemd)
sudo systemctl status school-network

# 10. Check Docker containers (if using Docker)
docker-compose ps
docker-compose logs -f
```

### Quick Fix Checklist

✅ **Before seeking help, verify:**

- [ ] Application is running
- [ ] Database is accessible
- [ ] Network connectivity is working
- [ ] Sufficient disk space (>1GB free)
- [ ] Sufficient memory (>500MB free)
- [ ] Python virtual environment is activated
- [ ] Environment variables are set correctly
- [ ] Firewall allows required ports
- [ ] PostgreSQL service is running
- [ ] Correct Python version (3.12+)

---

## 🔨 Installation Issues

### Problem: Python Version Mismatch

**Symptoms:**
```
ERROR: This package requires Python 3.12 or higher
```

**Solution:**
```bash
# Check current version
python3 --version

# Ubuntu/Debian - Install Python 3.12
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev

# Verify installation
python3.12 --version

# Recreate virtual environment
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Problem: pip Installation Fails

**Symptoms:**
```
ERROR: Could not build wheels for psycopg
```

**Solution:**
```bash
# Install build dependencies
sudo apt-get install -y \
    build-essential \
    libpq-dev \
    python3.12-dev

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies again
pip install -r requirements.txt
```

---

### Problem: Virtual Environment Not Activated

**Symptoms:**
- Packages not found
- Wrong Python version
- Module import errors

**Solution:**
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# Verify activation (should show venv path)
which python
python --version
```

---

### Problem: setup_dev.sh Permission Denied

**Symptoms:**
```
bash: ./setup_dev.sh: Permission denied
```

**Solution:**
```bash
# Make script executable
chmod +x setup_dev.sh

# Run setup
./setup_dev.sh

# Alternative: run with bash
bash setup_dev.sh
```

---

## 💾 Database Problems

### Problem: Cannot Connect to PostgreSQL

**Symptoms:**
```
psycopg.OperationalError: could not connect to server
```

**Diagnosis:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check PostgreSQL port
sudo netstat -plnt | grep 5432

# Test connection
psql -U postgres -h localhost
```

**Solutions:**

**Solution 1: Start PostgreSQL**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Solution 2: Check PostgreSQL Configuration**
```bash
# Edit pg_hba.conf
sudo nano /etc/postgresql/16/main/pg_hba.conf

# Ensure this line exists:
# host    all    all    127.0.0.1/32    md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

**Solution 3: Check Database URL in .env**
```bash
# Verify DATABASE_URL format
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Test connection with psql
psql "postgresql://netmon:password@localhost:5432/school_network"
```

---

### Problem: Database Does Not Exist

**Symptoms:**
```
psycopg.OperationalError: database "school_network" does not exist
```

**Solution:**
```bash
# Create database
sudo -u postgres psql -c "CREATE DATABASE school_network;"

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE school_network TO netmon;"

# Verify
psql -U netmon -d school_network -c "\dt"
```

---

### Problem: Authentication Failed

**Symptoms:**
```
psycopg.OperationalError: FATAL: password authentication failed for user "netmon"
```

**Solutions:**

**Solution 1: Reset Password**
```bash
sudo -u postgres psql
ALTER USER netmon WITH PASSWORD 'your_new_password';
\q

# Update .env file
nano .env
# Change: DATABASE_URL=postgresql://netmon:your_new_password@localhost:5432/school_network
```

**Solution 2: Configure Trust Authentication (Development Only)**
```bash
# Edit pg_hba.conf
sudo nano /etc/postgresql/16/main/pg_hba.conf

# Change this line:
# host    all    all    127.0.0.1/32    md5
# To:
# host    all    all    127.0.0.1/32    trust

# Restart PostgreSQL
sudo systemctl restart postgresql
```

⚠️ **Warning:** Trust authentication is insecure. Use only for development.

---

### Problem: Migration Fails

**Symptoms:**
```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solutions:**

**Solution 1: Check Current Version**
```bash
alembic current
alembic history
```

**Solution 2: Run Migrations**
```bash
# Upgrade to latest
alembic upgrade head

# If that fails, check for conflicts
alembic check
```

**Solution 3: Reset Migrations (⚠️ Data Loss)**
```bash
# Backup database first!
pg_dump -U netmon school_network > backup.sql

# Drop and recreate database
sudo -u postgres psql -c "DROP DATABASE school_network;"
sudo -u postgres psql -c "CREATE DATABASE school_network;"

# Run migrations
alembic upgrade head
```

---

### Problem: Too Many Database Connections

**Symptoms:**
```
psycopg.OperationalError: FATAL: too many connections for database
```

**Solution:**
```bash
# Check current connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Kill idle connections
sudo -u postgres psql << EOF
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'school_network' 
AND pid <> pg_backend_pid()
AND state = 'idle';
EOF

# Increase max connections (if needed)
sudo nano /etc/postgresql/16/main/postgresql.conf
# Change: max_connections = 200

# Restart PostgreSQL
sudo systemctl restart postgresql
```

---

## 🐛 Application Errors

### Problem: Application Won't Start

**Symptoms:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Verify virtual environment is activated
which python
# Should show: /path/to/venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

---

### Problem: Import Errors

**Symptoms:**
```
ImportError: cannot import name 'Device' from 'models.device'
```

**Solutions:**

**Solution 1: Check File Structure**
```bash
# Verify all __init__.py files exist
find . -type d -name models -o -name schemas -o -name api | xargs ls -la

# Create missing __init__.py
touch models/__init__.py
touch schemas/__init__.py
```

**Solution 2: Check Circular Imports**
```bash
# Run Python with import debugging
python -v -c "from models.device import Device"
```

**Solution 3: Restart Application**
```bash
# Kill existing processes
pkill -f "uvicorn main:app"

# Start fresh
uvicorn main:app --reload
```

---

### Problem: Port Already in Use

**Symptoms:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
```bash
# Find process using port 8000
sudo lsof -i :8000
# or
sudo netstat -tulpn | grep 8000

# Kill the process
sudo kill -9 <PID>

# Or use a different port
uvicorn main:app --port 8001
```

---

### Problem: CORS Errors

**Symptoms:**
```
Access to fetch at 'http://localhost:8000/api/v1/devices' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**
```bash
# Update .env file
nano .env

# Add your frontend URL to ALLOWED_ORIGINS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:4200,http://yourdomain.com

# Restart application
```

---

### Problem: Pydantic Validation Errors

**Symptoms:**
```
pydantic.error_wrappers.ValidationError: 1 validation error for DeviceCreate
```

**Solution:**

Check the error details and fix the request:
```python
# Error might show:
# field required (type=value_error.missing)
# Means: Required field is missing in request

# Or:
# value is not a valid enumeration member (type=type_error.enum)
# Means: Invalid enum value provided

# Check API documentation for correct schema
curl http://localhost:8000/api/docs
```

---

## 🌐 Network Discovery Issues

### Problem: No Devices Found During Scan

**Symptoms:**
```json
{
  "devices_found": 0,
  "network_range": "192.168.1.0/24"
}
```

**Diagnosis:**
```bash
# Test network connectivity
ping 192.168.1.1

# Check if you can reach devices
nmap -sn 192.168.1.0/24

# Verify network interface
ip addr show

# Check routing
ip route
```

**Solutions:**

**Solution 1: Check Network Permissions**
```bash
# ARP requires root/sudo or CAP_NET_RAW capability
# Run with sudo (development only)
sudo uvicorn main:app

# Or grant capabilities (production)
sudo setcap cap_net_raw+ep $(which python3.12)
```

**Solution 2: Check Firewall**
```bash
# Check firewall status
sudo ufw status

# Allow ICMP
sudo ufw allow from 192.168.1.0/24

# Allow ARP (no specific rule needed, but ensure not blocked)
```

**Solution 3: Verify Network Range**
```bash
# Check your actual network
ip addr show

# Use correct network range
# If your IP is 10.0.0.5, use 10.0.0.0/24, not 192.168.1.0/24
```

---

### Problem: Discovery Timeout

**Symptoms:**
```
Discovery timed out after 30 seconds
```

**Solution:**
```bash
# Increase timeout in .env
nano .env

# Add or modify:
DISCOVERY_TIMEOUT=60
PING_TIMEOUT=5

# Restart application
```

---

### Problem: ARP Scan Permission Denied

**Symptoms:**
```
PermissionError: [Errno 1] Operation not permitted
```

**Solution:**
```bash
# Option 1: Run with sudo (development only)
sudo uvicorn main:app

# Option 2: Grant CAP_NET_RAW capability
sudo setcap cap_net_raw+ep $(readlink -f $(which python3.12))

# Option 3: Add user to netdev group
sudo usermod -aG netdev $USER
# Logout and login again

# Verify capabilities
getcap $(which python3.12)
```

---

## 📡 SNMP Problems

### Problem: SNMP Timeout

**Symptoms:**
```
SNMP error for host 192.168.1.1: Request timeout
```

**Diagnosis:**
```bash
# Test SNMP manually
snmpwalk -v2c -c public 192.168.1.1 system

# Or
snmpget -v2c -c public 192.168.1.1 sysDescr.0
```

**Solutions:**

**Solution 1: Verify SNMP is Enabled on Device**
```bash
# On Cisco devices:
# conf t
# snmp-server community public RO
# end

# Verify
show snmp community
```

**Solution 2: Check Community String**
```bash
# Update .env with correct community
nano .env
SNMP_COMMUNITY=your_actual_community

# Common community strings:
# public (default, read-only)
# private (read-write)
```

**Solution 3: Check SNMP Version**
```bash
# Try different versions
snmpwalk -v1 -c public 192.168.1.1 system  # SNMPv1
snmpwalk -v2c -c public 192.168.1.1 system # SNMPv2c

# Update .env
SNMP_VERSION=2c  # or 1
```

**Solution 4: Check Firewall**
```bash
# SNMP uses UDP port 161
sudo ufw allow from 192.168.1.0/24 to any port 161 proto udp

# Or temporarily disable firewall to test
sudo ufw disable
# Test SNMP
# Re-enable
sudo ufw enable
```

---

### Problem: SNMP Returns No Data

**Symptoms:**
```
SNMP query succeeded but returned no interfaces
```

**Solution:**
```bash
# Check if device supports MIB-II
snmpwalk -v2c -c public 192.168.1.1 .1.3.6.1.2.1.2.2

# Check device documentation for supported OIDs

# Try different OID bases
snmpwalk -v2c -c public 192.168.1.1 interfaces
snmpwalk -v2c -c public 192.168.1.1 ifTable
```

---

## ⚡ Performance Issues

### Problem: Slow API Responses

**Symptoms:**
- Requests take >5 seconds
- Timeouts in frontend

**Diagnosis:**
```bash
# Check database query performance
psql -U netmon -d school_network << EOF
EXPLAIN ANALYZE SELECT * FROM devices WHERE status = 'UP';
EOF

# Check for missing indexes
psql -U netmon -d school_network << EOF
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public';
EOF

# Check slow queries
psql -U netmon -d school_network << EOF
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
EOF
```

**Solutions:**

**Solution 1: Add Missing Indexes**
```sql
-- Add indexes for commonly queried fields
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_type ON devices(device_type);
CREATE INDEX idx_links_source ON links(source_device_id);
CREATE INDEX idx_events_created ON events(created_at);
```

**Solution 2: Optimize Database Connection Pool**
```python
# In database.py
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=20,        # Increase pool size
    max_overflow=40,     # Increase overflow
    pool_pre_ping=True,
    pool_recycle=3600
)
```

**Solution 3: Increase Workers**
```bash
# Increase number of uvicorn workers
uvicorn main:app --workers 8 --host 0.0.0.0 --port 8000
```

**Solution 4: Enable Query Caching (with Redis)**
```bash
# Install Redis
sudo apt install redis-server

# Update .env
REDIS_URL=redis://localhost:6379/0

# Restart application
```

---

### Problem: High Memory Usage

**Symptoms:**
```
MemoryError: Unable to allocate memory
```

**Diagnosis:**
```bash
# Check memory usage
free -h

# Check process memory
ps aux | grep python

# Check for memory leaks
htop  # Press F4 and filter by 'python'
```

**Solutions:**

**Solution 1: Reduce Connection Pool**
```python
# In database.py
pool_size=5,         # Reduce from 20
max_overflow=10,     # Reduce from 40
```

**Solution 2: Limit Workers**
```bash
# Reduce number of workers
# Formula: workers = (2 × CPU cores) + 1
uvicorn main:app --workers 4
```

**Solution 3: Add Swap Space**
```bash
# Create 2GB swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

### Problem: High CPU Usage

**Symptoms:**
- CPU usage consistently >90%
- Application slow or unresponsive

**Diagnosis:**
```bash
# Check CPU usage
top
htop

# Profile Python application
python -m cProfile -o profile.stats main.py
```

**Solutions:**

**Solution 1: Reduce Monitoring Frequency**
```bash
# Update .env
MONITORING_INTERVAL=120      # Increase from 60
CABLE_HEALTH_INTERVAL=600    # Increase from 300
DISCOVERY_SCAN_INTERVAL=7200 # Increase from 3600

# Restart application
```

**Solution 2: Optimize Monitoring**
```python
# Limit concurrent device checks
# In services/monitoring.py
semaphore = asyncio.Semaphore(10)  # Max 10 concurrent checks
```

**Solution 3: Disable Unnecessary Features**
```bash
# Temporarily disable background monitoring
# Comment out in main.py:
# await start_background_monitoring()
```

---

## 🌐 API Errors

### Problem: 401 Unauthorized

**Symptoms:**
```json
{
  "detail": "Could not validate credentials",
  "status_code": 401
}
```

**Solution:**
```bash
# Ensure Authorization header is included
curl -X GET "http://localhost:8000/api/v1/devices" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Generate new token if expired
# (Token generation endpoint to be implemented)

# Check token expiration
# Decode JWT at https://jwt.io
```

---

### Problem: 422 Validation Error

**Symptoms:**
```json
{
  "detail": [
    {
      "loc": ["body", "device_type"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

**Solution:**
```bash
# Check valid enum values in API docs
curl http://localhost:8000/api/docs

# Fix request body
# Valid device_type values: ROUTER, SWITCH, SERVER, PC, AP, PRINTER, CAMERA, UNKNOWN

# Correct example:
curl -X POST "http://localhost:8000/api/v1/devices" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Device",
    "device_type": "ROUTER"
  }'
```

---

### Problem: 500 Internal Server Error

**Symptoms:**
```json
{
  "detail": "Internal server error",
  "status_code": 500
}
```

**Diagnosis:**
```bash
# Check application logs
tail -f logs/error.log

# Check for Python exceptions
tail -f logs/app.log | grep ERROR

# Check systemd logs (if using systemd)
sudo journalctl -u school-network -n 50
```

**Solutions:**

**Solution 1: Check Database Connection**
```bash
# Test database
curl http://localhost:8000/health/detailed

# Reconnect if needed
sudo systemctl restart postgresql
sudo systemctl restart school-network
```

**Solution 2: Review Stack Trace**
```bash
# Enable debug mode temporarily
nano .env
DEBUG=True

# Restart and check logs
./run.sh -m dev
```

**Solution 3: Check for Unhandled Exceptions**
```python
# Add more error handling in code
try:
    # operation
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    raise
```

---

## 🐳 Docker Issues

### Problem: Container Won't Start

**Symptoms:**
```
ERROR: Container school-network-app exited with code 1
```

**Diagnosis:**
```bash
# Check container logs
docker-compose logs app

# Check container status
docker-compose ps

# Inspect container
docker inspect school-network-app
```

**Solutions:**

**Solution 1: Check Environment Variables**
```bash
# Verify .env file exists
cat .env

# Check if variables are loaded
docker-compose config
```

**Solution 2: Rebuild Containers**
```bash
# Stop containers
docker-compose down

# Remove volumes (⚠️ Data loss)
docker-compose down -v

# Rebuild
docker-compose build --no-cache

# Start
docker-compose up -d
```

**Solution 3: Check Dependencies**
```bash
# Ensure database is ready before app starts
# In docker-compose.yml:
depends_on:
  postgres:
    condition: service_healthy
```

---

### Problem: Cannot Connect to Database from Container

**Symptoms:**
```
psycopg.OperationalError: could not translate host name "postgres" to address
```

**Solution:**
```bash
# Check if containers are on same network
docker network ls
docker network inspect school-network_default

# Verify DATABASE_URL in .env
# Use service name as hostname:
DATABASE_URL=postgresql://netmon:password@postgres:5432/school_network
# NOT localhost!

# Restart containers
docker-compose restart
```

---

### Problem: Port Conflicts

**Symptoms:**
```
ERROR: for app Cannot start service app: 
Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solution:**
```bash
# Check what's using the port
sudo lsof -i :8000

# Stop the conflicting service
sudo kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # External:Internal
```

---

### Problem: Docker Build Fails

**Symptoms:**
```
ERROR: failed to solve: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully
```

**Solution:**
```bash
# Check Dockerfile syntax
cat Dockerfile

# Build with verbose output
docker-compose build --progress=plain

# Check available disk space
df -h

# Clean up Docker to free space
docker system prune -a
docker volume prune
```

---

## ⚠️ Common Error Messages

### Error: "Module 'pydantic' has no attribute 'BaseModel'"

**Cause:** Pydantic version mismatch

**Solution:**
```bash
pip install --upgrade pydantic
pip install "pydantic>=2.5.0"
```

---

### Error: "asyncpg.exceptions.UndefinedTableError"

**Cause:** Database tables not created

**Solution:**
```bash
# Run migrations
alembic upgrade head

# Verify tables exist
psql -U netmon -d school_network -c "\dt"
```

---

### Error: "Cannot import name 'AsyncSession' from 'sqlalchemy.ext.asyncio'"

**Cause:** SQLAlchemy version mismatch

**Solution:**
```bash
pip install --upgrade sqlalchemy
pip install "sqlalchemy>=2.0.23"
```

---

### Error: "No module named 'psycopg'"

**Cause:** Missing psycopg3 package

**Solution:**
```bash
pip install "psycopg[binary]>=3.2"
```

---

### Error: "regex= parameter not supported"

**Cause:** Pydantic v2 syntax change

**Solution:**
```bash
# In schemas, change:
# regex=r"pattern"
# To:
# pattern=r"pattern"
```

---

### Error: "The asyncio extension requires an async driver"

**Cause:** Wrong database driver

**Solution:**
```bash
# Change DATABASE_URL format
# From: postgresql://...
# To:   postgresql+psycopg://...

nano .env
DATABASE_URL=postgresql+psycopg://netmon:password@localhost:5432/school_network
```

---

## 📝 Logs and Debugging

### Log Locations
```
Application Logs:
├── logs/app.log          # General application logs
├── logs/error.log        # Error logs only
└── logs/access.log       # API access logs

System Logs:
├── /var/log/nginx/       # Nginx logs
├── /var/log/postgresql/  # PostgreSQL logs
└── systemd journal       # System service logs
```

### Enable Debug Logging

**Temporary (Current Session):**
```bash
# Set in environment
export LOG_LEVEL=DEBUG
uvicorn main:app --reload
```

**Permanent:**
```bash
# Update .env
nano .env
LOG_LEVEL=DEBUG
DEBUG=True

# Restart application
```

### View Logs in Real-Time
```bash
# Application logs
tail -f logs/app.log

# Error logs only
tail -f logs/error.log

# Filter for specific patterns
tail -f logs/app.log | grep ERROR
tail -f logs/app.log | grep "device_id"

# Docker logs
docker-compose logs -f app

# Systemd logs
sudo journalctl -u school-network -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Increase Log Verbosity
```python
# In core/logger.py, modify log level
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO
    ...
)

# Enable SQL query logging
# In database.py
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # Enable SQL logging
    ...
)
```

### Debug Specific Modules
```python
# In your code
import logging
logger = logging.getLogger(__name__)

# Add debug statements
logger.debug(f"Variable value: {variable}")
logger.info(f"Processing device: {device_id}")
logger.warning(f"Unusual condition: {condition}")
logger.error(f"Error occurred: {error}", exc_info=True)
```

---

## 🔄 Recovery Procedures

### Complete Application Reset
```bash
# ⚠️ WARNING: This will delete all data!

# 1. Stop application
sudo systemctl stop school-network
# or
docker-compose down

# 2. Backup database
pg_dump -U netmon school_network > backup_$(date +%Y%m%d).sql

# 3. Drop and recreate database
sudo -u postgres psql << EOF
DROP DATABASE school_network;
CREATE DATABASE school_network;
GRANT ALL PRIVILEGES ON DATABASE school_network TO netmon;
EOF

# 4. Run migrations
source venv/bin/activate
alembic upgrade head

# 5. Restart application
sudo systemctl start school-network
# or
docker-compose up -d
```

---

### Restore from Backup
```bash
# 1. Stop application
sudo systemctl stop school-network

# 2. Drop existing database
sudo -u postgres psql -c "DROP DATABASE school_network;"

# 3. Create new database
sudo -u postgres psql -c "CREATE DATABASE school_network;"

# 4. Restore from backup
psql -U netmon school_network < backup_20250117.sql

# 5. Start application
sudo systemctl start school-network
```

---

### Clean Reinstall
```bash
# 1. Backup data
pg_dump -U netmon school_network > backup.sql
cp .env .env.backup

# 2. Remove application
rm -rf /opt/school-network-backend

# 3. Clone fresh copy
cd /opt
git clone https://github.com/your-org/school-network-backend.git
cd school-network-backend

# 4. Run setup
./setup_dev.sh

# 5. Restore .env
cp /path/to/.env.backup .env

# 6. Restore database
psql -U netmon school_network < /path/to/backup.sql

# 7. Start application
./run.sh -m prod
```

---

### Emergency Procedures

#### System Unresponsive
```bash
# 1. Force kill application
sudo pkill -9 -f uvicorn

# 2. Restart PostgreSQL
sudo systemctl restart postgresql

# 3. Clear locks
sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'school_network';"

# 4. Start application
sudo systemctl start school-network
```

#### Database Corruption
```bash
# 1. Stop application
sudo systemctl stop school-network

# 2. Verify database integrity
sudo -u postgres psql school_network -c "VACUUM FULL ANALYZE;"

# 3. Reindex
sudo -u postgres psql school_network -c "REINDEX DATABASE school_network;"

# 4. Check for corruption
sudo -u postgres pg_dump school_network > /dev/null

# 5. If corrupt, restore from backup
```

---

## 🆘 Getting Help

### Before Asking for Help

Prepare this information:
```bash
# 1. System Information
cat /etc/os-release
python --version
psql --version

# 2. Application Version
cat .env | grep APP_VERSION

# 3. Error Logs
tail -100 logs/error.log > error_snapshot.txt

# 4. Configuration (sanitized)
cat .env | grep -v PASSWORD | grep -v SECRET

# 5. Health Status
curl http://localhost:8000/health/detailed

# 6. Database Status
psql -U netmon -d school_network -c "\dt"
```

### Support Channels

1. **Check Documentation**
   - README.md
   - ARCHITECTURE.md
   - API.md
   - This file (TROUBLESHOOTING.md)

2. **Search Issues**
   - GitHub Issues: https://github.com/your-org/school-network-backend/issues
   - Stack Overflow: [school-network-monitor] tag

3. **Community**
   - Discord Server: (if available)
   - Forum: (if available)

4. **Direct Support**
   - Email: support@yourdomain.com
   - Emergency: emergency@yourdomain.com (critical issues only)

### Creating a Good Bug Report

Include:
```markdown
## Environment
- OS: Ubuntu 22.04
- Python: 3.12.1
- PostgreSQL: 16.1
- Installation Method: Docker / Manual

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Steps to Reproduce
1. Start application
2. Navigate to /api/v1/devices
3. Click "Create Device"
4. Error occurs

## Error Message
```
[Paste full error message and stack trace]
```

## Logs
```
[Paste relevant log excerpts]
```

## Screenshots
[If applicable]

## What I've Tried
- Restarted application
- Checked logs
- Verified database connection
```

---

## 📚 Additional Resources

### Useful Commands Reference
```bash
# System Monitoring
htop                                    # Interactive process viewer
df -h                                   # Disk usage
free -h                                 # Memory usage
netstat -tulpn                          # Network connections
lsof -i :8000                          # What's using port 8000

# Docker
docker-compose ps                       # Container status
docker-compose logs -f                  # Follow logs
docker-compose restart app              # Restart service
docker-compose down && docker-compose up -d  # Full restart
docker system prune -a                  # Clean up

# PostgreSQL
psql -U netmon school_network           # Connect to DB
\dt                                     # List tables
\d devices                              # Describe table
\l                                      # List databases
\q                                      # Quit

# Application
uvicorn main:app --reload              # Development mode
uvicorn main:app --workers 4           # Production mode
alembic upgrade head                    # Run migrations
alembic current                         # Check migration version
pytest                                  # Run tests
```

### Performance Monitoring Commands
```bash
# Monitor CPU and Memory
watch -n 1 'ps aux | grep python | grep -v grep'

# Monitor Database Performance
psql -U netmon school_network -c "SELECT * FROM pg_stat_activity;"

# Monitor Network Connections
watch -n 1 'netstat -an | grep :8000 | wc -l'

# Monitor Disk I/O
iostat -x 1

# Monitor Logs
tail -f logs/app.log | grep -E 'ERROR|WARNING'
```

---

## 🔍 Diagnostic Scripts

### Health Check Script

Save as `check_health.sh`:
```bash
#!/bin/bash

echo "=== School Network Monitor Health Check ==="
echo ""

# Check application
echo "1. Application Status:"
curl -s http://localhost:8000/health || echo "❌ Application not responding"
echo ""

# Check database
echo "2. Database Status:"
psql -U netmon -d school_network -c "SELECT 1;" > /dev/null 2>&1 && echo "✅ Database OK" || echo "❌ Database error"
echo ""

# Check disk space
echo "3. Disk Space:"
df -h | grep -E '^Filesystem|/$'
echo ""

# Check memory
echo "4. Memory:"
free -h
echo ""

# Check processes
echo "5. Running Processes:"
ps aux | grep -E 'uvicorn|postgres' | grep -v grep
echo ""

# Check logs for errors
echo "6. Recent Errors:"
tail -20 logs/error.log 2>/dev/null || echo "No error log found"
echo ""

echo "=== Health Check Complete ==="
```

Run with:
```bash
chmod +x check_health.sh
./check_health.sh
```

---

**Last Updated:** January 17, 2025  
**Version:** 1.0  
**For Questions:** Consult documentation or contact support