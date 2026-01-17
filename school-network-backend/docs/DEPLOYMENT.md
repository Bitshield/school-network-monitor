# 🚀 Deployment Guide

Complete production deployment guide for School Network Monitor.

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#-pre-deployment-checklist)
2. [Environment Preparation](#-environment-preparation)
3. [Docker Deployment](#-docker-deployment)
4. [Manual Deployment](#-manual-deployment)
5. [Production Configuration](#-production-configuration)
6. [Database Migration](#-database-migration)
7. [Monitoring Setup](#-monitoring-setup)
8. [Backup Strategy](#-backup-strategy)
9. [SSL/TLS Configuration](#-ssltls-configuration)
10. [Performance Tuning](#-performance-tuning)

---

## ✅ Pre-Deployment Checklist

### Required Software
- [ ] Python 3.12+
- [ ] PostgreSQL 16+
- [ ] Redis 7+ (optional, for caching)
- [ ] Nginx (for reverse proxy)
- [ ] Docker & Docker Compose (for containerized deployment)
- [ ] Git

### Security Requirements
- [ ] Generate secure SECRET_KEY
- [ ] Configure CORS allowed origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set strong database passwords
- [ ] Review and limit API rate limits

### Infrastructure
- [ ] Minimum 2 CPU cores
- [ ] Minimum 4GB RAM
- [ ] Minimum 20GB disk space
- [ ] Network access to monitored devices
- [ ] Static IP or domain name

---

## 🌍 Environment Preparation

### 1. Server Setup (Ubuntu 20.04/22.04)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    build-essential \
    libpq-dev

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Create Application User
```bash
# Create dedicated user
sudo useradd -m -s /bin/bash netmon
sudo passwd netmon

# Add to necessary groups
sudo usermod -aG sudo netmon

# Switch to user
sudo su - netmon
```

### 3. Clone Repository
```bash
cd /opt
sudo git clone https://github.com/your-org/school-network-backend.git
sudo chown -R netmon:netmon school-network-backend
cd school-network-backend
```

---

## 🐳 Docker Deployment (Recommended)

### Directory Structure
```
school-network-backend/
├── docker-compose.yml
├── Dockerfile
├── .env
├── docker/
│   ├── nginx/
│   │   └── nginx.conf
│   └── postgres/
│       └── init.sql
└── app/
```

### 1. Configure Environment

Create production `.env` file:
```bash
cat > .env << 'EOF'
# Application
APP_NAME="School Network Monitor"
APP_VERSION="1.0.0"
DEBUG=False
LOG_LEVEL=INFO
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://netmon:SecurePassword123!@postgres:5432/school_network
POSTGRES_USER=netmon
POSTGRES_PASSWORD=SecurePassword123!
POSTGRES_DB=school_network
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PORT=6379

# Security
SECRET_KEY=your-super-secure-secret-key-change-this-immediately-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Network Discovery
DEFAULT_NETWORK_RANGE=192.168.1.0/24
DISCOVERY_TIMEOUT=3
PING_TIMEOUT=2
ARP_RETRY_COUNT=2

# SNMP
SNMP_COMMUNITY=public
SNMP_VERSION=2c
SNMP_TIMEOUT=5
SNMP_RETRIES=3

# Monitoring Intervals (seconds)
MONITORING_INTERVAL=60
PORT_CHECK_INTERVAL=120
CABLE_HEALTH_INTERVAL=300
DISCOVERY_SCAN_INTERVAL=3600

# Performance
MAX_PACKET_LOSS_PERCENT=5.0
MAX_LATENCY_MS=100.0

# Application Port
APP_PORT=8000

# pgAdmin (optional)
PGADMIN_EMAIL=admin@yourdomain.com
PGADMIN_PASSWORD=AdminPassword123!
PGADMIN_PORT=5050
EOF
```

⚠️ **IMPORTANT:** Change all passwords and SECRET_KEY!

### 2. Generate Secure SECRET_KEY
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output to .env SECRET_KEY
```

### 3. Build and Start Containers
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

### 4. Initialize Database
```bash
# Run migrations
docker-compose exec app alembic upgrade head

# Verify
docker-compose exec app alembic current
```

### 5. Create Test Data (Optional)
```bash
docker-compose exec app python scripts/seed_database.py
```

### 6. Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "app": "School Network Monitor",
  "version": "1.0.0",
  "environment": "production"
}
```

---

## 🔧 Manual Deployment

### 1. Install Application
```bash
cd /opt/school-network-backend

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Database
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE school_network;
CREATE USER netmon WITH PASSWORD 'SecurePassword123!';
GRANT ALL PRIVILEGES ON DATABASE school_network TO netmon;
ALTER DATABASE school_network OWNER TO netmon;
\q
```

### 3. Configure Environment
```bash
cp .env.example .env
nano .env
# Edit configuration (same as Docker example above)
```

### 4. Run Migrations
```bash
source venv/bin/activate
alembic upgrade head
```

### 5. Create Systemd Service
```bash
sudo nano /etc/systemd/system/school-network.service
```
```ini
[Unit]
Description=School Network Monitor API
After=network.target postgresql.service

[Service]
Type=notify
User=netmon
Group=netmon
WorkingDirectory=/opt/school-network-backend
Environment="PATH=/opt/school-network-backend/venv/bin"
ExecStart=/opt/school-network-backend/venv/bin/uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info \
    --access-log

# Restart configuration
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=30

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/school-network-backend/logs

[Install]
WantedBy=multi-user.target
```

### 6. Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable school-network
sudo systemctl start school-network
sudo systemctl status school-network
```

### 7. View Logs
```bash
# Systemd logs
sudo journalctl -u school-network -f

# Application logs
tail -f /opt/school-network-backend/logs/app.log
```

---

## ⚙️ Production Configuration

### Nginx Reverse Proxy

#### 1. Install Nginx
```bash
sudo apt install nginx -y
```

#### 2. Configure Site
```bash
sudo nano /etc/nginx/sites-available/school-network
```
```nginx
# HTTP - Redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name network.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name network.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/network.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/network.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/school-network-access.log;
    error_log /var/log/nginx/school-network-error.log;

    # Client settings
    client_max_body_size 10M;
    client_body_timeout 60s;

    # Proxy to application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if any)
    location /static {
        alias /opt/school-network-backend/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API documentation
    location /api/docs {
        proxy_pass http://127.0.0.1:8000/api/docs;
        proxy_set_header Host $host;
    }

    # Health check endpoint (no auth required)
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

#### 3. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/school-network /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔒 SSL/TLS Configuration

### Using Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d network.yourdomain.com

# Auto-renewal test
sudo certbot renew --dry-run

# Certificate will auto-renew via systemd timer
sudo systemctl status certbot.timer
```

### Manual Certificate
```bash
# Place certificates
sudo mkdir -p /etc/ssl/school-network
sudo cp your-cert.crt /etc/ssl/school-network/
sudo cp your-key.key /etc/ssl/school-network/
sudo chmod 600 /etc/ssl/school-network/your-key.key

# Update nginx configuration to use these paths
```

---

## 💾 Database Migration

### Production Migration Strategy
```bash
# 1. Backup database before migration
pg_dump -U netmon school_network > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Test migration on staging
alembic upgrade head --sql > migration.sql
# Review migration.sql

# 3. Apply migration
alembic upgrade head

# 4. Verify
alembic current
psql -U netmon -d school_network -c "\dt"
```

### Rollback Procedure
```bash
# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Restore from backup if needed
psql -U netmon school_network < backup_20250117_120000.sql
```

---

## 📊 Monitoring Setup

### Application Monitoring

#### 1. Configure Logging
```bash
# Log rotation
sudo nano /etc/logrotate.d/school-network
```
```
/opt/school-network-backend/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    create 0640 netmon netmon
    sharedscripts
    postrotate
        systemctl reload school-network > /dev/null 2>&1 || true
    endscript
}
```

#### 2. Health Monitoring Script
```bash
cat > /opt/school-network-backend/scripts/health_check.sh << 'EOF'
#!/bin/bash

API_URL="http://localhost:8000"
ALERT_EMAIL="admin@yourdomain.com"

# Check health endpoint
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${API_URL}/health)

if [ "$RESPONSE" != "200" ]; then
    echo "API health check failed! Status: $RESPONSE" | \
        mail -s "School Network Monitor Alert" $ALERT_EMAIL
    exit 1
fi

# Check database
DB_STATUS=$(curl -s ${API_URL}/health/detailed | jq -r '.checks.database')

if [ "$DB_STATUS" != "healthy" ]; then
    echo "Database health check failed!" | \
        mail -s "School Network Monitor DB Alert" $ALERT_EMAIL
    exit 1
fi

echo "All health checks passed"
exit 0
EOF

chmod +x /opt/school-network-backend/scripts/health_check.sh
```

#### 3. Add Cron Job
```bash
crontab -e
```
```cron
# Health check every 5 minutes
*/5 * * * * /opt/school-network-backend/scripts/health_check.sh >> /var/log/school-network-health.log 2>&1
```

### System Monitoring
```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Check resource usage
htop
iotop
nethogs

# Check disk space
df -h

# Check memory
free -h

# Check database connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## 💾 Backup Strategy

### Automated Database Backup
```bash
cat > /opt/school-network-backend/scripts/backup_database.sh << 'EOF'
#!/bin/bash

# Configuration
BACKUP_DIR="/opt/backups/school-network"
DB_NAME="school_network"
DB_USER="netmon"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup filename with timestamp
BACKUP_FILE="$BACKUP_DIR/school_network_$(date +%Y%m%d_%H%M%S).sql.gz"

# Create backup
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup successful: $BACKUP_FILE"
    
    # Remove old backups
    find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
    
    echo "Old backups cleaned (retention: $RETENTION_DAYS days)"
else
    echo "Backup failed!"
    exit 1
fi

# Calculate backup size
ls -lh $BACKUP_FILE
EOF

chmod +x /opt/school-network-backend/scripts/backup_database.sh
```

### Schedule Backups
```bash
sudo crontab -e
```
```cron
# Daily backup at 2 AM
0 2 * * * /opt/school-network-backend/scripts/backup_database.sh >> /var/log/school-network-backup.log 2>&1

# Weekly full backup on Sunday at 3 AM
0 3 * * 0 /opt/school-network-backend/scripts/backup_database.sh >> /var/log/school-network-backup.log 2>&1
```

### Restore from Backup
```bash
# List available backups
ls -lh /opt/backups/school-network/

# Restore specific backup
gunzip < /opt/backups/school-network/school_network_20250117_020000.sql.gz | \
    psql -U netmon school_network

# Or restore latest
LATEST_BACKUP=$(ls -t /opt/backups/school-network/*.sql.gz | head -1)
gunzip < $LATEST_BACKUP | psql -U netmon school_network
```

---

## ⚡ Performance Tuning

### PostgreSQL Configuration
```bash
sudo nano /etc/postgresql/16/main/postgresql.conf
```
```ini
# Memory Settings
shared_buffers = 1GB                # 25% of RAM
effective_cache_size = 3GB          # 75% of RAM
work_mem = 16MB
maintenance_work_mem = 256MB

# Connections
max_connections = 100

# Query Planning
random_page_cost = 1.1              # For SSD
effective_io_concurrency = 200      # For SSD

# Write Ahead Log
wal_buffers = 16MB
checkpoint_completion_target = 0.9

# Logging
log_min_duration_statement = 1000   # Log slow queries (1 second)
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### Application Tuning

#### Uvicorn Workers

For production, set workers = (2 × CPU cores) + 1
```bash
# 4 CPU cores = 9 workers
uvicorn main:app --workers 9 --host 0.0.0.0 --port 8000
```

#### Connection Pool

In `database.py`:
```python
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=20,              # Increased for production
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False                 # Disable SQL logging in production
)
```

### System Limits
```bash
# Increase file descriptors
sudo nano /etc/security/limits.conf
```
```
netmon soft nofile 65536
netmon hard nofile 65536
```

### Nginx Tuning
```nginx
# Add to http block in /etc/nginx/nginx.conf
http {
    # Worker processes
    worker_processes auto;
    worker_connections 2048;

    # Buffers
    client_body_buffer_size 10K;
    client_header_buffer_size 1k;
    client_max_body_size 10M;
    large_client_header_buffers 2 1k;

    # Timeouts
    client_body_timeout 12;
    client_header_timeout 12;
    keepalive_timeout 15;
    send_timeout 10;

    # Compression
    gzip on;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
```

---

## 🔍 Verification Checklist

After deployment, verify:

- [ ] Application is running: `curl http://localhost:8000/health`
- [ ] Database is accessible: `curl http://localhost:8000/health/detailed`
- [ ] API documentation: `https://network.yourdomain.com/api/docs`
- [ ] SSL certificate is valid: `curl https://network.yourdomain.com/health`
- [ ] Logs are being written: `tail -f logs/app.log`
- [ ] Backups are working: `ls -lh /opt/backups/school-network/`
- [ ] Monitoring is active: `systemctl status school-network`
- [ ] Network discovery works: Test scan endpoint
- [ ] Events are being generated: Check events endpoint

---

## 📱 Post-Deployment

### Update DNS
```
A Record: network.yourdomain.com -> YOUR_SERVER_IP
```

### Configure Firewall
```bash
# UFW firewall
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable

# Check status
sudo ufw status
```

### Security Hardening
```bash
# Disable root SSH login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Restart SSH
sudo systemctl restart sshd

# Install fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

---

## 🆘 Troubleshooting Deployment

### Application Won't Start
```bash
# Check logs
sudo journalctl -u school-network -n 50

# Check if port is in use
sudo lsof -i :8000

# Verify Python environment
source venv/bin/activate
python --version
pip list | grep fastapi
```

### Database Connection Issues
```bash
# Test connection
psql -U netmon -d school_network -h localhost

# Check PostgreSQL is running
sudo systemctl status postgresql

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-16-main.log
```

### Nginx Issues
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Verify upstream is running
curl http://localhost:8000/health
```

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Administration](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**Deployment Guide Version:** 1.0  
**Last Updated:** January 17, 2025  
**For Support:** Contact your system administrator