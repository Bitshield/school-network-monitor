-- Initialize PostgreSQL database
-- This script runs on first container startup

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database if not exists (redundant but safe)
SELECT 'CREATE DATABASE school_network'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'school_network')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE school_network TO postgres;

-- Connect to database
\c school_network;

-- Create schemas if needed
-- CREATE SCHEMA IF NOT EXISTS app;

-- Add any initial data or configuration here
```

## 8. .dockerignore
```
# Git
.git
.gitignore
.gitattributes

# Python
__pycache__
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Virtual environments
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Documentation
docs/
*.md
!README.md

# Database
*.db
*.sqlite
*.sqlite3

# Environment
.env
.env.*

# Docker
docker-compose*.yml
Dockerfile*
.dockerignore

# CI/CD
.github/
.gitlab-ci.yml

# Temporary files
tmp/
temp/
*.tmp
*.bak

# OS
.DS_Store
Thumbs.db