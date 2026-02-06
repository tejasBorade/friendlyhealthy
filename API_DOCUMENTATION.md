# Healthcare Management Platform - API Documentation

## Base URL
```
Development: http://localhost:8000/api/v1
Production: https://yourdomain.com/api/v1
```

## Authentication

All endpoints except `/auth/register` and `/auth/login` require authentication.

**Authentication Header:**
```
Authorization: Bearer <access_token>
```

---

## API Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "role": "patient"  // patient | doctor | admin
}

Response: 201 Created
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "patient",
    "is_active": true,
    "is_verified": false,
    "created_at": "2026-02-07T10:00:00Z"
  }
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": { ... }
}
```

#### Refresh Token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}

Response: 200 OK
{
  "access_token": "new_access_token",
  "refresh_token": "new_refresh_token",
  "token_type": "bearer",
  "user": { ... }
}
```

#### Logout
```http
POST /auth/logout
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}

Response: 200 OK
{
  "message": "Successfully logged out"
}
```

---

### Doctors

#### Get Specializations
```http
GET /doctors/specializations

Response: 200 OK
[
  {
    "id": "uuid",
    "name": "Cardiologist",
    "description": "Heart specialists",
    "icon": "heart-icon.png"
  }
]
```

#### Search Doctors
```http
GET /doctors/search?specialization=Cardiologist&city=Mumbai&min_fee=500&max_fee=1000&is_verified=true&skip=0&limit=20
Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "first_name": "John",
    "last_name": "Doe",
    "gender": "male",
    "phone": "+911234567890",
    "registration_number": "MCI123456",
    "qualification": "MBBS, MD (Cardiology)",
    "experience_years": 10,
    "consultation_fee": 800.00,
    "about": "Experienced cardiologist...",
    "profile_picture": "url",
    "is_verified": true,
    "rating": 4.5,
    "total_reviews": 120,
    "specializations": ["Cardiologist"]
  }
]
```

#### Get Doctor by ID
```http
GET /doctors/{doctor_id}
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": "uuid",
  "first_name": "John",
  "last_name": "Doe",
  ...
}
```

#### Get Doctor Availability
```http
GET /doctors/{doctor_id}/availability?date=2026-02-10
Authorization: Bearer <access_token>

Response: 200 OK
{
  "doctor_id": "uuid",
  "date": "2026-02-10",
  "slots": [
    {
      "time": "09:00:00",
      "is_available": true
    },
    {
      "time": "09:30:00",
      "is_available": false
    }
  ]
}
```

---

### Appointments

#### Create Appointment
```http
POST /appointments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "doctor_id": "uuid",
  "appointment_date": "2026-02-10",
  "appointment_time": "09:00:00",
  "reason_for_visit": "Regular checkup",
  "symptoms": "Mild chest pain"
}

Response: 201 Created
{
  "id": "uuid",
  "appointment_number": "APT202602100001",
  "patient_id": "uuid",
  "doctor_id": "uuid",
  "appointment_date": "2026-02-10",
  "appointment_time": "09:00:00",
  "duration": 30,
  "status": "booked",
  "reason_for_visit": "Regular checkup",
  "symptoms": "Mild chest pain",
  "doctor_notes": null
}
```

#### Get Appointments
```http
GET /appointments?status=booked&skip=0&limit=20
Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": "uuid",
    "appointment_number": "APT202602100001",
    ...
  }
]
```

#### Get Appointment by ID
```http
GET /appointments/{appointment_id}
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": "uuid",
  "appointment_number": "APT202602100001",
  ...
}
```

#### Update Appointment Status
```http
PATCH /appointments/{appointment_id}/status
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "confirmed",  // booked | confirmed | completed | cancelled | rejected
  "notes": "Patient confirmed",
  "cancellation_reason": null
}

Response: 200 OK
{
  "id": "uuid",
  "status": "confirmed",
  ...
}
```

#### Cancel Appointment
```http
POST /appointments/{appointment_id}/cancel
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "reason": "Emergency came up"
}

Response: 200 OK
{
  "message": "Appointment cancelled successfully"
}
```

---

### Prescriptions (To be implemented)

#### Create Prescription
```http
POST /prescriptions
Authorization: Bearer <access_token> (Doctor only)
Content-Type: application/json

{
  "consultation_id": "uuid",
  "patient_id": "uuid",
  "notes": "Take medicines after food",
  "medicines": [
    {
      "medicine_name": "Aspirin",
      "dosage": "75mg",
      "usage": "after_food",
      "frequency": "1-0-1",
      "duration_days": 7,
      "special_instructions": "Avoid alcohol"
    }
  ]
}

Response: 201 Created
{
  "id": "uuid",
  "prescription_number": "RX202602100001",
  "consultation_id": "uuid",
  "patient_id": "uuid",
  "doctor_id": "uuid",
  "prescription_date": "2026-02-10",
  "notes": "Take medicines after food",
  "version": 1
}
```

#### Get Prescriptions
```http
GET /prescriptions?patient_id=uuid
Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": "uuid",
    "prescription_number": "RX202602100001",
    ...
  }
]
```

#### Download Prescription PDF
```http
GET /prescriptions/{prescription_id}/pdf
Authorization: Bearer <access_token>

Response: 200 OK
Content-Type: application/pdf
(Binary PDF data)
```

---

### Medical History (To be implemented)

#### Get Patient Medical History
```http
GET /medical-history/patient/{patient_id}
Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": "uuid",
    "patient_id": "uuid",
    "doctor_id": "uuid",
    "recorded_date": "2026-02-10",
    "past_illnesses": "Hypertension",
    "allergies": "Penicillin",
    "chronic_diseases": "Diabetes Type 2",
    "surgeries": "Appendectomy (2015)",
    "family_medical_history": "Father had heart disease",
    "current_medications": "Metformin 500mg",
    "notes": "Patient is managing well"
  }
]
```

#### Add Medical History
```http
POST /medical-history
Authorization: Bearer <access_token> (Doctor only)
Content-Type: application/json

{
  "patient_id": "uuid",
  "appointment_id": "uuid",
  "recorded_date": "2026-02-10",
  "past_illnesses": "Hypertension",
  "allergies": "Penicillin",
  "chronic_diseases": "Diabetes Type 2",
  "surgeries": "None",
  "family_medical_history": "Father had heart disease",
  "current_medications": "Metformin 500mg",
  "notes": "Regular monitoring required"
}

Response: 201 Created
{
  "id": "uuid",
  "patient_id": "uuid",
  ...
}
```

---

### Medical Reports (To be implemented)

#### Upload Report
```http
POST /reports
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

{
  "patient_id": "uuid",
  "report_type": "blood_test",  // blood_test | xray | mri | ct_scan | ecg | echo | ultrasound | other
  "report_name": "Complete Blood Count",
  "test_date": "2026-02-10",
  "lab_name": "City Lab",
  "lab_address": "123 Main St",
  "file": <binary>
}

Response: 201 Created
{
  "id": "uuid",
  "patient_id": "uuid",
  "report_type": "blood_test",
  "report_name": "Complete Blood Count",
  "test_date": "2026-02-10",
  "report_file_path": "uploads/reports/uuid.pdf"
}
```

#### Get Reports
```http
GET /reports?patient_id=uuid&report_type=blood_test
Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": "uuid",
    "patient_id": "uuid",
    "report_type": "blood_test",
    ...
  }
]
```

#### Download Report
```http
GET /reports/{report_id}/download
Authorization: Bearer <access_token>

Response: 200 OK
Content-Type: application/pdf or image/*
(Binary file data)
```

---

### Billing (To be implemented)

#### Create Bill
```http
POST /bills
Authorization: Bearer <access_token> (Admin/Doctor only)
Content-Type: application/json

{
  "patient_id": "uuid",
  "appointment_id": "uuid",
  "items": [
    {
      "charge_type_id": "uuid",
      "description": "Consultation",
      "quantity": 1,
      "unit_price": 800.00
    }
  ],
  "discount_amount": 0,
  "notes": "Initial consultation"
}

Response: 201 Created
{
  "id": "uuid",
  "bill_number": "BILL202602100001",
  "patient_id": "uuid",
  "appointment_id": "uuid",
  "bill_date": "2026-02-10",
  "subtotal": 800.00,
  "tax_amount": 144.00,
  "discount_amount": 0.00,
  "total_amount": 944.00,
  "payment_status": "pending"
}
```

#### Get Bills
```http
GET /bills?patient_id=uuid&payment_status=pending
Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": "uuid",
    "bill_number": "BILL202602100001",
    ...
  }
]
```

#### Update Payment Status
```http
PATCH /bills/{bill_id}/payment
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "payment_status": "paid",  // pending | paid | failed | refunded
  "payment_method": "credit_card",
  "transaction_id": "TXN123456"
}

Response: 200 OK
{
  "id": "uuid",
  "payment_status": "paid",
  "payment_date": "2026-02-10T15:30:00Z",
  ...
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "loc": ["body", "email"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  }
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Could not validate credentials"
  }
}
```

### 403 Forbidden
```json
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "Doctor access required"
  }
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found"
  }
}
```

### 409 Conflict
```json
{
  "success": false,
  "error": {
    "code": "CONFLICT",
    "message": "Email already registered"
  }
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An internal error occurred"
  }
}
```

---

## Rate Limiting

Default rate limit: **60 requests per minute** per user.

When rate limit is exceeded:
```json
{
  "error": "Rate limit exceeded. Please try again later."
}
```

---

## Pagination

List endpoints support pagination:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 20, max: 100)

Example:
```http
GET /appointments?skip=0&limit=20
```

---

## Testing the API

### Using cURL
```bash
# Set variables
export API_URL="http://localhost:8000/api/v1"
export TOKEN="your_access_token"

# Register
curl -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","role":"patient"}'

# Login
curl -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Get doctors
curl -X GET "$API_URL/doctors/search" \
  -H "Authorization: Bearer $TOKEN"
```

### Using Python
```python
import requests

API_URL = "http://localhost:8000/api/v1"

# Login
response = requests.post(f"{API_URL}/auth/login", json={
    "email": "test@example.com",
    "password": "Test123!"
})
token = response.json()["access_token"]

# Get doctors
headers = {"Authorization": f"Bearer {token}"}
doctors = requests.get(f"{API_URL}/doctors/search", headers=headers)
print(doctors.json())
```

---

**For interactive testing, visit:**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
