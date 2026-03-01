# Email Notification Setup Guide

This guide explains how to configure email notifications for appointments, prescriptions, and reminders in the Healthcare Management Platform.

## Features

The email notification system includes:

1. **Appointment Notifications**:
   - Booking confirmation email (sent to patient when appointment is booked)
   - Status update email (sent when appointment status changes: confirmed, cancelled, completed, rejected)
   - Reminder email (automatically sent 24 hours before appointment)

2. **Prescription Notifications**:
   - New prescription email (sent to patient when doctor creates a prescription)

3. **Routine Check-up Reminders**:
   - Check-up reminder email (can be triggered for routine health check-ups)

## Prerequisites

Before setting up email notifications, ensure you have:

1. **Gmail Account** - You'll use Gmail's SMTP server to send emails
2. **Redis Server** - Required for Celery task queue (see installation below)
3. **Python 3.10+** - Already installed in your project

## Step 1: Generate Gmail App Password

Google requires an **App Password** for applications to send emails via SMTP (your regular Gmail password won't work).

### Instructions:

1. **Enable 2-Factor Authentication** on your Gmail account:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Under "How you sign in to Google", click "2-Step Verification"
   - Follow the setup instructions

2. **Generate App Password**:
   - Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
   - Or navigate: Google Account → Security → 2-Step Verification → App passwords
   - Select app: "Mail"
   - Select device: "Other (Custom name)" - enter "Healthcare App"
   - Click "Generate"
   - **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)
   - ⚠️ **IMPORTANT**: Save this password - you won't be able to see it again

## Step 2: Configure Environment Variables

1. **Create/Update `.env` file** in the `backend` directory:

```bash
cd backend
# If .env doesn't exist, copy from example
cp .env.example .env
```

2. **Edit `.env` file** and add your Gmail credentials:

```dotenv
# Email (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=abcdefghijklmnop  # Your 16-character App Password (no spaces)
EMAIL_FROM_NAME=Healthcare Platform
EMAIL_ENABLED=True
```

Replace:
- `your-email@gmail.com` with your actual Gmail address
- `abcdefghijklmnop` with your generated App Password (remove spaces)

### Example `.env` configuration:

```dotenv
# Email (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_FROM=healthcareapp@gmail.com
EMAIL_PASSWORD=xyzwabc123456789
EMAIL_FROM_NAME=Healthcare Platform
EMAIL_ENABLED=True

# Redis (Required for Celery)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

## Step 3: Install Redis

Redis is required for Celery (background task queue).

### Windows:

**Option 1: Using Memurai (Redis alternative for Windows)**
```powershell
# Download Memurai from https://www.memurai.com/
# Or use Chocolatey:
choco install memurai-developer

# Start Memurai service
memurai
```

**Option 2: Using WSL (Windows Subsystem for Linux)**
```bash
# In WSL terminal:
sudo apt update
sudo apt install redis-server
sudo service redis-server start

# Test Redis
redis-cli ping  # Should return "PONG"
```

**Option 3: Using Docker**
```powershell
docker run -d -p 6379:6379 --name redis redis:latest
```

### macOS:

```bash
# Install via Homebrew
brew install redis

# Start Redis
brew services start redis

# Test Redis
redis-cli ping  # Should return "PONG"
```

### Linux:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping  # Should return "PONG"
```

## Step 4: Install Python Dependencies

Ensure Celery and email dependencies are installed:

```bash
cd backend
pip install celery redis python-dotenv
# Or if using requirements.txt:
pip install -r requirements.txt
```

## Step 5: Start the Services

You need to run **3 separate terminals** for the full system:

### Terminal 1: Backend (FastAPI Server)

```bash
cd backend
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Start FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Celery Worker (Processes email tasks)

```bash
cd backend
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Start Celery worker
celery -A app.services.celery_tasks.celery_app worker --loglevel=info --pool=solo
```

**Windows Note**: Use `--pool=solo` or `--pool=threads` on Windows (gevent/eventlet not fully supported)

### Terminal 3: Celery Beat (Scheduler for appointment reminders)

```bash
cd backend
.venv\Scripts\activate
source .venv/bin/activate

# Start Celery Beat scheduler
celery -A app.services.celery_tasks.celery_app beat --loglevel=info
```

**Combined Command** (Worker + Beat in one terminal):
```bash
celery -A app.services.celery_tasks.celery_app worker --beat --loglevel=info --pool=solo
```

## Step 6: Test Email Notifications

### Test 1: Book an Appointment

1. Login as **patient** (patient@test.com / Test@123)
2. Search for a doctor and book an appointment
3. **Expected**: Patient receives booking confirmation email

### Test 2: Update Appointment Status

1. Login as **doctor** (doctor@test.com / Test@123) or **admin** (admin@healthcare.com / Admin@123)
2. Go to Appointments page
3. Update an appointment status to "confirmed" or "cancelled"
4. **Expected**: Patient receives status update email

### Test 3: Create Prescription

1. Login as **doctor** (doctor@test.com / Test@123)
2. Create a new prescription for a patient
3. **Expected**: Patient receives prescription notification email

### Test 4: Appointment Reminder (Scheduled)

1. Create an appointment for **tomorrow** (date = today + 1 day)
2. Set appointment status to "confirmed" or "booked"
3. Wait for Celery Beat to run (scheduled for 9 AM daily)
4. **Expected**: Patient receives reminder email 24 hours before appointment

**Manual Test** (trigger reminder immediately):
```python
# In Python terminal with backend environment
from app.services.celery_tasks import check_appointment_reminders
result = check_appointment_reminders()
print(result)
```

## Troubleshooting

### Issue 1: Email not sending

**Check Celery Worker logs:**
```
[2024-03-01 10:30:15,123: INFO/MainProcess] Task send_appointment_booking_email succeeded
```

**Common fixes:**
1. Verify Gmail credentials in `.env` (no typos, no spaces in app password)
2. Check Redis is running: `redis-cli ping`
3. Restart Celery worker after `.env` changes
4. Check `EMAIL_ENABLED=True` in `.env`

### Issue 2: "SMTP Authentication failed"

**Solution:**
- Verify 2FA is enabled on Gmail account
- Regenerate App Password (old one might be invalid)
- Remove spaces from App Password in `.env`
- Use the Gmail account email exactly as it is (case-sensitive)

### Issue 3: Redis connection error

**Error:** `kombu.exceptions.OperationalError: Error 10061 connecting to localhost:6379`

**Solution:**
- Start Redis server (see Step 3)
- Verify Redis is running: `redis-cli ping` should return "PONG"
- Check `REDIS_HOST` and `REDIS_PORT` in `.env`

### Issue 4: Celery worker not processing tasks

**Solution:**
```bash
# Stop existing worker
Ctrl+C

# Clear Redis queue
redis-cli FLUSHALL

# Restart Celery worker with verbose logging
celery -A app.services.celery_tasks.celery_app worker --loglevel=debug --pool=solo
```

### Issue 5: Appointments tomorrow but no reminder sent

**Check:**
1. Celery Beat is running (separate terminal or use `--beat` flag)
2. Beat schedule is loaded: Look for log message `[INFO/Beat] beat: Starting...`
3. Appointment status is 'confirmed' or 'booked' (not 'cancelled' or 'completed')
4. Appointment date is exactly tomorrow (not today or future dates)

**Manual trigger:**
```python
# Test the scheduled task manually
from app.services.celery_tasks import check_appointment_reminders
check_appointment_reminders.delay()
```

## Email Templates

The system sends beautifully formatted HTML emails with:

- **Booking Confirmation**: Blue-themed with appointment details (date, time, doctor)
- **Status Update**: Color-coded by status (green=confirmed, red=cancelled, purple=completed)
- **Reminder**: Yellow-themed warning with "tomorrow" emphasis
- **Prescription**: Green-themed with prescription details

### Customizing Email Templates

Edit the HTML templates in:
```
backend/app/services/email_service.py
```

Search for functions:
- `send_appointment_booking_notification()`
- `send_appointment_status_update()`
- `send_appointment_reminder()`
- `send_prescription_notification()`

## Scheduled Tasks

Current Celery Beat schedule:

| Task | Schedule | Description |
|------|----------|-------------|
| `check_appointment_reminders` | Daily at 9:00 AM UTC | Checks for appointments tomorrow and sends reminders |

**To modify schedule**, edit `backend/app/services/celery_tasks.py`:

```python
celery_app.conf.beat_schedule = {
    'check-appointment-reminders': {
        'task': 'check_appointment_reminders',
        'schedule': crontab(hour=9, minute=0),  # Change hour/minute here
    },
}
```

**Schedule examples:**
```python
# Every hour
'schedule': crontab(minute=0)

# Every day at 8 AM
'schedule': crontab(hour=8, minute=0)

# Every Monday at 9 AM
'schedule': crontab(hour=9, minute=0, day_of_week=1)

# Every 30 minutes
'schedule': crontab(minute='*/30')
```

## Production Deployment

For production, consider:

1. **Use Supervisor or systemd** to manage Celery processes
2. **Enable Redis persistence** (RDB or AOF)
3. **Set `EMAIL_ENABLED=True`** only in production
4. **Use environment-specific configs** (staging/production)
5. **Monitor Celery** with Flower:
   ```bash
   pip install flower
   celery -A app.services.celery_tasks.celery_app flower
   # Visit http://localhost:5555
   ```

6. **Log monitoring**: Check logs for failed email tasks
7. **Rate limiting**: Gmail has sending limits (500 recipients/day for free accounts)

## Disabling Email Notifications

To disable email notifications without removing code:

```dotenv
# In .env file
EMAIL_ENABLED=False
```

Emails will be skipped, but tasks will still log what would have been sent.

## Alternative Email Providers

To use a different SMTP provider (SendGrid, Mailgun, AWS SES):

1. Update SMTP settings in `.env`:
```dotenv
EMAIL_HOST=smtp.sendgrid.net  # or smtp.mailgun.org, email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_FROM=your-verified-sender@yourdomain.com
EMAIL_PASSWORD=your-provider-api-key
```

2. Verify the sender email with your provider
3. Restart backend and Celery worker

## Support

If you encounter issues:

1. Check Celery worker logs (Terminal 2)
2. Check Celery Beat logs (Terminal 3)
3. Verify all environment variables are set correctly
4. Test Redis connection independently
5. Test Gmail credentials using a simple Python script:

```python
import smtplib
from email.mime.text import MIMEText

msg = MIMEText("Test email")
msg['Subject'] = "Test"
msg['From'] = "your-email@gmail.com"
msg['To'] = "test@example.com"

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login("your-email@gmail.com", "your-app-password")
    server.send_message(msg)
print("Email sent successfully!")
```

---

## Summary Checklist

- [ ] Enable 2FA on Gmail account
- [ ] Generate Gmail App Password
- [ ] Update `.env` with Gmail credentials
- [ ] Install and start Redis server
- [ ] Install Python dependencies (celery, redis)
- [ ] Start FastAPI backend (Terminal 1)
- [ ] Start Celery worker (Terminal 2)
- [ ] Start Celery Beat scheduler (Terminal 3)
- [ ] Test appointment booking email
- [ ] Test appointment status update email
- [ ] Test prescription notification email
- [ ] Verify scheduled reminders work

**Congratulations!** Your email notification system is now configured. Patients will automatically receive emails for appointments, prescriptions, and reminders. 📧✅
