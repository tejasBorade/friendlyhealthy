# Redis Setup for Windows (No Docker Required)

Since you don't have Docker installed, here are **3 easy ways** to run Redis on Windows:

## Option 1: Download Redis for Windows (Easiest)

### Automated Installation:

```powershell
cd backend
.\install-redis-windows.ps1
```

This script will:
1. Download Redis for Windows (5.0.14.1)
2. Extract it to `backend/redis` folder
3. Create `start-redis.ps1` script

Then start Redis:
```powershell
cd backend
.\start-redis.ps1
```

### Manual Installation:

1. **Download Redis for Windows**:
   - Visit: https://github.com/tporadowski/redis/releases
   - Download: `Redis-x64-5.0.14.1.zip`
   - Extract to: `backend/redis`

2. **Start Redis**:
   ```powershell
   cd backend\redis
   .\redis-server.exe
   ```

3. **Test Redis** (in another terminal):
   ```powershell
   cd backend\redis
   .\redis-cli.exe ping
   # Should return: PONG
   ```

---

## Option 2: Install Memurai (Professional Redis for Windows)

Memurai is a Redis-compatible server built for Windows.

### Using Installer:

1. Download from: https://www.memurai.com/get-memurai
2. Run the installer
3. Memurai starts automatically as a Windows service

### Using Chocolatey:

```powershell
# Install Chocolatey first (if not installed):
# See: https://chocolatey.org/install

# Then install Memurai:
choco install memurai-developer

# Start Memurai:
memurai
```

**Test:**
```powershell
redis-cli ping  # Should return: PONG
```

---

## Option 3: Use WSL (Windows Subsystem for Linux)

### Install WSL:

```powershell
# In PowerShell (as Administrator):
wsl --install
```

Restart your computer.

### Install Redis in WSL:

```bash
# Open WSL terminal
wsl

# Update packages
sudo apt update

# Install Redis
sudo apt install redis-server -y

# Start Redis
sudo service redis-server start

# Test
redis-cli ping  # Should return: PONG
```

**Keep WSL running** while using the application.

---

## Option 4: Run Backend Without Redis (Quick Test)

If you just want to test the backend immediately without email notifications:

```powershell
cd backend
.\start-backend-only.ps1
```

This starts only the FastAPI backend. Emails won't be sent, but the API will work.

**To enable emails later**:
1. Install Redis (any option above)
2. Start Celery worker:
   ```powershell
   cd backend
   celery -A app.services.celery_tasks.celery_app worker --loglevel=info --pool=solo
   ```

---

## Recommended Setup

**For development on Windows (no Docker):**

1. **Install Memurai** (easiest, professional): ⭐ RECOMMENDED
   ```powershell
   # Download from https://www.memurai.com/get-memurai
   # Install and it runs as a service
   ```

2. **Or use automated script**:
   ```powershell
   cd backend
   .\install-redis-windows.ps1
   .\start-redis.ps1
   ```

3. **Start backend**:
   ```powershell
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

4. **Start Celery** (in separate terminal):
   ```powershell
   cd backend
   celery -A app.services.celery_tasks.celery_app worker --beat --loglevel=info --pool=solo
   ```

---

## Verification

After starting Redis, verify it's running:

```powershell
# Test connection
redis-cli ping

# Should return:
# PONG

# Check if port 6379 is listening
netstat -an | findstr "6379"

# Should show:
# TCP    0.0.0.0:6379    0.0.0.0:0    LISTENING
```

---

## Troubleshooting

### Redis won't start

**Error:** "Creating Server TCP listening socket *:6379: bind: No error"

**Solution:** Port 6379 is already in use
```powershell
# Find process using port 6379
netstat -ano | findstr "6379"

# Kill the process (replace PID with actual number)
taskkill /PID 12345 /F
```

### Can't download Redis

**Solution:** Use Memurai instead (Option 2)

### WSL not working

**Solution:** Requires Windows 10 version 2004+ or Windows 11
- Check: `winver` in Run dialog
- Update Windows if needed

---

## Next Steps

Once Redis is running:

1. ✅ Configure Gmail credentials in `.env`
2. ✅ Start backend
3. ✅ Start Celery worker
4. ✅ Test email notifications

See [EMAIL_QUICK_START.md](../EMAIL_QUICK_START.md) for email setup.

---

## Quick Commands Cheat Sheet

```powershell
# Start Redis (Option 1 - Downloaded)
cd backend\redis
.\redis-server.exe

# Start Redis (Option 2 - Memurai)
memurai

# Start Redis (Option 3 - WSL)
wsl sudo service redis-server start

# Test Redis
redis-cli ping

# Start Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Start Celery Worker + Beat
cd backend
celery -A app.services.celery_tasks.celery_app worker --beat --loglevel=info --pool=solo

# Check Redis status
redis-cli info server
```

---

That's it! Choose the option that works best for you. **Memurai** is recommended for Windows users. 🚀
