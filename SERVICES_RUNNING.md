# Email Notifications - Quick Reference

## ✅ What's Running Now

You have successfully started:

1. **Redis Server** - Running in background (port 6379)
2. **Backend API** - Running in separate window (http://localhost:8000)
3. **Celery Worker + Beat** - Running in separate window (processing email tasks)

## 📧 Gmail Configuration

Your email is configured with:
- **Email**: mazaemailghe@gmail.com  
- **Status**: EMAIL_ENABLED=True ✅
- **SMTP**: smtp.gmail.com:587

## 🧪 Test Email Notifications

### 1. Book an Appointment
- Login as **patient** (patient@test.com / Test@123)
- Search for a doctor
- Book appointment
- ✉️ **Patient receives booking confirmation email**

### 2. Update Appointment Status
- Login as **doctor** (doctor@test.com / Test@123) or **admin** (admin@healthcare.com / Admin@123)
- Go to Appointments
- Change status to "confirmed" or "cancelled"
- ✉️ **Patient receives status update email**

### 3. Create Prescription
- Login as **doctor** (doctor@test.com / Test@123)
- Create prescription for a patient
- ✉️ **Patient receives prescription notification**

### 4. Appointment Reminder (Automatic)
- Book appointment for **tomorrow**
- Set status to "confirmed" or "booked"
- ✉️ **Patient receives reminder at 9 AM (daily check)**

## 🔄 Daily Operations

### Starting Services (Next Time)

```powershell
cd backend
.\start-all-services.ps1
```

This will:
- Start Redis if not running
- Open Backend API window
- Open Celery Worker window

### Stopping Services

Close the PowerShell windows or press `Ctrl+C` in each window

### Checking Status

```powershell
# Check if Redis is running
Get-Process redis-server

# Check if backend is running
Get-Process python | Where-Object {(Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine -like "*uvicorn*"}

# Test Redis connection
redis\redis-cli.exe ping
# Should return: PONG
```

## 📝 Service Windows

You should see **3 windows** open:

1. **This window** - Main terminal
2. **Backend API window** - Shows FastAPI logs, API requests
3. **Celery Worker window** - Shows email task processing logs

## 🔍 Monitoring Email Tasks

In the **Celery Worker window**, you'll see logs like:

```
[INFO/MainProcess] Task send_appointment_booking_email[...] received
[INFO/ForkPoolWorker-1] Task send_appointment_booking_email[...] succeeded in 1.2s
```

This confirms emails are being sent.

## 📊 API Documentation

Visit: http://localhost:8000/docs

Try these endpoints:
- `POST /api/v1/appointments` - Book appointment (triggers email)
- `PATCH /api/v1/appointments/{id}/status` - Update status (triggers email)
- `POST /api/v1/prescriptions` - Create prescription (triggers email)

## ⚙️ Configuration Files

- **Email Config**: `backend/.env`
  ```dotenv
  EMAIL_HOST=smtp.gmail.com
  EMAIL_PORT=587
  EMAIL_FROM=mazaemailghe@gmail.com
  EMAIL_PASSWORD=***
  EMAIL_ENABLED=True
  ```

- **Redis Config**: `backend/.env`
  ```dotenv
  REDIS_HOST=localhost
  REDIS_PORT=6379
  CELERY_BROKER_URL=redis://localhost:6379/1
  ```

## 🛠️ Troubleshooting

### Email not sending?

1. **Check Celery Worker window** for errors
2. **Verify Gmail credentials** in `.env` file
3. **Check Gmail App Password** (16 characters, no spaces)
4. **Restart Celery Worker** (close window and run start script again)

### Redis connection error?

```powershell
# Stop existing Redis
Get-Process redis-server | Stop-Process

# Restart
cd backend
.\start-all-services.ps1
```

### Backend not responding?

1. Check Backend API window for errors
2. Restart: Close window and run start script again

## 📁 Important Files

- `backend/start-all-services.ps1` - Start everything
- `backend/install-redis-windows.ps1` - Reinstall Redis
- `backend/start-backend-only.ps1` - Backend without email (no Redis needed)
- `backend/.env` - Configuration

## 🎯 Next Steps

1. ✅ All services running
2. ✅ Email configured
3. 🧪 Test by booking an appointment
4. 📧 Check patient email inbox
5. 🎉 Email notification working!

## 📚 Full Documentation

- [EMAIL_NOTIFICATION_SETUP.md](../EMAIL_NOTIFICATION_SETUP.md) - Complete guide
- [EMAIL_QUICK_START.md](../EMAIL_QUICK_START.md) - Quick start
- [REDIS_WINDOWS_SETUP.md](../REDIS_WINDOWS_SETUP.md) - Redis alternatives

---

**Status: All systems operational! 🚀**

Test email notifications by booking an appointment now!
