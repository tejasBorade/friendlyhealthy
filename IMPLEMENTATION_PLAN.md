# SymptoTrack Implementation Plan
## From FriendlyHealthy to SymptoTrack PRD v1.0

**Primary Backend:** FastAPI (Python) + PostgreSQL  
**Mobile:** Flutter (Android + iOS)  
**AI Provider:** Google Gemini  
**Scope:** Full product (P0 + P1) — all 8 modules  
**Estimated Duration:** 18-22 weeks  

---

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary API | FastAPI + PostgreSQL | Mature, full ORM, async, Celery for jobs |
| Mobile | Flutter | Cross-platform, single codebase for Android/iOS |
| Web Frontend | Keep React + MUI | Already built, used for admin panel |
| AI | Google Gemini API | Strong medical knowledge, cost-effective |
| Notifications | FCM + SMS (Twilio) + WhatsApp (Meta API) | Multi-channel as per PRD |
| File Storage | AWS S3 / Cloudflare R2 | Scalable, CDN-backed |
| Background Jobs | Celery + Redis (already set up) | Reminders, notifications, AI |
| Auth | Keep JWT but add OTP flow | PRD mandates OTP-first login |

---

## Phase 0: Foundation & Database Migration (Week 1-2)

### Sprint 0.1 — Database Schema Extensions (Week 1)

New tables and columns needed to support SymptoTrack features.

**Files to modify:**
- `DATABASE_SCHEMA.sql` — Add new tables
- `backend/app/models/` — Add/update SQLAlchemy models

**New Tables:**

```
1. digital_signatures
   - id, doctor_id, signature_image_path, signature_pin_hash
   - is_active, created_at

2. prescription_signatures
   - id, prescription_id, signature_id, signed_at, is_locked

3. medicine_reminders
   - id, prescription_id, prescription_medicine_id, patient_id
   - medicine_name, dosage, frequency_code, timing_slots (JSONB)
   - start_date, end_date, is_active, is_critical
   - snooze_count, last_triggered_at, created_at

4. follow_up_reminders
   - id, prescription_id, patient_id, doctor_id
   - follow_up_date, reminder_7day_sent, reminder_1day_sent
   - reminder_morning_sent, status (upcoming/visited/missed)
   - created_at

5. test_reminders
   - id, prescription_id, patient_id
   - test_name, follow_up_date, reminder_3day_sent
   - reminder_1day_sent, upload_status (ordered/uploaded/missing)
   - report_id (FK to medical_reports), created_at

6. patient_abha
   - id, patient_id, abha_id, abha_address
   - linked_at, is_verified, consent_status

7. doctor_verification
   - id, doctor_id, nmc_registration_number, state_council
   - verification_status (pending/verified/rejected/manual_review)
   - verified_at, verified_by, rejection_reason
   - nmc_api_response (JSONB)

8. consent_records
   - id, patient_id, doctor_id, consent_type
   - purpose, duration_days, granted_at, expires_at
   - revoked_at, is_active, device_info, ip_address

9. emergency_access_logs
   - id, doctor_id, patient_id, justification
   - accessed_at, reviewed_at, reviewed_by
   - review_status (pending/approved/flagged)

10. data_erasure_requests
    - id, patient_id, requested_at, status
    - processed_at, processing_notes
    - data_retained_reason, deadline_date

11. ai_suggestions
    - id, doctor_id, session_id, patient_context_hash
    - suggestion_type, suggestion_text (JSONB)
    - doctor_action (used/dismissed/noted)
    - created_at, response_time_ms

12. doctor_patient_connections
    - id, doctor_id, patient_id, connect_code
    - connected_at, is_active, connection_method (qr/code/search)

13. messages
    - id, sender_id, receiver_id, prescription_id
    - message_type, content, is_read, created_at

14. doctor_medicine_favorites
    - id, doctor_id, medicine_name, dosage, frequency
    - usage_instructions, category, usage_count

15. prescription_templates
    - id, doctor_id, template_name, diagnosis
    - medicines (JSONB), tests (JSONB), instructions
    - usage_count, created_at

16. tests_ordered
    - id, prescription_id, test_name, test_type
    - due_date, status (ordered/uploaded/missing)
    - report_id, created_at

17. notification_preferences
    - id, user_id, medicine_reminders, follow_up_reminders
    - test_reminders, doctor_messages, report_alerts
    - quiet_hours_start, quiet_hours_end
    - preferred_channel (push/sms/whatsapp)

18. device_tokens
    - id, user_id, device_token, platform (android/ios/web)
    - device_info, is_active, registered_at
```

**Columns to add to existing tables:**

```
prescriptions:
  + follow_up_date DATE
  + patient_instructions TEXT
  + is_signed BOOLEAN DEFAULT FALSE
  + signed_at TIMESTAMP
  + pdf_path VARCHAR(500)
  + is_locked BOOLEAN DEFAULT FALSE
  + diagnosis_icd10_code VARCHAR(20)
  + diagnosis_patient_friendly TEXT

patients:
  + abha_id VARCHAR(50)
  + known_allergies TEXT
  + chronic_conditions TEXT
  + caregiver_name VARCHAR(200)
  + caregiver_phone VARCHAR(20)

doctors:
  + clinic_name VARCHAR(200)  [exists in CF D1 schema]
  + clinic_address TEXT
  + clinic_logo VARCHAR(500)
  + nmc_verified BOOLEAN DEFAULT FALSE
  + nmc_verified_at TIMESTAMP
  + digital_signature_path VARCHAR(500)

medical_reports:
  + prescription_id UUID FK
  + test_order_id UUID FK
  + follow_up_date DATE
  + structured_values JSONB (for trend analysis)

users:
  + phone VARCHAR(20)
  + otp_hash VARCHAR(255)
  + otp_expires_at TIMESTAMP
  + failed_otp_attempts INTEGER DEFAULT 0
  + locked_until TIMESTAMP
  + last_device_info JSONB
```

### Sprint 0.2 — Auth System Upgrade (Week 2)

Add OTP-based auth alongside existing JWT.

**Files to create:**
- `backend/app/services/otp_service.py` — OTP generation, verification, rate limiting
- `backend/app/api/routes/onboarding.py` — Multi-step onboarding endpoints

**Files to modify:**
- `backend/app/api/routes/auth.py` — Add OTP login flow
- `backend/app/core/security.py` — Add OTP hash/verify, session timeout logic
- `backend/app/core/config.py` — Add Gemini API key, OTP settings, session timeout config

**Endpoints to add:**
```
POST /api/v1/auth/send-otp          — Send OTP to phone
POST /api/v1/auth/verify-otp        — Verify OTP and issue JWT
POST /api/v1/auth/biometric-login   — Biometric token exchange

POST /api/v1/onboarding/doctor/step/{n}  — Doctor 5-step onboarding
POST /api/v1/onboarding/patient/step/{n} — Patient 5-step onboarding
```

---

## Phase 1: Digital Prescription Engine (Week 3-5) — P0

### Sprint 1.1 — Prescription Enhancements (Week 3)

**Files to create:**
- `backend/app/services/prescription_service.py` — PDF generation, signing, locking
- `backend/app/services/pdf_generator.py` — Prescription PDF with letterhead + signature

**Files to modify:**
- `backend/app/api/routes/prescriptions.py` — Add signing, locking, PDF endpoints
- `backend/app/schemas/prescription.py` — Add signature, template, follow-up fields

**Endpoints to add:**
```
POST /api/v1/prescriptions/{id}/sign         — Doctor signs (PIN verified)
GET  /api/v1/prescriptions/{id}/pdf          — Download/generate PDF
POST /api/v1/prescriptions/from-template     — Create from template
GET  /api/v1/prescriptions/active            — Patient's active prescriptions
GET  /api/v1/prescriptions/search            — Search by doctor/medicine/diagnosis/date
```

### Sprint 1.2 — Templates & Favorites (Week 4)

**Files to create:**
- `backend/app/models/prescription_extras.py` — Templates, favorites models
- `backend/app/api/routes/templates.py` — Template CRUD
- `backend/app/api/routes/favorites.py` — Medicine favorites CRUD

**Endpoints:**
```
CRUD /api/v1/templates                       — Prescription templates
CRUD /api/v1/favorites                       — Doctor medicine favorites
GET  /api/v1/favorites/search?q=             — Search favorites while typing
```

### Sprint 1.3 — Digital Signature System (Week 4)

**Files to create:**
- `backend/app/services/signature_service.py` — Signature upload, PIN management

**Endpoints:**
```
POST /api/v1/signatures/setup               — Upload/draw signature + set PIN
POST /api/v1/signatures/verify-pin           — Verify PIN before signing
PUT  /api/v1/signatures/update-pin           — Change PIN
```

### Sprint 1.4 — Tests Ordered Tracking (Week 5)

**Files to modify:**
- `backend/app/api/routes/prescriptions.py` — Add tests ordered within prescription
- `backend/app/models/medical.py` — Add TestsOrdered model

**Endpoints:**
```
GET  /api/v1/prescriptions/{id}/tests        — Get tests for a prescription
PUT  /api/v1/tests-ordered/{id}/status       — Update test status
```

---

## Phase 2: Smart Reminder System (Week 5-7) — P0

### Sprint 2.1 — Reminder Engine Core (Week 5-6)

**Files to create:**
- `backend/app/models/reminder.py` — MedicineReminder, FollowUpReminder, TestReminder models
- `backend/app/services/reminder_service.py` — Auto-generate reminders from prescription
- `backend/app/services/reminder_scheduler.py` — Celery beat tasks for triggering reminders
- `backend/app/api/routes/reminders.py` — Reminder dashboard API

**Key Logic:**
```python
# When prescription is signed and sent:
# 1. Parse each medicine → create medicine_reminder with:
#    - timing_slots from frequency (e.g., "1-0-1" → [08:00, 20:00])
#    - start_date = prescription_date
#    - end_date = prescription_date + duration_days
#    - is_critical based on medicine category
# 2. If follow_up_date set → create follow_up_reminder
# 3. If tests_ordered → create test_reminder per test
```

**Celery Beat Schedule:**
```python
# Every 1 minute: check due medicine reminders → send push/SMS
# Every morning 7AM: check follow-up reminders (7-day, 1-day, morning-of)
# Every morning 7AM: check test reminders (3-day, 1-day before follow-up)
```

**Endpoints:**
```
GET  /api/v1/reminders/dashboard             — All active reminders (patient)
GET  /api/v1/reminders/medicine              — Medicine reminders only
GET  /api/v1/reminders/follow-ups            — Follow-up reminders only
GET  /api/v1/reminders/tests                 — Test reminders only
POST /api/v1/reminders/{id}/snooze           — Snooze a reminder (15 min max)
POST /api/v1/reminders/{id}/acknowledge      — Mark as taken/done
GET  /api/v1/reminders/missed                — Missed reminders
```

### Sprint 2.2 — Notification Delivery (Week 6-7)

**Files to create:**
- `backend/app/services/push_notification.py` — FCM integration for push notifications
- `backend/app/services/whatsapp_service.py` — WhatsApp Business API integration
- `backend/app/api/routes/notification_preferences.py` — User notification settings

**Files to modify:**
- `backend/app/services/notification_service.py` — Multi-channel fallback logic
- `backend/app/services/celery_tasks.py` — Add reminder trigger tasks

**Multi-channel Fallback Logic:**
```python
async def send_reminder(user_id, reminder):
    # 1. Try Push (FCM)
    if push_sent: return
    # 2. Try SMS (Twilio)
    if sms_sent: return
    # 3. Try WhatsApp (Meta API)
    whatsapp_sent = await send_whatsapp(...)
```

**Quiet Hours Logic:**
```python
# Regular medicines: hold until 7 AM
# Critical medicines: silent vibrate (push with sound=false)
# Security alerts: always immediate
```

**Endpoints:**
```
GET  /api/v1/notification-preferences        — Get preferences
PUT  /api/v1/notification-preferences        — Update preferences
POST /api/v1/devices/register                — Register FCM device token
DELETE /api/v1/devices/{token}               — Remove device token
```

---

## Phase 3: Lab Report Linking (Week 7-8) — P1

### Sprint 3.1 — Report-Prescription Linking (Week 7)

**Files to modify:**
- `backend/app/api/routes/reports.py` — Add linking to prescription/test-order
- `backend/app/models/report.py` — Add prescription_id, test_order_id FKs

**Endpoints:**
```
POST /api/v1/reports/upload                  — Upload + link to prescription
GET  /api/v1/reports/by-prescription/{id}    — Reports for a prescription
GET  /api/v1/reports/pending                 — Ordered but not uploaded
POST /api/v1/reports/{id}/nudge              — Doctor nudge for missing report
```

### Sprint 3.2 — Pre-Visit Summary (Week 8)

**Files to create:**
- `backend/app/services/pre_visit_service.py` — Auto-load patient summary before follow-up

**Endpoints:**
```
GET  /api/v1/doctors/pre-visit-summary/{patient_id}  — Summary for upcoming visit
GET  /api/v1/reports/ordered-vs-uploaded/{rx_id}      — Test status matrix
```

---

## Phase 4: Patient Health Timeline (Week 8-10) — P1

### Sprint 4.1 — Timeline API (Week 8-9)

**Files to create:**
- `backend/app/services/timeline_service.py` — Build chronological timeline
- `backend/app/api/routes/timeline.py` — Timeline endpoints
- `backend/app/schemas/timeline.py` — Timeline card schemas

**Endpoints:**
```
GET  /api/v1/timeline                        — Patient's complete health journey
GET  /api/v1/timeline/summary                — Health summary stats
GET  /api/v1/timeline/active-medicines       — Currently active medicines (cross-doctor)
```

### Sprint 4.2 — Patient Profile Enhancements (Week 9)

**Files to modify:**
- `backend/app/api/routes/patients.py` — Enhanced profile with allergies, chronic conditions
- `backend/app/schemas/patient.py` — Profile card schema

**Endpoints:**
```
GET  /api/v1/patients/profile-card           — Full profile card
PUT  /api/v1/patients/allergies              — Update allergies
PUT  /api/v1/patients/chronic-conditions     — Update chronic conditions
POST /api/v1/patients/export-health-pdf      — Export full health summary as PDF
POST /api/v1/patients/share-qr              — Generate 24-hour QR sharing code
```

### Sprint 4.3 — Trend Analysis (Week 10)

**Files to create:**
- `backend/app/services/trend_service.py` — Calculate trends from structured lab values

**Endpoints:**
```
GET  /api/v1/trends/{test_type}              — Value graph over time (HbA1c, BP, etc.)
GET  /api/v1/trends/summary                  — Improving/Stable/Worsening per metric
```

---

## Phase 5: Doctor AI Assistant (Week 10-13) — P1

### Sprint 5.1 — AI Service Foundation (Week 10-11)

**Files to create:**
- `backend/app/services/ai_service.py` — Google Gemini integration with PHI stripping
- `backend/app/services/drug_interaction.py` — Drug interaction checker
- `backend/app/services/dosage_reference.py` — Indian drug database reference
- `backend/app/models/ai.py` — AISuggestion, AIAuditLog models
- `backend/app/api/routes/ai_assistant.py` — AI endpoints

**PHI Protection:**
```python
# Before sending to Gemini:
# 1. Strip patient name, ID, ABHA
# 2. Send only: diagnosis, medicines, dosages, clinical terms
# 3. Log all AI interactions with session_id (no patient PII)
```

**Endpoints:**
```
POST /api/v1/ai/check-interactions           — Check drug interactions for Rx
POST /api/v1/ai/dosage-reference             — Get dosage range for medicine
POST /api/v1/ai/diagnosis-guidance           — First-line drugs per diagnosis
POST /api/v1/ai/suggest-follow-up            — Suggest follow-up duration
POST /api/v1/ai/suggest-tests                — Recommend tests for diagnosis
POST /api/v1/ai/chat                         — Free clinical question
POST /api/v1/ai/suggestions/{id}/action      — Log doctor action (used/dismissed)
```

### Sprint 5.2 — AI Audit Trail (Week 12)

**Files to create:**
- `backend/app/api/routes/ai_audit.py` — Audit trail endpoints

**Endpoints:**
```
GET  /api/v1/ai/audit-trail                  — All AI logs for current session
GET  /api/v1/ai/audit-trail/export           — Export for regulatory review
GET  /api/v1/ai/stats                        — Usage stats (suggestions vs actions)
```

### Sprint 5.3 — AI Integration with Prescription UI (Week 13)

This sprint focuses on connecting the AI service with the prescription writing flow.

**Logic:**
```
1. Doctor starts writing prescription
2. As medicine is typed → auto-check interactions with existing medicines
3. As diagnosis is entered → show first-line drug suggestions
4. On save → suggest follow-up duration + tests
5. All suggestions appear in right panel (slide-in)
6. Every suggestion + doctor action logged to audit trail
```

---

## Phase 6: Notifications & Communication (Week 13-15) — P0

### Sprint 6.1 — In-App Messaging (Week 13-14)

**Files to create:**
- `backend/app/models/message.py` — Message model
- `backend/app/api/routes/messages.py` — Messaging endpoints
- `backend/app/schemas/message.py` — Message schemas

**Endpoints:**
```
POST /api/v1/messages                        — Send message (doctor to patient)
GET  /api/v1/messages/conversation/{user_id} — Get conversation thread
GET  /api/v1/messages/unread                 — Unread messages count
POST /api/v1/messages/patient-request        — Pre-defined patient request
```

**Patient Request Types:**
```
- REQUEST_PRESCRIPTION_COPY
- ASK_ABOUT_MEDICINE
- REPORT_ISSUE
- REQUEST_EARLIER_APPOINTMENT
```

### Sprint 6.2 — Doctor-Patient Connect (Week 14-15)

**Files to create:**
- `backend/app/services/connect_service.py` — QR code generation, 6-digit codes
- `backend/app/api/routes/connections.py` — Connection endpoints

**Endpoints:**
```
POST /api/v1/connections/generate-code       — Doctor generates 6-digit code
POST /api/v1/connections/connect-by-code     — Patient connects using code
POST /api/v1/connections/generate-qr         — Generate QR for connection
GET  /api/v1/connections/my-doctors          — Patient's connected doctors
GET  /api/v1/connections/my-patients         — Doctor's connected patients
DELETE /api/v1/connections/{id}              — Disconnect
```

---

## Phase 7: Admin Panel & Compliance (Week 15-17) — P1

### Sprint 7.1 — Doctor Verification Queue (Week 15)

**Files to create:**
- `backend/app/services/nmc_verification.py` — NMC/State Council API integration
- `backend/app/api/routes/admin_verification.py` — Verification queue endpoints

**Endpoints:**
```
GET  /api/v1/admin/verification-queue        — Pending doctor verifications
POST /api/v1/admin/verify-doctor/{id}        — Approve doctor
POST /api/v1/admin/reject-doctor/{id}        — Reject with reason
GET  /api/v1/admin/verification-stats        — Queue stats
```

### Sprint 7.2 — DPDP & Consent Management (Week 16)

**Files to create:**
- `backend/app/services/consent_service.py` — Consent management
- `backend/app/services/erasure_service.py` — Data erasure workflow
- `backend/app/api/routes/consent.py` — Consent endpoints
- `backend/app/api/routes/erasure.py` — Erasure request endpoints

**Endpoints:**
```
POST /api/v1/consent/grant                   — Grant consent to doctor
POST /api/v1/consent/revoke                  — Revoke consent from doctor
GET  /api/v1/consent/my-consents             — Patient's active consents
GET  /api/v1/consent/audit-log               — Admin: consent audit log

POST /api/v1/erasure/request                 — Patient requests data erasure
GET  /api/v1/erasure/status/{id}             — Check request status
GET  /api/v1/admin/erasure-requests          — Admin: process requests
POST /api/v1/admin/erasure/{id}/process      — Admin: process an erasure
```

### Sprint 7.3 — Emergency Access & Reports (Week 17)

**Files to create:**
- `backend/app/services/emergency_access.py` — Break-the-Glass access
- `backend/app/services/report_generator.py` — Regulatory report generation
- `backend/app/api/routes/admin_reports.py` — Admin report endpoints

**Endpoints:**
```
POST /api/v1/emergency-access               — Doctor triggers emergency access
GET  /api/v1/admin/emergency-access-log      — All emergency access events
POST /api/v1/admin/emergency-review/{id}     — Review an emergency access

GET  /api/v1/admin/reports/monthly-doctors   — Monthly active doctor report
GET  /api/v1/admin/reports/consent-audit     — Consent audit report
GET  /api/v1/admin/reports/erasure           — Erasure compliance report
GET  /api/v1/admin/reports/emergency-access  — Emergency access report
GET  /api/v1/admin/reports/ai-usage          — AI usage & safety report
GET  /api/v1/admin/reports/security          — Security incidents report
```

---

## Phase 8: Flutter Mobile App (Week 12-20) — P0

> Runs in parallel with Phase 5-7 backend work.

### Sprint 8.1 — Project Setup & Auth (Week 12-13)

**Folder structure:**
```
symptotrack_mobile/
├── lib/
│   ├── main.dart
│   ├── app/
│   │   ├── routes.dart
│   │   ├── theme.dart
│   │   └── constants.dart
│   ├── core/
│   │   ├── api/
│   │   │   ├── api_client.dart         — Dio + interceptors
│   │   │   └── api_endpoints.dart
│   │   ├── auth/
│   │   │   ├── auth_service.dart
│   │   │   └── token_manager.dart
│   │   └── storage/
│   │       └── secure_storage.dart
│   ├── features/
│   │   ├── auth/
│   │   ├── onboarding/
│   │   ├── prescriptions/
│   │   ├── reminders/
│   │   ├── reports/
│   │   ├── timeline/
│   │   ├── ai_assistant/
│   │   ├── messages/
│   │   └── settings/
│   └── shared/
│       ├── widgets/
│       └── utils/
├── pubspec.yaml
└── README.md
```

**Key packages:**
```yaml
dependencies:
  dio: ^5.0.0                    # HTTP client
  flutter_riverpod: ^2.0.0       # State management
  go_router: ^14.0.0             # Navigation
  flutter_secure_storage: ^9.0.0 # Token storage
  firebase_messaging: ^15.0.0    # Push notifications
  local_auth: ^2.0.0             # Biometric login
  qr_code_scanner: ^1.0.0        # QR code scanning
  qr_flutter: ^4.0.0             # QR code generation
  flutter_local_notifications: ^18.0.0
```

### Sprint 8.2 — Patient Screens (Week 14-16)
```
- Prescription list + detail view
- Reminder dashboard (color-coded)
- Medicine reminder with snooze
- Reports upload (camera/PDF)
- Health timeline
- Doctor connection (QR/code)
- Settings & notification preferences
```

### Sprint 8.3 — Doctor Screens (Week 16-18)
```
- Prescription writing screen
- AI assistant panel (slide-in)
- Patient chart with pre-visit summary
- Digital signature setup
- Template and favorites management
- Patient messaging
```

### Sprint 8.4 — Push Notifications & Offline (Week 18-20)
```
- FCM integration
- Local notifications for reminders
- Background task for scheduled reminders
- Offline prescription viewing
- Lock screen privacy (no medicine names)
```

---

## Phase 9: ABDM Integration (Week 18-20) — P0

### Sprint 9.1 — ABHA Linking (Week 18-19)

**Files to create:**
- `backend/app/services/abdm_service.py` — ABDM Sandbox API integration
- `backend/app/api/routes/abdm.py` — ABHA endpoints

**Endpoints:**
```
POST /api/v1/abdm/create-abha               — Create new ABHA ID
POST /api/v1/abdm/link-abha                 — Link existing ABHA
POST /api/v1/abdm/verify-abha               — Verify ABHA OTP
GET  /api/v1/abdm/health-records             — Pull records from ABDM
```

### Sprint 9.2 — FHIR R4 Mapping (Week 19-20)

**Files to create:**
- `backend/app/services/fhir_service.py` — FHIR R4 resource mapping
- `backend/app/services/fhir_mapper.py` — Transform internal models → FHIR R4

**FHIR Resources to map:**
```
- Patient → FHIR Patient resource
- Prescription → FHIR MedicationRequest
- Consultation → FHIR Encounter
- Medical Report → FHIR DiagnosticReport
- Allergy → FHIR AllergyIntolerance
```

---

## Phase 10: Integration Testing & Launch Prep (Week 20-22)

### Sprint 10.1 — End-to-End Testing (Week 20-21)
```
- API integration tests (pytest)
- Flutter widget tests + integration tests
- Prescription → Reminder → Notification flow test
- Consent grant → revoke → erasure flow test
- AI suggestion → doctor action → audit trail test
- Multi-channel notification fallback test
```

### Sprint 10.2 — Security & Performance (Week 21-22)
```
- Penetration testing (OWASP top 10)
- Load testing (locust)
- AES-256 at-rest encryption for sensitive fields
- Session timeout enforcement
- Rate limiting on OTP endpoints
- API response time optimization (<3s for AI)
- Push notification delivery <30s
```

### Sprint 10.3 — Deployment & Go-Live (Week 22)
```
- Docker production configs
- CI/CD pipeline (GitHub Actions)
- Database migration scripts (Alembic)
- Flutter app builds (APK + AAB + iOS)
- Play Store / App Store submission
- Production monitoring setup (Sentry + Prometheus)
```

---

## Implementation Order (What to Build When)

| Week | Backend | Frontend/Mobile | Deliverable |
|------|---------|-----------------|-------------|
| 1 | DB schema migration | — | New tables + migration scripts |
| 2 | OTP auth + session timeout | — | OTP login working |
| 3 | Prescription signing + PDF | — | Signed prescription PDF |
| 4 | Templates + favorites | — | Template-based prescription |
| 5 | Tests ordered + reminder core | — | Reminders auto-generated |
| 6 | Reminder scheduler + triggers | — | Reminders fire on schedule |
| 7 | Multi-channel notifications | — | Push → SMS → WhatsApp |
| 8 | Report linking + pre-visit | — | Reports linked to Rx |
| 9 | Timeline + profile enhancements | — | Health timeline API |
| 10 | Trend analysis | — | Test value graphs |
| 10-11 | AI service (Gemini) | — | Drug interactions working |
| 12 | AI audit trail | Flutter setup + auth | AI logs exportable |
| 13 | AI + Rx integration, messaging | Flutter patient screens | AI in prescription flow |
| 14-15 | Connect system | Flutter patient screens | QR/code connection |
| 15 | Admin verification queue | — | Doctor verification flow |
| 16 | DPDP consent + erasure | Flutter doctor screens | Consent management |
| 17 | Emergency access + reports | Flutter doctor screens | Admin compliance |
| 18-19 | ABDM integration | Flutter push + offline | ABHA linking |
| 19-20 | FHIR R4 mapping | Flutter polish | FHIR compliant |
| 20-22 | Testing + security + deploy | Flutter app release | Production launch |

---

## Files to Create (Summary)

### Backend — New Files (~35 files)

**Models (5):**
- `app/models/reminder.py`
- `app/models/ai.py`
- `app/models/message.py`
- `app/models/consent.py`
- `app/models/prescription_extras.py`

**Services (15):**
- `app/services/otp_service.py`
- `app/services/prescription_service.py`
- `app/services/pdf_generator.py`
- `app/services/signature_service.py`
- `app/services/reminder_service.py`
- `app/services/reminder_scheduler.py`
- `app/services/push_notification.py`
- `app/services/whatsapp_service.py`
- `app/services/pre_visit_service.py`
- `app/services/timeline_service.py`
- `app/services/trend_service.py`
- `app/services/ai_service.py`
- `app/services/drug_interaction.py`
- `app/services/dosage_reference.py`
- `app/services/connect_service.py`
- `app/services/nmc_verification.py`
- `app/services/consent_service.py`
- `app/services/erasure_service.py`
- `app/services/emergency_access.py`
- `app/services/report_generator.py`
- `app/services/abdm_service.py`
- `app/services/fhir_service.py`
- `app/services/fhir_mapper.py`

**API Routes (12):**
- `app/api/routes/onboarding.py`
- `app/api/routes/templates.py`
- `app/api/routes/favorites.py`
- `app/api/routes/reminders.py`
- `app/api/routes/notification_preferences.py`
- `app/api/routes/timeline.py`
- `app/api/routes/ai_assistant.py`
- `app/api/routes/ai_audit.py`
- `app/api/routes/messages.py`
- `app/api/routes/connections.py`
- `app/api/routes/consent.py`
- `app/api/routes/erasure.py`
- `app/api/routes/admin_verification.py`
- `app/api/routes/admin_reports.py`
- `app/api/routes/abdm.py`

**Schemas (5):**
- `app/schemas/reminder.py`
- `app/schemas/timeline.py`
- `app/schemas/message.py`
- `app/schemas/consent.py`
- `app/schemas/ai.py`

### Flutter — New Project (~60+ files)
- Complete Flutter project for Android + iOS
- See Phase 8 for detailed structure

---

## Configuration Requirements

### New Environment Variables (backend/.env)
```
# OTP
OTP_LENGTH=6
OTP_EXPIRY_MINUTES=5
OTP_MAX_ATTEMPTS=5
OTP_LOCKOUT_MINUTES=30

# Google Gemini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-pro

# Firebase (Push Notifications)
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# WhatsApp Business API
WHATSAPP_API_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=

# ABDM
ABDM_CLIENT_ID=
ABDM_CLIENT_SECRET=
ABDM_BASE_URL=https://dev.abdm.gov.in/gateway

# Session
DOCTOR_SESSION_TIMEOUT_MINUTES=10
PATIENT_SESSION_TIMEOUT_MINUTES=30

# Security
ENCRYPTION_KEY=    # AES-256 key for at-rest encryption
SIGNATURE_PIN_SALT=
```

---

## Risk & Dependencies

| Risk | Mitigation |
|------|-----------|
| ABDM Sandbox may have downtime | Mock ABDM responses for dev, test on sandbox periodically |
| NMC API may not exist publicly | Build manual verification queue as fallback |
| Gemini may hallucinate drug interactions | Cross-reference with Indian drug database, label "suggestive only" |
| FCM token management complexity | Use Firebase Admin SDK with proper token refresh |
| WhatsApp API approval takes time | Start with Push + SMS only, add WhatsApp when approved |
| Flutter learning curve | Start with auth/list screens, build complexity gradually |

---

## Getting Started — First Task

**Ready to begin with Phase 0, Sprint 0.1: Database Schema Extensions.**

This creates all the new tables and columns needed, which every other feature depends on. I'll create:
1. Alembic migration setup (for versioned DB migrations)
2. New SQLAlchemy models
3. Database migration script

Shall I proceed?
