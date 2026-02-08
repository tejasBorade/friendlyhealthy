# 🏥 Healthcare Platform - Login Credentials

## All Roles Available

### 👤 **Patient Login**
- **Email**: `patient@healthcare.com`
- **Password**: `Patient@123`
- **Access**: Book appointments, view medical history, prescriptions, reports, billing

---

### 👨‍⚕️ **Doctor Login**
- **Email**: `doctor@healthcare.com`
- **Password**: `Doctor@123`
- **Access**: View appointments, patient records, write prescriptions, manage schedule

---

### 👔 **Staff Login**
- **Email**: `staff@healthcare.com`
- **Password**: `Staff@123`
- **Access**: Manage appointments, view all patients, doctors, administrative tasks

---

### 🔐 **Admin Login**
- **Email**: `admin@healthcare.com`
- **Password**: `Admin@123`
- **Access**: Full system access, user management, reports, settings, analytics

---

## Additional Test Accounts

### Patient
- **Email**: `test@example.com`
- **Password**: `Test@123`

---

## Features by Role

### Patient Dashboard Features:
- ✅ Search and filter doctors by specialization
- ✅ Book appointments with available doctors
- ✅ View appointment history
- ✅ Access medical records
- ✅ View prescriptions  
- ✅ Download reports
- ✅ Check billing information

### Doctor Dashboard Features:
- ✅ View scheduled appointments
- ✅ Access patient medical history
- ✅ Write and manage prescriptions
- ✅ Update appointment status
- ✅ View patient reports
- ✅ Manage availability

### Staff Dashboard Features:
- ✅ Manage all appointments
- ✅ View and edit patient information
- ✅ View doctor schedules
- ✅ Handle administrative tasks
- ✅ Generate reports
- ✅ Process billing

### Admin Dashboard Features:
- ✅ Complete system overview
- ✅ User management (patients, doctors, staff)
- ✅ System analytics and statistics
- ✅ Revenue tracking
- ✅ Appointment management
- ✅ Doctor management
- ✅ System settings
- ✅ Generate comprehensive reports

---

## How to Login

1. **Start the Application**:
   ```powershell
   cd c:\Users\tejas\friendlyhealthy\friendlyhealthy
   .\run-app.ps1
   ```

2. **Open Browser**: http://localhost:3000

3. **Select Your Role**: Choose one of the login credentials above

4. **Login**: Enter email and password

5. **You'll be automatically redirected** to the appropriate dashboard based on your role

---

## Testing Different Roles

To test different role functionalities:

1. **Logout** from current account (click profile/logout button)
2. **Return to login page**
3. **Login with different role credentials**
4. **Explore role -specific features**

---

## Role Permissions Summary

| Feature | Patient | Doctor | Staff | Admin |
|---------|---------|--------|-------|-------|
| View Own Dashboard | ✅ | ✅ | ✅ | ✅ |
| Book Appointments | ✅ | ❌ | ✅ | ✅ |
| View All Appointments | ❌ | ✅ (own) | ✅ | ✅ |
| Manage Appointments | ❌ | ✅ (own) | ✅ | ✅ |
| View Medical Records | ✅ (own) | ✅ | ✅ | ✅ |
| Write Prescriptions | ❌ | ✅ | ❌ | ✅ |
| View All Patients | ❌ | ✅ (own) | ✅ | ✅ |
| View All Doctors | ✅ | ✅ | ✅ | ✅ |
| User Management | ❌ | ❌ | ❌ | ✅ |
| System Reports | ❌ | ✅ (own) | ✅ | ✅ |
| Billing | ✅ (own) | ❌ | ✅ | ✅ |
| System Settings | ❌ | ❌ | ❌ | ✅ |

---

## Current System Status

✅ **Backend**: Running on http://localhost:5000  
✅ **Frontend**: Running on http://localhost:3000  
✅ **Database**: PostgreSQL Connected  
✅ **All 4 Roles**: Patient, Doctor, Staff, Admin  
✅ **Authentication**: JWT-based secure login  
✅ **Role-Based Access Control**: Fully implemented  

---

## Quick Test Flow

### Test as Patient:
1. Login as `patient@healthcare.com`
2. Search for doctors
3. Book an appointment
4. View your dashboard

### Test as Doctor:
1. Login as `doctor@healthcare.com`
2. View your appointments
3. Check patient records
4. Manage your schedule

### Test as Staff:
1. Login as `staff@healthcare.com`
2. View all appointments
3. Manage patient records
4. Access administrative features

### Test as Admin:
1. Login as `admin@healthcare.com`
2. View system analytics
3. Manage all users
4. Access system settings

---

**All credentials are ready! Choose your role and start testing! 🚀**
