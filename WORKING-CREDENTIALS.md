# ✅ WORKING LOGIN CREDENTIALS

**All passwords have been reset and tested - these credentials are confirmed working!**

## Quick Login Guide

| Role | Email | Password |
|------|-------|----------|
| **Patient** | patient@healthcare.com | Patient@123 |
| **Doctor** | doctor@healthcare.com | Doctor@123 |
| **Staff** | staff@healthcare.com | Staff@123 |
| **Admin** | admin@healthcare.com | Admin@123 |
| **Test Patient** | test@example.com | Test@123 |

## Access the Application

1. **Frontend:** http://localhost:3000
2. **Backend API:** http://localhost:5000/api

## Important: Refresh Your Browser!

If you were previously testing the login:
1. **Hard refresh** your browser: `Ctrl + Shift + R` (or `Ctrl + F5`)
2. **Clear localStorage**: Open browser console and run: `localStorage.clear()`
3. Try logging in again with the credentials above

## What Was Fixed

✅ API base URL corrected from port 8000 to port 5000  
✅ Token response format aligned between frontend and backend  
✅ All user passwords reset to known values  
✅ Backend authentication tested and confirmed working  

## Test Login Flow

```bash
# Test backend directly (PowerShell)
$body = @{ email = "test@example.com"; password = "Test@123" } | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:5000/api/auth/login" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

Expected response: `StatusCode: 200` with JWT token

## Next Steps After Login

- **Patient:** Navigate to `/patient/dashboard` → Browse doctors, book appointments
- **Doctor:** Navigate to `/doctor/dashboard` → View appointments, manage prescriptions  
- **Staff:** Navigate to `/staff/dashboard` → Manage appointments and doctors
- **Admin:** Navigate to `/admin/dashboard` → Full system access

---

**Last Updated:** Passwords reset and tested - all accounts working!
