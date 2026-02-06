# Healthcare Management Platform - Setup & Deployment Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Quick Start (Docker)](#quick-start-docker)
3. [Local Development Setup](#local-development-setup)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [API Testing](#api-testing)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: 8 GB
- **Storage**: 10 GB free space
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### For Local Development (without Docker)
- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **PostgreSQL**: 15 or higher
- **Redis**: 7 or higher

---

## Quick Start (Docker)

The fastest way to get the entire platform running:

### 1. Clone the Repository
```bash
git clone <repository-url>
cd friendlyhealthy
```

### 2. Create Environment File
```bash
cd backend
copy .env.example .env
# Edit .env and update the SECRET_KEY
```

**Important**: Change the `SECRET_KEY` to a strong random string:
```bash
# Generate a secure secret key (on Linux/Mac)
openssl rand -hex 32

# On Windows PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

### 3. Start All Services
```bash
cd ..
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- Backend API (port 8000)
- Frontend app (port 3000)
- Celery worker

### 4. Verify Services
```bash
# Check all containers are running
docker-compose ps

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### 6. Stop Services
```bash
docker-compose down

# To also remove volumes (database data)
docker-compose down -v
```

---

## Local Development Setup

For development without Docker:

### Backend Setup

#### 1. Install Python Dependencies
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

#### 2. Set Up PostgreSQL
```powershell
# Install PostgreSQL (if not installed)
# Download from: https://www.postgresql.org/download/

# Create database
psql -U postgres
CREATE DATABASE healthcare_db;
\q

# Run schema
psql -U postgres -d healthcare_db -f ../DATABASE_SCHEMA.sql
```

#### 3. Set Up Redis
```powershell
# Install Redis on Windows using WSL or download from:
# https://github.com/microsoftarchive/redis/releases

# Or use Docker
docker run -d -p 6379:6379 redis:7-alpine
```

#### 4. Configure Environment
```bash
# Copy and edit .env file
copy .env.example .env

# Update these values in .env:
# DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/healthcare_db
# REDIS_HOST=localhost
# SECRET_KEY=your-generated-secret-key
```

#### 5. Run Backend
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with specific Python
python -m uvicorn app.main:app --reload
```

### Frontend Setup

#### 1. Install Node.js Dependencies
```bash
cd frontend
npm install
```

#### 2. Configure Environment
```bash
# Create .env file
echo VITE_API_URL=http://localhost:8000/api/v1 > .env
```

#### 3. Run Frontend
```bash
npm run dev
```

The application will be available at http://localhost:3000

---

## Database Setup

### Initialize Database
```bash
# Using psql
psql -U postgres -d healthcare_db -f DATABASE_SCHEMA.sql

# Or from Docker
docker exec -i healthcare_db psql -U postgres -d healthcare_db < DATABASE_SCHEMA.sql
```

### Verify Tables
```sql
-- Connect to database
psql -U postgres -d healthcare_db

-- List all tables
\dt

-- Check specializations data
SELECT * FROM specializations;

-- Check charge types
SELECT * FROM charge_types;
```

### Create Admin User (Optional)
```sql
-- Insert admin user
INSERT INTO users (email, password_hash, role, is_active, is_verified)
VALUES (
    'admin@healthcare.com',
    -- Use the hash_password function from your app or bcrypt
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaOBYeu', -- 'admin123'
    'admin',
    TRUE,
    TRUE
);
```

---

## Running the Application

### Development Mode

**Terminal 1 - Backend**
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Celery Worker (for background tasks)**
```bash
cd backend
venv\Scripts\activate
celery -A app.celery_app worker --loglevel=info
```

### Using Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart a specific service
docker-compose restart backend

# Stop all services
docker-compose down
```

---

## API Testing

### Using Swagger UI
1. Open http://localhost:8000/api/docs
2. Click "Authorize" button
3. Register a new user or login
4. Copy the access_token
5. Paste in Authorization field: `Bearer <access_token>`
6. Test endpoints

### Using cURL

**Register a User**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "SecurePass123!",
    "role": "patient"
  }'
```

**Login**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "SecurePass123!"
  }'
```

**Get Doctors (with authentication)**
```bash
curl -X GET "http://localhost:8000/api/v1/doctors/search" \
  -H "Authorization: Bearer <your_access_token>"
```

### Using Postman
1. Import the API collection (if available)
2. Set environment variable `base_url` = `http://localhost:8000/api/v1`
3. Set `access_token` after login
4. Use `{{base_url}}` and `{{access_token}}` in requests

---

## Production Deployment

### Prerequisites
- Linux server (Ubuntu 20.04+ recommended)
- Domain name (optional)
- SSL certificate (Let's Encrypt recommended)

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone and Configure
```bash
# Clone repository
git clone <repository-url>
cd friendlyhealthy

# Configure production environment
cd backend
cp .env.example .env
nano .env
```

**Update these production settings**:
```env
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql+asyncpg://postgres:<strong-password>@db:5432/healthcare_db
CORS_ORIGINS=["https://yourdomain.com"]
```

### 3. Deploy with Docker
```bash
# Build and start
docker-compose -f docker-compose.yml up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Set Up Nginx (Optional - for SSL)
```bash
sudo apt install nginx certbot python3-certbot-nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/healthcare
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/healthcare /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

### 5. Database Backup
```bash
# Manual backup
docker exec healthcare_db pg_dump -U postgres healthcare_db > backup_$(date +%Y%m%d).sql

# Automated daily backups (cron)
crontab -e

# Add this line for daily 2 AM backup
0 2 * * * docker exec healthcare_db pg_dump -U postgres healthcare_db > /backups/db_$(date +\%Y\%m\%d).sql
```

### 6. Monitoring
```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check resource usage
docker stats
```

---

## Troubleshooting

### Backend Issues

**Issue: Database connection fails**
```bash
# Check database is running
docker-compose ps db

# Check connection
docker exec healthcare_db psql -U postgres -d healthcare_db -c "SELECT 1"

# Check environment variables
docker exec healthcare_backend env | grep DATABASE_URL
```

**Issue: Import errors**
```bash
# Reinstall dependencies
cd backend
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

**Issue: Port already in use**
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Kill the process or change port in docker-compose.yml
```

### Frontend Issues

**Issue: Cannot connect to backend**
```bash
# Check VITE_API_URL in .env
cat frontend/.env

# Check backend is running
curl http://localhost:8000/health

# Check browser console for CORS errors
```

**Issue: Build fails**
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear cache
npm cache clean --force
```

### Docker Issues

**Issue: Container won't start**
```bash
# Check logs
docker-compose logs backend
docker-compose logs db

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Remove and recreate volumes
docker-compose down -v
docker-compose up -d
```

**Issue: Permission denied**
```bash
# Linux: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo
sudo docker-compose up -d
```

### Database Issues

**Issue: Tables not created**
```bash
# Manually run schema
docker exec -i healthcare_db psql -U postgres -d healthcare_db < DATABASE_SCHEMA.sql

# Check if tables exist
docker exec healthcare_db psql -U postgres -d healthcare_db -c "\dt"
```

**Issue: Connection pool exhausted**
```env
# Increase pool size in .env
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=10
```

---

## Getting Help

- Check the [README.md](README.md) for general information
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Check API documentation at http://localhost:8000/api/docs
- Review logs: `docker-compose logs -f`
- Open an issue on GitHub

---

## Next Steps

After setup:
1. Create initial admin user
2. Add specializations (already in schema)
3. Register doctors
4. Configure email/SMS providers (Twilio, SendGrid)
5. Set up monitoring (Prometheus, Grafana)
6. Configure backups
7. Set up CI/CD pipeline

---

**Last Updated**: February 2026
