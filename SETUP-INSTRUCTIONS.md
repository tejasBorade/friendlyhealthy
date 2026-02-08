# 🏥 Healthcare Management Platform - Complete Setup Guide

## ✅ What I've Built For You

A **complete healthcare management system** with:
- ✨ **Backend**: Node.js + Express + PostgreSQL
- 🎨 **Frontend**: React 18 + Vite + Material-UI
- 🔐 **Authentication**: JWT-based secure login
- 📊 **Features**: Patient/Doctor management, Appointments, Medical Records

---

## 📋 Prerequisites You Need

### 1. **Node.js** (Already Installed ✅)
You have this already!

### 2. **PostgreSQL Database** ⬇️ **Need to Install**

**Download PostgreSQL:**
1. Go to: https://www.postgresql.org/download/windows/
2. Download the Windows installer (latest version)
3. Run the installer
4. **IMPORTANT**: Remember the password you set for 'postgres' user!
5. Keep default port: 5432
6. Click Next through the rest

After installation, PostgreSQL will start automatically.

---

## 🚀 Installation Steps

### Step 1: Update Database Password

Open this file: `server/.env`

Change this line if your PostgreSQL password is different:
```
DB_PASSWORD=postgres
```

Replace `postgres` with YOUR password you set during PostgreSQL installation.

### Step 2: Create Database

**Option A: Using pgAdmin (Easiest)**
1. Open **pgAdmin** (installed with PostgreSQL)
2. Enter your PostgreSQL password
3. Right-click on "Databases" → "Create" → "Database"
4. Name it: `healthcare_db`
5. Click "Save"

**Option B: Using Command Line**
```powershell
# Open PowerShell as Administrator
psql -U postgres

# Enter your password, then type:
CREATE DATABASE healthcare_db;
\q
```

### Step 3: Run Database Schema

**Option A: Using pgAdmin**
1. In pgAdmin, click on `healthcare_db`
2. Click "Tools" → "Query Tool"
3. Click "Open File" icon
4. Select: `c:\Users\tejas\friendlyhealthy\friendlyhealthy\server\database\schema.sql`
5. Click the "Play" button (▶️) to execute

**Option B: Using Command Line**
```powershell
psql -U postgres -d healthcare_db -f "c:\Users\tejas\friendlyhealthy\friendlyhealthy\server\database\schema.sql"
```

### Step 4: Start the Application

```powershell
cd c:\Users\tejas\friendlyhealthy\friendlyhealthy
.\run-app.ps1
```

This will:
- ✅ Start the backend on http://localhost:5000
- ✅ Start the frontend on http://localhost:3000
- ✅ Open your browser automatically

---

## 🎯 Using the Application

### First Time Setup:
1. Click **"Register"**
2. Fill in details:
   - Email: your@email.com
   - Password: Test@123 (must have uppercase, lowercase, number, special char)
   - First Name: Your Name
   - Last Name: Your Last Name
   - Role: Choose Patient or Doctor
   - Phone: Optional
3. Click **Register**
4. You'll be logged in automatically!

### Features Available:
- 👤 **Patient Dashboard**: View appointments, medical records
- 👨‍⚕️ **Doctor Search**: Find doctors by specialization
- 📅 **Appointments**: Book and manage appointments
- 📋 **Medical History**: View patient records
- 💊 **Prescriptions**: Manage medications

---

## 🐛 Troubleshooting

### "Cannot connect to database"
❌ **Problem**: PostgreSQL not running
✅ **Solution**:
1. Open "Services" (press Win+R, type `services.msc`)
2. Find "postgresql" service
3. Right-click → Start

### "Port 5000 already in use"
❌ **Problem**: Another app using port 5000
✅ **Solution**:
```powershell
# Find and kill the process
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process -Force
```

### "Module not found"
❌ **Problem**: Dependencies not installed
✅ **Solution**:
```powershell
cd server
npm install

cd ../frontend
npm install
```

---

## 📁 Project Structure

```
friendlyhealthy/
├── server/                 # Node.js Backend
│   ├── config/            # Database configuration
│   ├── database/          # SQL schema
│   ├── middleware/        # Authentication
│   ├── routes/            # API endpoints
│   ├── .env              # Configuration (UPDATE THIS!)
│   ├── package.json       # Dependencies
│   └── server.js          # Main server file
│
├── frontend/              # React Frontend
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API calls
│   │   └── store/        # State management
│   ├── .env.local        # Frontend config
│   └── package.json       # Dependencies
│
└── run-app.ps1           # Start script (USE THIS!)
```

---

## 🌐 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Doctors
- `GET /api/doctors` - List all doctors
- `GET /api/doctors/:id` - Get doctor details

### Appointments  
- `GET /api/appointments` - List appointments
- `POST /api/appointments` - Create appointment
- `PATCH /api/appointments/:id` - Update appointment
- `DELETE /api/appointments/:id` - Cancel appointment

---

## 💡 Quick Test

After setup, test the backend:

1. Open browser: http://localhost:5000/health
2. You should see: `{"status":"healthy"}`

If you see this, backend is working! ✅

---

## 📞 Next Steps

1. **Install PostgreSQL** (if not installed)
2. **Create database** using pgAdmin or command line
3. **Run schema** from `server/database/schema.sql`
4. **Update** `server/.env` with your PostgreSQL password
5. **Run** `.\run-app.ps1`
6. **Register** your first account
7. **Start using** the application!

---

## 🎉 Success!

When you see:
```
✅ Backend running on http://localhost:5000
✅ Frontend running on http://localhost:3000
```

You're all set! The browser will open automatically.

**First login**: Use the email/password you registered with.

---

Need help? Check the troubleshooting section above or let me know what error you're seeing!
