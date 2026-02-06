# Quick Testing Guide - Healthcare Management Platform

## 🚀 Quick Start

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Access Points
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Frontend**: http://localhost:3000
- **Database**: localhost:5432
- **Redis**: localhost:6379

---

## 🧪 Testing New Features

### Test Sequence

#### Step 1: Register Users
```bash
# Register Doctor
POST http://localhost:8000/api/v1/auth/register
{
  "email": "doctor@example.com",
  "password": "Doctor@123",
  "role": "doctor"
}

# Register Patient
POST http://localhost:8000/api/v1/auth/register
{
  "email": "patient@example.com",
  "password": "Patient@123",
  "role": "patient"
}
```

#### Step 2: Create Consultation (Doctor)
```bash
POST http://localhost:8000/api/v1/prescriptions/consultations
Authorization: Bearer <doctor_token>
{
  "appointment_id": "existing_appointment_uuid",
  "chief_complaint": "Fever and headache",
  "diagnosis": "Viral fever",
  "consultation_notes": "Rest advised",
  "follow_up_required": true,
  "follow_up_after_days": 7
}
```

#### Step 3: Create Prescription (Doctor)
```bash
POST http://localhost:8000/api/v1/prescriptions
Authorization: Bearer <doctor_token>
{
  "consultation_id": "consultation_uuid",
  "notes": "Take complete course",
  "medicines": [
    {
      "medicine_name": "Paracetamol 500mg",
      "dosage": "1 tablet",
      "frequency": "3 times a day",
      "duration_days": 5,
      "usage": "oral",
      "special_instructions": "After meals"
    }
  ]
}
```

#### Step 4: Record Medical History (Doctor)
```bash
POST http://localhost:8000/api/v1/medical-history
Authorization: Bearer <doctor_token>
{
  "patient_id": "patient_uuid",
  "recorded_date": "2026-02-07",
  "allergies": "Penicillin",
  "chronic_diseases": "None",
  "past_illnesses": "Typhoid (2020)",
  "surgeries": "Appendectomy (2018)"
}
```

#### Step 5: Upload Medical Report
```bash
# Using curl
curl -X POST "http://localhost:8000/api/v1/reports" \
  -H "Authorization: Bearer <token>" \
  -F "patient_id=patient_uuid" \
  -F "report_type=blood_test" \
  -F "report_name=CBC Test Results" \
  -F "test_date=2026-02-07" \
  -F "lab_name=PathLab" \
  -F "file=@report.pdf"

# Using Swagger UI
# Go to http://localhost:8000/api/docs
# Find POST /reports
# Click "Try it out"
# Fill in form fields
# Upload file
# Execute
```

#### Step 6: Create Bill (Doctor/Admin)
```bash
POST http://localhost:8000/api/v1/billing/bills
Authorization: Bearer <doctor_token>
{
  "patient_id": "patient_uuid",
  "appointment_id": "appointment_uuid",
  "items": [
    {
      "charge_type_id": "charge_type_uuid",
      "description": "General consultation",
      "quantity": 1,
      "unit_price": 500.00
    }
  ],
  "discount_amount": 0,
  "notes": "Regular consultation"
}
```

#### Step 7: Update Payment Status
```bash
PATCH http://localhost:8000/api/v1/billing/bills/{bill_id}/payment
Authorization: Bearer <token>
{
  "payment_status": "paid",
  "payment_method": "card",
  "transaction_id": "TXN123456789"
}
```

#### Step 8: Check Notifications
```bash
# Get unread count
GET http://localhost:8000/api/v1/notifications/unread-count
Authorization: Bearer <patient_token>

# Get all notifications
GET http://localhost:8000/api/v1/notifications
Authorization: Bearer <patient_token>

# Mark as read
PATCH http://localhost:8000/api/v1/notifications/{notification_id}/read
Authorization: Bearer <patient_token>
```

---

## 🔍 Testing Tips

### Using Swagger UI (Recommended)
1. Go to http://localhost:8000/api/docs
2. Click "Authorize" button at top
3. Enter token in format: `Bearer your_token_here`
4. Now you can test all endpoints interactively

### Using Postman
1. Import from OpenAPI: http://localhost:8000/api/openapi.json
2. Set environment variable: `token = your_access_token`
3. Add to Authorization header: `Bearer {{token}}`

### Using VS Code REST Client
Create `test.http` file:
```http
### Variables
@baseUrl = http://localhost:8000/api/v1
@token = your_access_token_here

### Login
POST {{baseUrl}}/auth/login
Content-Type: application/json

{
  "email": "doctor@example.com",
  "password": "Doctor@123"
}

### Get Prescriptions
GET {{baseUrl}}/prescriptions
Authorization: Bearer {{token}}
```

---

## 📋 Test Checklist

### Prescription Management
- [ ] Create consultation record
- [ ] Create prescription with multiple medicines
- [ ] List prescriptions
- [ ] View prescription details
- [ ] Update prescription (creates new version)
- [ ] View prescription history

### Medical History
- [ ] Create medical history record
- [ ] Get patient's medical history
- [ ] Update history record
- [ ] Delete history record

### Medical Reports
- [ ] Upload PDF report
- [ ] Upload image report (JPG/PNG)
- [ ] List reports with filters
- [ ] Download report file
- [ ] Update report metadata
- [ ] Delete report

### Billing
- [ ] Get charge types
- [ ] Create bill with multiple items
- [ ] List bills with filters
- [ ] Get bill details
- [ ] Update payment status
- [ ] Get bill summary

### Notifications
- [ ] Create notification
- [ ] List notifications
- [ ] Get unread count
- [ ] Mark notification as read
- [ ] Mark all as read
- [ ] Delete notification

### Background Tasks
- [ ] Start Celery worker
- [ ] Trigger email notification
- [ ] Trigger SMS notification
- [ ] Check Celery logs

---

## 🐛 Common Issues & Solutions

### Issue: "Appointment not found"
**Solution**: Create an appointment first using appointments endpoint

### Issue: "Doctor profile not found"
**Solution**: Complete doctor profile after registration

### Issue: "File upload failed"
**Solution**: Check file size (<10MB) and type (PDF, JPG, PNG only)

### Issue: "Token expired"
**Solution**: Use refresh token endpoint to get new access token

### Issue: "Permission denied"
**Solution**: Check user role - some endpoints are doctor/admin only

### Issue: "Celery tasks not running"
**Solution**: 
```bash
# Start Celery worker
cd backend
celery -A app.services.celery_tasks.celery_app worker --loglevel=info
```

---

## 🔐 Test Credentials

After registration, use these credentials:

**Doctor:**
- Email: doctor@example.com
- Password: Doctor@123

**Patient:**
- Email: patient@example.com
- Password: Patient@123

**Admin:**
- Email: admin@example.com
- Password: Admin@123

---

## 📊 Sample Data

### Sample Prescription Medicine
```json
{
  "medicine_name": "Azithromycin 500mg",
  "dosage": "1 tablet",
  "usage": "oral",
  "frequency": "Once daily",
  "duration_days": 5,
  "special_instructions": "Take on empty stomach"
}
```

### Sample Medical History
```json
{
  "past_illnesses": "Chickenpox (2015), Dengue (2018)",
  "allergies": "Penicillin, Peanuts",
  "chronic_diseases": "Asthma",
  "surgeries": "Tonsillectomy (2010)",
  "family_medical_history": "Father has diabetes, Mother has hypertension",
  "current_medications": "Salbutamol inhaler as needed"
}
```

### Sample Bill Item
```json
{
  "charge_type_id": "uuid",
  "description": "General consultation with specialist",
  "quantity": 1,
  "unit_price": 1000.00
}
```

---

## 🎯 Performance Testing

### Load Testing with Apache Bench
```bash
# Test login endpoint
ab -n 100 -c 10 -T 'application/json' \
  -p login.json \
  http://localhost:8000/api/v1/auth/login

# Test get prescriptions
ab -n 100 -c 10 \
  -H "Authorization: Bearer token" \
  http://localhost:8000/api/v1/prescriptions
```

### Response Time Goals
- Authentication: < 200ms
- List endpoints: < 300ms
- Create operations: < 400ms
- File upload: < 1000ms
- File download: < 500ms

---

## 📝 Notes

1. **Database Setup**: Run `DATABASE_SCHEMA.sql` before testing
2. **Charge Types**: Create charge types before creating bills
3. **File Storage**: Ensure `./uploads/reports` directory exists
4. **Redis**: Required for Celery tasks
5. **Email/SMS**: Configure SendGrid/Twilio for real notifications

---

## 🎉 Happy Testing!

For detailed API documentation, visit:
- Swagger UI: http://localhost:8000/api/docs
- Full Documentation: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

For issues or questions, check:
- [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)
- [SETUP_GUIDE.md](SETUP_GUIDE.md)
