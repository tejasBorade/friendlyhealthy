# Quick Start: Email Notifications

## 1. Setup Gmail (5 minutes)

1. Enable 2FA: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Copy the 16-character password

## 2. Configure .env

```bash
cd backend
notepad .env  # or use your editor
```

Add these lines:
```dotenv
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
EMAIL_FROM_NAME=Healthcare Platform
EMAIL_ENABLED=True

REDIS_HOST=localhost
REDIS_PORT=6379
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

## 3. Start Redis

**Windows (using Docker):**
```powershell
docker run -d -p 6379:6379 --name redis redis:latest
```

**Or download Memurai:** https://www.memurai.com/

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
```

## 4. Start Services (3 terminals)

### Terminal 1: Backend
```bash
cd backend
.venv\Scripts\activate  # Windows
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Celery Worker
```bash
cd backend
.venv\Scripts\activate
celery -A app.services.celery_tasks.celery_app worker --loglevel=info --pool=solo
```

### Terminal 3: Celery Beat (Scheduler)
```bash
cd backend
.venv\Scripts\activate
celery -A app.services.celery_tasks.celery_app beat --loglevel=info
```

**Or combine Worker + Beat in Terminal 2:**
```bash
celery -A app.services.celery_tasks.celery_app worker --beat --loglevel=info --pool=solo
```

## 5. Test

1. **Book appointment** → Patient receives confirmation email ✅
2. **Update status** → Patient receives status update email ✅
3. **Create prescription** → Patient receives prescription notification ✅
4. **Tomorrow's appointment** → Auto-reminder at 9 AM daily ⏰

## Troubleshooting

| Issue | Solution |
|-------|----------|
| SMTP Auth Error | Regenerate Gmail App Password, remove spaces |
| Redis Error | Start Redis: `redis-cli ping` should return "PONG" |
| No emails | Check Celery worker logs, verify EMAIL_ENABLED=True |
| Celery not starting | Add `--pool=solo` flag on Windows |

## Quick Test Command

```bash
# Test Redis connection
redis-cli ping

# Test email sending (in Python with .venv active)
python -c "from app.services.email_service import EmailService; print(EmailService.send_email('test@example.com', 'Test', '<h1>Hello</h1>'))"
```

---

📖 **Full documentation:** [EMAIL_NOTIFICATION_SETUP.md](EMAIL_NOTIFICATION_SETUP.md)
