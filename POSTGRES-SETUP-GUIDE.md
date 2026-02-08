# PostgreSQL Setup for Healthcare Platform

## Step 1: PostgreSQL Installation Settings

During installation, use these settings:

1. **Port**: `5432` (default - keep this)
2. **Superuser (postgres) Password**: Choose a password and REMEMBER IT!
   - Example: `postgres` or `admin123`
   - Write it down - you'll need it!
3. **Locale**: Default (English, United States)
4. **Components**: Install all (PostgreSQL Server, pgAdmin, Command Line Tools)

Click "Next" through the rest and finish installation.

---

## Step 2: Open pgAdmin

After installation:

1. Look for **pgAdmin 4** in Start Menu → Open it
2. First time opening? It will ask for a **Master Password** → Set any password (this is just for pgAdmin, not PostgreSQL)
3. On the left panel, you'll see **Servers** → Click the arrow to expand
4. Click on **PostgreSQL [version number]**
5. Enter the **postgres password** you set during installation

---

## Step 3: Create the Database

In pgAdmin:

1. **Right-click** on **"Databases"** (in the left tree)
2. Select **"Create"** → **"Database..."**
3. In the dialog:
   - **Database name**: `healthcare_db`
   - **Owner**: `postgres` (should be default)
4. Click **"Save"**

You should now see `healthcare_db` under Databases!

---

## Step 4: Load the Database Schema

In pgAdmin:

1. **Click** on `healthcare_db` in the left tree (to select it)
2. Click **"Tools"** menu at the top → Select **"Query Tool"**
3. A new query window opens
4. Click the **folder icon** (📁) "Open File" at the top
5. Navigate to and select:
   ```
   c:\Users\tejas\friendlyhealthy\friendlyhealthy\server\database\schema.sql
   ```
6. Click **"Open"**
7. Click the **▶️ Play button** (or press F5) to execute
8. You should see: **"Query returned successfully"**

---

## Step 5: Verify Tables Were Created

In pgAdmin:

1. Expand `healthcare_db` in the left tree
2. Expand **"Schemas"** → **"public"** → **"Tables"**
3. You should see these tables:
   - ✅ users
   - ✅ patients
   - ✅ doctors
   - ✅ appointments
   - ✅ medical_records
   - ✅ prescriptions

If you see all 6 tables, SUCCESS! ✅

---

## Step 6: Configure the Application

### A. Update Backend Configuration

1. Open this file in VS Code:
   ```
   c:\Users\tejas\friendlyhealthy\friendlyhealthy\server\.env
   ```

2. Update the **DB_PASSWORD** line with YOUR password:
   ```
   DB_PASSWORD=your_password_here
   ```
   
   Replace `your_password_here` with the password you set during installation.

3. **Save the file** (Ctrl+S)

Example `.env` file:
```env
PORT=5000
NODE_ENV=development

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=postgres    ← CHANGE THIS TO YOUR PASSWORD!

# JWT Secret
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRE=7d
```

---

## Step 7: Test Database Connection

Open PowerShell and test:

```powershell
cd c:\Users\tejas\friendlyhealthy\friendlyhealthy\server
npm start
```

**Expected output:**
```
✅ Database connected successfully
🚀 Server running on http://localhost:5000
```

**If you see errors:**
- ❌ "password authentication failed" → Wrong password in .env
- ❌ "database does not exist" → Database not created (go back to Step 3)
- ❌ "connect ECONNREFUSED" → PostgreSQL service not running

---

## Step 8: Start the Full Application

Once backend starts successfully, stop it (Ctrl+C) and run:

```powershell
cd c:\Users\tejas\friendlyhealthy\friendlyhealthy
.\run-app.ps1
```

This will:
1. ✅ Start backend on http://localhost:5000
2. ✅ Start frontend on http://localhost:3000
3. ✅ Open browser automatically

---

## 🎯 Quick Reference

### Database Credentials (default):
- **Host**: localhost
- **Port**: 5432
- **Database**: healthcare_db
- **User**: postgres
- **Password**: [what you set during installation]

### Connection String Format:
```
postgresql://postgres:your_password@localhost:5432/healthcare_db
```

### Check if PostgreSQL is Running:
```powershell
Get-Service -Name "postgresql*"
```

### Start PostgreSQL Service:
```powershell
Start-Service -Name "postgresql-x64-[version]"
```

### Stop PostgreSQL Service:
```powershell
Stop-Service -Name "postgresql-x64-[version]"
```

---

## 🐛 Troubleshooting

### Problem: "Could not connect to server"
**Solution:**
1. Open Services: Press `Win+R`, type `services.msc`, press Enter
2. Find service starting with "postgresql"
3. Right-click → Start
4. Status should show "Running"

### Problem: "password authentication failed"
**Solution:**
1. Double-check password in `server\.env`
2. Make sure it matches what you set during installation
3. No spaces before or after the password

### Problem: pgAdmin asks for password every time
**Solution:**
1. In pgAdmin, right-click on PostgreSQL server
2. Select "Properties"
3. Go to "Connection" tab
4. Check "Save password"
5. Click "Save"

### Problem: Tables not showing in pgAdmin
**Solution:**
1. Right-click on "Tables" in left tree
2. Select "Refresh"
3. If still empty, re-run the schema.sql (Step 4)

---

## ✅ Verification Checklist

Before starting the app, verify:

- [ ] PostgreSQL installed and running
- [ ] pgAdmin opens without errors
- [ ] Database `healthcare_db` created
- [ ] 6 tables visible in pgAdmin
- [ ] Password updated in `server\.env`
- [ ] Backend dependencies installed (`npm install` in server folder)
- [ ] Frontend dependencies installed (`npm install` in frontend folder)

---

## 🚀 Ready to Start!

Once all steps are complete:

```powershell
cd c:\Users\tejas\friendlyhealthy\friendlyhealthy
.\run-app.ps1
```

Browser will open to http://localhost:3000

**First time?** Click "Register" and create your account!

---

Need help with any step? Let me know which step you're on and what error you're seeing!
