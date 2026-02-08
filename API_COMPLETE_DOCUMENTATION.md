# Healthcare Management Platform - Complete API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
All protected routes require a Bearer token in the Authorization header:
```
Authorization: Bearer <token>
```

---

## 1. Authentication APIs

### 1.1 Register User
**POST** `/auth/register`

**Body:**
```json
{
  "email": "user@example.com",
  "password": "Password@123",
  "role": "patient",
  "firstName": "John",
  "lastName": "Doe",
  "phone": "555-0100"
}
```

**Response:** `201 Created`
```json
{
  "message": "User registered successfully",
  "userId": 1,
  "patientId": 1
}
```

### 1.2 Login
**POST** `/auth/login`

**Body:**
```json
{
  "email": "user@example.com",
  "password": "Password@123"
}
```

**Response:** `200 OK`
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "userId": 1,
    "email": "user@example.com",
    "role": "patient",
    "patientId": 1
  }
}
```

### 1.3 Get Current User
**GET** `/auth/me` 🔒

**Response:** `200 OK`
```json
{
  "user": {
    "userId": 1,
    "email": "user@example.com",
    "role": "patient",
    "patientId": 1
  }
}
```

---

## 2. Doctor APIs

### 2.1 Get All Doctors
**GET** `/doctors`

**Query Parameters:**
- `specialization` (optional): Filter by specialization
- `available` (optional): true/false
- `search` (optional): Search by name or specialization

**Response:** `200 OK`
```json
{
  "doctors": [
    {
      "id": 1,
      "first_name": "Barbara",
      "last_name": "White",
      "specialization": "Cardiology",
      "qualification": "MD, FACC",
      "experience_years": 15,
      "phone": "555-0201",
      "consultation_fee": 500,
      "clinic_name": "Heart Care Clinic",
      "clinic_address": "123 Medical Center",
      "clinic_phone": "555-0300",
      "hospital_affiliation": "City General Hospital",
      "license_number": "MC12345",
      "is_available": true
    }
  ]
}
```

### 2.2 Get Doctor by ID
**GET** `/doctors/:id`

**Response:** `200 OK`
```json
{
  "doctor": {
    "id": 1,
    "first_name": "Barbara",
    "last_name": "White",
    "specialization": "Cardiology",
    "timeSlots": [
      {
        "id": 1,
        "day_of_week": 1,
        "start_time": "09:00:00",
        "end_time": "17:00:00",
        "slot_duration": 30
      }
    ]
  }
}
```

### 2.3 Update Doctor Profile
**PUT** `/doctors/:id` 🔒 (Doctor, Admin)

**Body:**
```json
{
  "firstName": "Barbara",
  "lastName": "White",
  "clinicName": "Heart Care Clinic",
  "clinicAddress": "123 Medical Center",
  "clinicPhone": "555-0300",
  "consultationFee": 600
}
```

### 2.4 Add Time Slot
**POST** `/doctors/:id/time-slots` 🔒 (Doctor, Admin)

**Body:**
```json
{
  "dayOfWeek": 1,
  "startTime": "09:00",
  "endTime": "17:00",
  "slotDuration": 30
}
```

### 2.5 Get Available Slots
**GET** `/doctors/:id/available-slots?date=2026-02-10`

**Response:** `200 OK`
```json
{
  "availableSlots": ["09:00", "09:30", "10:00", "10:30"]
}
```

---

## 3. Appointment APIs

### 3.1 Get Appointments
**GET** `/appointments` 🔒

**Query Parameters:**
- `patientId` (optional)
- `doctorId` (optional)
- `status` (optional): booked, confirmed, completed, cancelled, rejected
- `date` (optional): YYYY-MM-DD

### 3.2 Create Appointment
**POST** `/appointments` 🔒

**Body:**
```json
{
  "patientId": 1,
  "doctorId": 1,
  "appointmentDate": "2026-02-15",
  "appointmentTime": "10:00",
  "reason": "Regular checkup"
}
```

### 3.3 Update Appointment Status
**PATCH** `/appointments/:id` 🔒

**Body:**
```json
{
  "status": "confirmed",
  "notes": "Patient confirmed attendance"
}
```

### 3.4 Accept Appointment
**PATCH** `/appointments/:id/accept` 🔒 (Doctor)

### 3.5 Reject Appointment
**PATCH** `/appointments/:id/reject` 🔒 (Doctor)

**Body:**
```json
{
  "reason": "Not available at this time"
}
```

### 3.6 Reschedule Appointment
**POST** `/appointments/:id/reschedule` 🔒

**Body:**
```json
{
  "newDate": "2026-02-20",
  "newTime": "14:00",
  "reason": "Doctor's request"
}
```

---

## 4. Patient APIs

### 4.1 Get Patient by ID
**GET** `/patients/:id` 🔒

### 4.2 Get All Patients
**GET** `/patients` 🔒 (Staff, Admin)

---

## 5. Medical Records APIs

### 5.1 Get Medical Records
**GET** `/medical-records/:patientId` 🔒

### 5.2 Add Medical Record
**POST** `/medical-records` 🔒 (Doctor)

**Body:**
```json
{
  "patientId": 1,
  "diagnosis": "Hypertension",
  "symptoms": "Headache, dizziness",
  "treatment": "Medication prescribed",
  "notes": "Follow-up in 2 weeks",
  "visitDate": "2026-02-08",
  "allergies": "Penicillin",
  "chronicDiseases": "Diabetes Type 2",
  "surgeries": "Appendectomy (2020)",
  "familyHistory": "Father had heart disease",
  "bloodPressure": "140/90",
  "temperature": 98.6,
  "weight": 75.5,
  "height": 170
}
```

### 5.3 Update Medical Record
**PUT** `/medical-records/:id` 🔒 (Doctor)

### 5.4 Delete Medical Record
**DELETE** `/medical-records/:id` 🔒 (Doctor)

---

## 6. Prescription APIs

### 6.1 Get Prescriptions
**GET** `/prescriptions/:patientId` 🔒

### 6.2 Add Prescription
**POST** `/prescriptions` 🔒 (Doctor)

**Body:**
```json
{
  "patientId": 1,
  "medicationName": "Lisinopril",
  "dosage": "10mg",
  "frequency": "Once daily",
  "duration": "30 days",
  "instructions": "Take with water",
  "prescribedDate": "2026-02-08",
  "usageTiming": "after_food",
  "frequencyPattern": "1-0-0"
}
```

**Usage Timing Options:**
- `before_food`
- `after_food`
- `with_food`
- `empty_stomach`

**Frequency Pattern Format:**
Morning-Afternoon-Evening (e.g., "1-0-1" means morning and evening)

### 6.3 Update Prescription
**PUT** `/prescriptions/:id` 🔒 (Doctor)

### 6.4 Delete Prescription
**DELETE** `/prescriptions/:id` 🔒 (Doctor)

---

## 7. Reports APIs

### 7.1 Get Reports
**GET** `/reports/:patientId` 🔒

### 7.2 Upload Report
**POST** `/reports` 🔒 (Doctor)

**Body:**
```json
{
  "patientId": 1,
  "reportType": "Blood Test",
  "reportDate": "2026-02-08",
  "findings": "All parameters within normal range",
  "testName": "Complete Blood Count",
  "labName": "City Diagnostics",
  "labAddress": "456 Lab Street",
  "labPhone": "555-0400",
  "doctorRemarks": "Reports normal, continue medication",
  "testResults": {
    "hemoglobin": 14.5,
    "wbc": 7500,
    "platelets": 250000
  }
}
```

### 7.3 Update Report
**PUT** `/reports/:id` 🔒 (Doctor)

### 7.4 Delete Report
**DELETE** `/reports/:id` 🔒 (Doctor)

---

## 8. Billing APIs

### 8.1 Get All Invoices
**GET** `/billing` 🔒

**Query Parameters:**
- `patientId` (optional)
- `status` (optional): pending, paid, partially_paid, overdue, cancelled
- `fromDate` (optional): YYYY-MM-DD
- `toDate` (optional): YYYY-MM-DD

### 8.2 Get Invoice by ID
**GET** `/billing/:id` 🔒

**Response:**
```json
{
  "invoice": {
    "id": 1,
    "invoice_number": "INV-2026-10001",
    "patient_name": "John Doe",
    "doctor_name": "Dr. Barbara White",
    "invoice_date": "2026-02-08",
    "subtotal": 500,
    "tax_rate": 18,
    "tax_amount": 90,
    "discount": 0,
    "total_amount": 590,
    "payment_status": "pending",
    "items": [
      {
        "item_type": "consultation",
        "item_name": "Cardiology Consultation",
        "quantity": 1,
        "unit_price": 500,
        "total_price": 500
      }
    ]
  }
}
```

### 8.3 Create Invoice
**POST** `/billing` 🔒 (Doctor, Staff, Admin)

**Body:**
```json
{
  "patientId": 1,
  "doctorId": 1,
  "appointmentId": 1,
  "items": [
    {
      "item_type": "consultation",
      "item_name": "Cardiology Consultation",
      "description": "Initial consultation",
      "quantity": 1,
      "unit_price": 500,
      "total_price": 500
    },
    {
      "item_type": "test",
      "item_name": "ECG",
      "description": "Electrocardiogram",
      "quantity": 1,
      "unit_price": 200,
      "total_price": 200
    }
  ],
  "taxRate": 18,
  "discount": 50,
  "notes": "Payment due in 7 days",
  "dueDate": "2026-02-15"
}
```

**Item Type Options:**
- `consultation`
- `test`
- `checkup`
- `followup`
- `procedure`

### 8.4 Update Invoice
**PUT** `/billing/:id` 🔒 (Staff, Admin)

**Body:**
```json
{
  "paymentStatus": "paid",
  "paymentMethod": "credit_card",
  "paymentDate": "2026-02-08",
  "notes": "Payment received"
}
```

### 8.5 Get Billing Statistics
**GET** `/billing/stats/summary` 🔒 (Admin)

**Query Parameters:**
- `fromDate` (optional)
- `toDate` (optional)

**Response:**
```json
{
  "stats": {
    "total_paid_invoices": 150,
    "total_pending_invoices": 25,
    "total_overdue_invoices": 5,
    "total_revenue": 75000,
    "pending_amount": 12500,
    "overdue_amount": 2500,
    "average_invoice_amount": 500
  }
}
```

---

## 9. Notifications APIs

### 9.1 Get Notifications
**GET** `/notifications` 🔒

**Query Parameters:**
- `isRead` (optional): true/false
- `type` (optional): appointment_reminder, prescription_ready, payment_due
- `limit` (optional): default 50

### 9.2 Create Notification
**POST** `/notifications` 🔒

**Body:**
```json
{
  "userId": 1,
  "notificationType": "appointment_reminder",
  "title": "Appointment Tomorrow",
  "message": "Your appointment with Dr. White is tomorrow at 10:00 AM",
  "priority": "high",
  "sendVia": "email",
  "scheduledTime": "2026-02-09T09:00:00",
  "referenceType": "appointment",
  "referenceId": 1
}
```

**Notification Types:**
- `appointment_reminder`
- `prescription_ready`
- `payment_due`
- `test_results_ready`
- `appointment_confirmed`
- `appointment_cancelled`

**Priority Levels:**
- `low`
- `normal`
- `high`
- `urgent`

### 9.3 Mark as Read
**PUT** `/notifications/:id/read` 🔒

### 9.4 Mark All as Read
**PUT** `/notifications/read-all` 🔒

### 9.5 Get Unread Count
**GET** `/notifications/unread/count` 🔒

**Response:**
```json
{
  "unreadCount": 5
}
```

---

## 10. Audit Logs APIs

### 10.1 Get Audit Logs
**GET** `/audit` 🔒 (Admin)

**Query Parameters:**
- `entityType` (optional): medical_record, prescription, invoice, appointment
- `entityId` (optional)
- `userId` (optional)
- `fromDate` (optional)
- `toDate` (optional)
- `limit` (optional): default 100

**Response:**
```json
{
  "logs": [
    {
      "id": 1,
      "user_email": "doctor@example.com",
      "user_role": "doctor",
      "action": "create",
      "entity_type": "prescription",
      "entity_id": 1,
      "old_values": null,
      "new_values": {
        "medication_name": "Lisinopril",
        "dosage": "10mg"
      },
      "ip_address": "192.168.1.1",
      "created_at": "2026-02-08T10:30:00"
    }
  ]
}
```

### 10.2 Get Audit Statistics
**GET** `/audit/stats` 🔒 (Admin)

---

## Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Role-Based Access Control

### Roles:
1. **patient** - Can view own data, book appointments
2. **doctor** - Can manage medical records, prescriptions, appointments
3. **staff** - Can manage appointments, billing
4. **admin** - Full access to all resources

---

## Database Schema Summary

### Tables:
1. `users` - Authentication (26 users)
2. `patients` - Patient profiles (linked to users)
3. `doctors` - Doctor profiles with clinic details (21 doctors)
4. `doctor_time_slots` - Doctor availability schedules
5. `appointments` - Appointment bookings
6. `medical_records` - Patient medical history
7. `prescriptions` - Medication prescriptions
8. `reports` - Diagnostic reports
9. `invoices` - Billing invoices
10. `invoice_items` - Invoice line items
11. `notifications` - User notifications
12. `audit_logs` - System audit trail
13. `patient_consents` - Patient consent management
14. `system_settings` - Application settings

---

## Production Deployment Checklist

✅ Database schema with all tables
✅ Role-based access control
✅ JWT authentication
✅ Input validation
✅ Error handling
✅ Audit logging
✅ CORS configuration
✅ Environment variables
⏳ Rate limiting (recommended)
⏳ File upload handling (multer)
⏳ PDF generation (pdfkit/puppeteer)
⏳ Email/SMS integration
⏳ Data encryption
⏳ Backup strategy

---

## Testing Credentials

### Doctor:
- Email: `barbara.white@healthcare.com`
- Password: `Doctor@123`

### Patient:
- Email: `john.smith@email.com`
- Password: `Patient@123`

### Admin (if created):
- Email: `admin@healthcare.com`
- Password: `Admin@123`

---

## Next Steps for Production

1. **Security Enhancements:**
   - Implement rate limiting
   - Add request validation middleware
   - Enable HTTPS
   - Implement data encryption

2. **File Upload:**
   - Configure multer for file uploads
   - Set up cloud storage (AWS S3, Azure Blob)
   - Implement file type validation

3. **PDF Generation:**
   - Install pdfkit or puppeteer
   - Create prescription PDF templates
   - Add download endpoints

4. **Notifications:**
   - Integrate email service (SendGrid, AWS SES)
   - Integrate SMS service (Twilio)
   - Set up notification scheduler

5. **Analytics:**
   - Add dashboard statistics
   - Implement reporting system
   - Track user activity

6. **Testing:**
   - Write unit tests
   - Write integration tests
   - Perform load testing

---

*Last Updated: February 8, 2026*
