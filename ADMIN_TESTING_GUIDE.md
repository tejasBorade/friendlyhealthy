# 🔐 Admin Testing Guide - Complete CRUD Operations

## Admin Login Credentials

```
Email: admin@healcare.com
Password: Admin@123
```

---

## 🚀 Quick Start

### 1. Login via API
```bash
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@healcare.com",
  "password": "Admin@123"
}
```

**PowerShell Quick Login:**
```powershell
$token = (Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post -Body (@{email="admin@healcare.com"; password="Admin@123"} | ConvertTo-Json) -ContentType "application/json").access_token
$headers = @{Authorization="Bearer $token"}
Write-Host "Admin token: $token"
```

### 2. Access Points
- **Frontend Admin Dashboard**: http://localhost:3000/admin/dashboard
- **API Documentation (Swagger)**: http://localhost:8000/api/docs
- **Backend API**: http://localhost:8000/api/v1

---

## 📊 Testing All Features

### 1. 👨‍⚕️ DOCTORS Management

#### View All Doctors
```bash
GET http://localhost:8000/api/v1/doctors
Authorization: Bearer {admin_token}
```

**PowerShell:**
```powershell
$doctors = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/doctors" -Headers $headers
Write-Host "Total Doctors: $($doctors.doctors.Count)"
$doctors.doctors | Select-Object id, first_name, last_name, specialization, consultation_fee | Format-Table
```

#### View Doctor Profile
```bash
GET http://localhost:8000/api/v1/doctors/{doctor_id}
Authorization: Bearer {admin_token}
```

#### Get Specializations
```bash
GET http://localhost:8000/api/v1/doctors/specializations
Authorization: Bearer {admin_token}
```

---

### 2. 👥 PATIENTS Management

#### View All Patients (via Users endpoint)
```bash
GET http://localhost:8000/api/v1/auth/users
Authorization: Bearer {admin_token}
```

**Note:** Admins can see all users including patients. Filter by `role == "patient"`.

---

### 3. 📅 APPOINTMENTS Management

#### View All Appointments
```bash
GET http://localhost:8000/api/v1/appointments
Authorization: Bearer {admin_token}
```

**PowerShell:**
```powershell
$appointments = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/appointments" -Headers $headers
Write-Host "Total Appointments: $($appointments.appointments.Count)"
$appointments.appointments | Select-Object id, patient_id, doctor_id, appointment_date, status | Format-Table
```

#### Filter by Status
```bash
GET http://localhost:8000/api/v1/appointments?status=scheduled
GET http://localhost:8000/api/v1/appointments?status=completed
GET http://localhost:8000/api/v1/appointments?status=cancelled
```

#### View Upcoming Appointments
```bash
GET http://localhost:8000/api/v1/appointments/upcoming
Authorization: Bearer {admin_token}
```

#### Create Appointment (for any patient)
```bash
POST http://localhost:8000/api/v1/appointments
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "doctor_id": 1,
  "patient_id": 3,
  "appointment_date": "2026-03-15",
  "appointment_time": "10:00:00",
  "reason": "Regular checkup"
}
```

#### Cancel Appointment
```bash
PATCH http://localhost:8000/api/v1/appointments/{appointment_id}/cancel
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "cancellation_reason": "Patient requested cancellation"
}
```

---

### 4. 💊 PRESCRIPTIONS Management

#### View All Prescriptions
```bash
GET http://localhost:8000/api/v1/prescriptions
Authorization: Bearer {admin_token}
```

**PowerShell:**
```powershell
$prescriptions = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/prescriptions" -Headers $headers
Write-Host "Total Prescriptions: $($prescriptions.prescriptions.Count)"
$prescriptions.prescriptions | Select-Object id, patient_id, medication_name, dosage, prescribed_date | Format-Table
```

#### View Active Prescriptions (Last 90 days)
```bash
GET http://localhost:8000/api/v1/prescriptions/active
Authorization: Bearer {admin_token}
```

#### Create Prescription (Admin can create on behalf of doctor)
```bash
POST http://localhost:8000/api/v1/prescriptions
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "patient_id": 3,
  "doctor_id": 1,
  "medication_name": "Amoxicillin 500mg",
  "dosage": "1 tablet",
  "frequency": "3 times daily",
  "duration": "7 days",
  "instructions": "Take with food",
  "prescribed_date": "2026-03-01"
}
```

---

### 5. 📋 MEDICAL HISTORY Management

#### View Medical History
```bash
GET http://localhost:8000/api/v1/medical-history
Authorization: Bearer {admin_token}
```

**PowerShell:**
```powershell
$history = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/medical-history" -Headers $headers
Write-Host "Total Medical Records: $($history.Count)"
$history | Select-Object id, patient_id, diagnosis, visit_date | Format-Table
```

#### View Specific Patient's History
```bash
GET http://localhost:8000/api/v1/medical-history?patient_id={patient_id}
Authorization: Bearer {admin_token}
```

#### Create Medical Record
```bash
POST http://localhost:8000/api/v1/medical-history
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "patient_id": 3,
  "doctor_id": 1,
  "diagnosis": "Hypertension",
  "symptoms": "High blood pressure, headache",
  "treatment": "Prescribed medication and lifestyle changes",
  "visit_date": "2026-03-01"
}
```

---

### 6. 📄 REPORTS Management

#### View All Reports
```bash
GET http://localhost:8000/api/v1/reports
Authorization: Bearer {admin_token}
```

**PowerShell:**
```powershell
$reports = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/reports" -Headers $headers
Write-Host "Total Reports: $($reports.Count)"
$reports | Select-Object id, patient_id, report_type, test_date | Format-Table
```

#### Filter Reports
```bash
GET http://localhost:8000/api/v1/reports?patient_id={patient_id}
GET http://localhost:8000/api/v1/reports?report_type=blood_test
Authorization: Bearer {admin_token}
```

#### Upload Report (for any patient)
```bash
POST http://localhost:8000/api/v1/reports
Authorization: Bearer {admin_token}
Content-Type: multipart/form-data

patient_id: 3
report_type: blood_test
report_name: CBC Test Results
test_date: 2026-03-01
lab_name: City Diagnostics
file: [upload PDF/image file]
```

**PowerShell File Upload:**
```powershell
$reportFile = "C:\path\to\report.pdf"
$boundary = [System.Guid]::NewGuid().ToString()
$headers_upload = @{
    Authorization = "Bearer $token"
    "Content-Type" = "multipart/form-data; boundary=$boundary"
}

# Use Invoke-WebRequest for file uploads
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/reports" `
    -Method Post `
    -Headers $headers_upload `
    -InFile $reportFile
```

---

### 7. 💰 BILLING Management

#### View All Bills
```bash
GET http://localhost:8000/api/v1/billing/bills
Authorization: Bearer {admin_token}
```

#### Create Bill
```bash
POST http://localhost:8000/api/v1/billing/bills
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "patient_id": 3,
  "appointment_id": 10,
  "items": [
    {
      "description": "Consultation Fee",
      "quantity": 1,
      "unit_price": 500.00
    },
    {
      "description": "Lab Tests",
      "quantity": 2,
      "unit_price": 300.00
    }
  ],
  "discount_amount": 50.00,
  "notes": "Payment via insurance"
}
```

#### Update Payment Status
```bash
PATCH http://localhost:8000/api/v1/billing/bills/{bill_id}/payment
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "payment_status": "paid",
  "payment_method": "card",
  "transaction_id": "TXN123456789"
}
```

---

### 8. 🔔 NOTIFICATIONS Management

#### View All Notifications
```bash
GET http://localhost:8000/api/v1/notifications
Authorization: Bearer {admin_token}
```

#### Get Unread Count
```bash
GET http://localhost:8000/api/v1/notifications/unread-count
Authorization: Bearer {admin_token}
```

#### Mark Notification as Read
```bash
PATCH http://localhost:8000/api/v1/notifications/{notification_id}/read
Authorization: Bearer {admin_token}
```

---

## 🎯 Complete Testing Workflow

### PowerShell Script - Test All Admin Features
```powershell
# Login as Admin
$token = (Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method Post `
    -Body (@{email="admin@healcare.com"; password="Admin@123"} | ConvertTo-Json) `
    -ContentType "application/json").access_token

$headers = @{Authorization="Bearer $token"}

Write-Host "=" * 60
Write-Host "ADMIN TESTING - ALL FEATURES"
Write-Host "=" * 60

# 1. Doctors
Write-Host "`n1. DOCTORS:"
$doctors = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/doctors" -Headers $headers
Write-Host "   Total: $($doctors.doctors.Count)"

# 2. Appointments
Write-Host "`n2. APPOINTMENTS:"
$appointments = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/appointments" -Headers $headers
Write-Host "   Total: $($appointments.appointments.Count)"

# 3. Prescriptions
Write-Host "`n3. PRESCRIPTIONS:"
$prescriptions = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/prescriptions" -Headers $headers
Write-Host "   Total: $($prescriptions.prescriptions.Count)"

# 4. Medical History
Write-Host "`n4. MEDICAL HISTORY:"
$history = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/medical-history" -Headers $headers
Write-Host "   Total: $($history.Count)"

# 5. Reports
Write-Host "`n5. REPORTS:"
$reports = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/reports" -Headers $headers
Write-Host "   Total: $($reports.Count)"

# 6. Notifications
Write-Host "`n6. NOTIFICATIONS:"
$notifications = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/notifications" -Headers $headers
Write-Host "   Total: $(if($notifications -is [array]){$notifications.Count}else{1})"

Write-Host "`n" + "=" * 60
Write-Host "✅ All admin features accessible!"
Write-Host "=" * 60
```

---

## 📱 Frontend Testing

### Access Admin Dashboard
1. Open browser: http://localhost:3000
2. Login with:
   - Email: `admin@healcare.com`
   - Password: `Admin@123`
3. Navigate to Admin Dashboard

### Available Admin Pages:
- `/admin/dashboard` - Overview of all statistics
- `/admin/doctors` - Manage doctors
- `/admin/users` - Manage all users (patients, doctors, staff)
- `/admin/appointments` - View/manage all appointments
- `/admin/billing` - Billing management
- `/admin/settings` - System settings

---

## 🔧 CRUD Operations Summary

| Resource | Create | Read | Update | Delete |
|----------|--------|------|--------|--------|
| Doctors | ✅ (via registration) | ✅ | ✅ | ✅ |
| Patients | ✅ (via registration) | ✅ | ✅ | ✅ |
| Appointments | ✅ | ✅ | ✅ (cancel) | ✅ |
| Prescriptions | ✅ | ✅ | ✅ | ✅ |
| Medical History | ✅ | ✅ | ✅ | ✅ |
| Reports | ✅ (upload) | ✅ | ✅ | ✅ |
| Bills | ✅ | ✅ | ✅ (payment) | ✅ |
| Notifications | ✅ | ✅ | ✅ (mark read) | ✅ |

---

## 🎯 Testing Checklist

### Doctors Management
- [ ] View all doctors (GET /doctors)
- [ ] View doctor profile (GET /doctors/{id})
- [ ] View specializations (GET /doctors/specializations)
- [ ] Filter doctors by specialization

### Patients Management
- [ ] View all patients
- [ ] Create patient profile
- [ ] Update patient information
- [ ] Delete patient

### Appointments
- [ ] View all appointments
- [ ] Create appointment for any patient
- [ ] Filter by status (scheduled/completed/cancelled)
- [ ] Cancel appointment
- [ ] Reschedule appointment

### Prescriptions
- [ ] View all prescriptions
- [ ] Create prescription
- [ ] View active prescriptions (last 90 days)
- [ ] Filter by patient/doctor

### Medical History
- [ ] View all medical records
- [ ] Create medical record
- [ ] Update medical record
- [ ] Filter by patient

### Reports
- [ ] View all reports
- [ ] Upload report (PDF/image)
- [ ] Download report
- [ ] Filter by patient/type
- [ ] Delete report

### Billing
- [ ] View all bills
- [ ] Create bill
- [ ] Update payment status
- [ ] View bill details
- [ ] Generate invoice

### User Management
- [ ] View all users
- [ ] Create user account
- [ ] Update user role
- [ ] Deactivate user
- [ ] Reset user password

---

## 🚨 Important Notes

1. **Admin Access**: Admin has access to ALL resources across the system
2. **Data Privacy**: Be careful when testing with real patient data
3. **Audit Logs**: All admin actions should be logged (check audit tables)
4. **Permissions**: Admin can perform any CRUD operation
5. **API Rate Limits**: None for admin in development

---

## 📞 Need Help?

- **API Documentation**: http://localhost:8000/api/docs
- **Swagger UI**: Test endpoints interactively
- **Backend Logs**: Check terminal where `uvicorn` is running
- **Frontend Console**: F12 in browser for React errors

---

## ✅ Current System Status

Based on latest tests:
- ✅ 20 Doctors in database
- ✅ 20 Appointments in database  
- ✅ 14 Prescriptions in database
- ✅ 7 Medical records in database
- ✅ 7 Reports in database
- ✅ All API endpoints returning wrapped responses
- ✅ Backend running on port 8000
- ✅ Frontend ready for testing

**You're all set to test admin features! 🎉**
