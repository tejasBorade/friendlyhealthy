-- ============================================================
-- SymptoTrack PRD v1.0 - Database Migration (INTEGER-based)
-- From: Healthcare Management Platform v1.0
-- To: SymptoTrack-compliant schema
-- Date: 2026-02-26
-- ============================================================
-- This migration adds 18 new tables using INTEGER IDs to match
-- the existing database schema.
-- ============================================================

BEGIN;

-- ============================================================
-- 1. ALTER EXISTING TABLES — Add new columns
-- ============================================================

-- Users: OTP-based auth fields
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20) UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS otp_hash VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS otp_expires_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_otp_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_device_info JSONB;

-- Patients: ABHA & health profile
ALTER TABLE patients ADD COLUMN IF NOT EXISTS abha_id VARCHAR(50) UNIQUE;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS abha_address VARCHAR(100);
ALTER TABLE patients ADD COLUMN IF NOT EXISTS known_allergies TEXT;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS chronic_conditions TEXT;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS caregiver_name VARCHAR(200);
ALTER TABLE patients ADD COLUMN IF NOT EXISTS caregiver_phone VARCHAR(20);

-- Doctors: Clinic, NMC, signature
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS clinic_name VARCHAR(200);
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS clinic_address TEXT;
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS clinic_logo VARCHAR(500);
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS nmc_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS nmc_verified_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS digital_signature_path VARCHAR(500);
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS state_medical_council VARCHAR(100);
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS hfr_id VARCHAR(50);

-- Prescriptions: Signing, PDF, follow-up
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS follow_up_date DATE;
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS patient_instructions TEXT;
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS is_signed BOOLEAN DEFAULT FALSE;
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS signed_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS pdf_path VARCHAR(500);
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS is_locked BOOLEAN DEFAULT FALSE;
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS diagnosis_icd10_code VARCHAR(20);
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS diagnosis_patient_friendly TEXT;

-- ============================================================
-- 2. NEW TABLES — Tests Ordered
-- ============================================================

CREATE TABLE IF NOT EXISTS tests_ordered (
    id SERIAL PRIMARY KEY,
    prescription_id INTEGER NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
    test_name VARCHAR(200) NOT NULL,
    test_type VARCHAR(100),
    notes TEXT,
    due_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'ordered'
        CHECK(status IN ('ordered', 'uploaded', 'missing')),
    report_id INTEGER REFERENCES reports(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Reports: Link to prescription and test order (if reports table exists)
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'reports') THEN
        ALTER TABLE reports ADD COLUMN IF NOT EXISTS prescription_id INTEGER REFERENCES prescriptions(id) ON DELETE SET NULL;
        ALTER TABLE reports ADD COLUMN IF NOT EXISTS test_order_id INTEGER REFERENCES tests_ordered(id) ON DELETE SET NULL;
        ALTER TABLE reports ADD COLUMN IF NOT EXISTS follow_up_date DATE;
        ALTER TABLE reports ADD COLUMN IF NOT EXISTS structured_values JSONB;
    END IF;
END $$;

-- ============================================================
-- 3. NEW TABLES — Digital Signatures
-- ============================================================

CREATE TABLE IF NOT EXISTS digital_signatures (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER UNIQUE NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    signature_image_path VARCHAR(500) NOT NULL,
    signature_pin_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prescription_signatures (
    id SERIAL PRIMARY KEY,
    prescription_id INTEGER UNIQUE NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
    signature_id INTEGER NOT NULL REFERENCES digital_signatures(id) ON DELETE CASCADE,
    signed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_locked BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- 4. NEW TABLES — Reminders
-- ============================================================

CREATE TABLE IF NOT EXISTS medicine_reminders (
    id SERIAL PRIMARY KEY,
    prescription_id INTEGER NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    medicine_name VARCHAR(200) NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    frequency_code VARCHAR(50) NOT NULL,
    timing_slots JSONB NOT NULL DEFAULT '[]',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK(status IN ('active', 'completed', 'snoozed', 'missed', 'cancelled')),
    is_active BOOLEAN DEFAULT TRUE,
    is_critical BOOLEAN DEFAULT FALSE,
    snooze_count INTEGER DEFAULT 0,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    total_taken INTEGER DEFAULT 0,
    total_missed INTEGER DEFAULT 0,
    custom_note VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS medicine_reminder_logs (
    id SERIAL PRIMARY KEY,
    reminder_id INTEGER NOT NULL REFERENCES medicine_reminders(id) ON DELETE CASCADE,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    action VARCHAR(20) NOT NULL CHECK(action IN ('taken', 'missed', 'snoozed')),
    action_time TIMESTAMP WITH TIME ZONE,
    snoozed_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS follow_up_reminders (
    id SERIAL PRIMARY KEY,
    prescription_id INTEGER NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    follow_up_date DATE NOT NULL,
    reminder_7day_sent BOOLEAN DEFAULT FALSE,
    reminder_7day_sent_at TIMESTAMP WITH TIME ZONE,
    reminder_1day_sent BOOLEAN DEFAULT FALSE,
    reminder_1day_sent_at TIMESTAMP WITH TIME ZONE,
    reminder_morning_sent BOOLEAN DEFAULT FALSE,
    reminder_morning_sent_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL DEFAULT 'upcoming'
        CHECK(status IN ('upcoming', 'visited', 'missed', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS test_reminders (
    id SERIAL PRIMARY KEY,
    prescription_id INTEGER NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
    test_order_id INTEGER NOT NULL REFERENCES tests_ordered(id) ON DELETE CASCADE,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    test_name VARCHAR(200) NOT NULL,
    follow_up_date DATE,
    reminder_3day_sent BOOLEAN DEFAULT FALSE,
    reminder_3day_sent_at TIMESTAMP WITH TIME ZONE,
    reminder_1day_sent BOOLEAN DEFAULT FALSE,
    reminder_1day_sent_at TIMESTAMP WITH TIME ZONE,
    upload_status VARCHAR(20) NOT NULL DEFAULT 'ordered'
        CHECK(upload_status IN ('ordered', 'uploaded', 'missing')),
    report_id INTEGER REFERENCES reports(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 5. NEW TABLES — Consent & Compliance (DPDP Act)
-- ============================================================

CREATE TABLE IF NOT EXISTS consent_records (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    consent_type VARCHAR(50) NOT NULL
        CHECK(consent_type IN (
            'view_records', 'view_reports', 'view_prescriptions',
            'share_timeline', 'emergency_access', 'abdm_data_pull', 'ai_processing'
        )),
    purpose TEXT NOT NULL,
    duration_days INTEGER,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    device_info JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS emergency_access_logs (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    justification TEXT NOT NULL,
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    review_status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK(review_status IN ('pending', 'approved', 'flagged')),
    review_notes TEXT,
    patient_notified BOOLEAN DEFAULT FALSE,
    patient_notified_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS data_erasure_requests (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deadline_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'requested'
        CHECK(status IN ('requested', 'in_progress', 'completed', 'partially_completed', 'rejected')),
    processed_at TIMESTAMP WITH TIME ZONE,
    processed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    processing_notes TEXT,
    data_retained_reason TEXT,
    erasure_report JSONB,
    confirmation_sent BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS doctor_verifications (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER UNIQUE NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    nmc_registration_number VARCHAR(100) NOT NULL,
    state_council VARCHAR(100),
    verification_status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK(verification_status IN ('pending', 'verified', 'rejected', 'manual_review')),
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP WITH TIME ZONE,
    verified_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    rejection_reason TEXT,
    appeal_text TEXT,
    appeal_submitted_at TIMESTAMP WITH TIME ZONE,
    nmc_api_response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 6. NEW TABLES — AI Assistant
-- ============================================================

CREATE TABLE IF NOT EXISTS ai_sessions (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    patient_context_hash VARCHAR(64),
    prescription_id INTEGER REFERENCES prescriptions(id) ON DELETE SET NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    total_suggestions INTEGER DEFAULT 0,
    suggestions_used INTEGER DEFAULT 0,
    suggestions_dismissed INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ai_suggestions (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES ai_sessions(id) ON DELETE CASCADE,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    suggestion_type VARCHAR(30) NOT NULL
        CHECK(suggestion_type IN (
            'drug_interaction', 'dosage_reference', 'diagnosis_guidance',
            'follow_up_suggestion', 'test_suggestion', 'free_chat'
        )),
    input_context JSONB,
    suggestion_text TEXT NOT NULL,
    suggestion_data JSONB,
    reference_links JSONB,
    ai_model VARCHAR(50),
    ai_status VARCHAR(20) DEFAULT 'success'
        CHECK(ai_status IN ('success', 'failed', 'fallback', 'timeout')),
    response_time_ms INTEGER,
    doctor_action VARCHAR(20) DEFAULT 'pending'
        CHECK(doctor_action IN ('used', 'dismissed', 'noted', 'pending')),
    doctor_action_at TIMESTAMP WITH TIME ZONE,
    doctor_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 7. NEW TABLES — Messaging & Connections
-- ============================================================

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receiver_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    prescription_id INTEGER REFERENCES prescriptions(id) ON DELETE SET NULL,
    message_type VARCHAR(30) NOT NULL
        CHECK(message_type IN (
            'prescription_followup', 'report_request', 'followup_confirmation',
            'custom_clinical', 'patient_request', 'system'
        )),
    patient_request_type VARCHAR(40)
        CHECK(patient_request_type IS NULL OR patient_request_type IN (
            'request_prescription_copy', 'ask_about_medicine',
            'report_issue', 'request_earlier_appointment'
        )),
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    is_ai_drafted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS doctor_patient_connections (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    connect_code VARCHAR(10),
    connection_method VARCHAR(20) NOT NULL
        CHECK(connection_method IN ('qr', 'code', 'search', 'prescription')),
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    disconnected_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 8. NEW TABLES — Prescription Extras
-- ============================================================

CREATE TABLE IF NOT EXISTS doctor_medicine_favorites (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    medicine_name VARCHAR(200) NOT NULL,
    dosage VARCHAR(100),
    frequency VARCHAR(50),
    usage_instructions TEXT,
    duration_days INTEGER,
    category VARCHAR(100),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prescription_templates (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    template_name VARCHAR(200) NOT NULL,
    diagnosis TEXT NOT NULL,
    diagnosis_icd10_code VARCHAR(20),
    medicines JSONB NOT NULL DEFAULT '[]',
    tests JSONB DEFAULT '[]',
    instructions TEXT,
    follow_up_days INTEGER,
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 9. NEW TABLES — Notification Preferences & Device Tokens
-- ============================================================

CREATE TABLE IF NOT EXISTS notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    medicine_reminders BOOLEAN DEFAULT TRUE,
    follow_up_reminders BOOLEAN DEFAULT TRUE,
    test_reminders BOOLEAN DEFAULT TRUE,
    doctor_messages BOOLEAN DEFAULT TRUE,
    report_alerts BOOLEAN DEFAULT TRUE,
    security_alerts BOOLEAN DEFAULT TRUE,
    quiet_hours_enabled BOOLEAN DEFAULT TRUE,
    quiet_hours_start TIME DEFAULT '22:00',
    quiet_hours_end TIME DEFAULT '07:00',
    preferred_channel VARCHAR(20) DEFAULT 'push'
        CHECK(preferred_channel IN ('push', 'sms', 'whatsapp')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS device_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_token VARCHAR(500) UNIQUE NOT NULL,
    platform VARCHAR(10) NOT NULL CHECK(platform IN ('android', 'ios', 'web')),
    device_info JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================
-- 10. NEW INDEXES
-- ============================================================

-- Users
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);

-- Patients
CREATE INDEX IF NOT EXISTS idx_patients_abha ON patients(abha_id);

-- Doctors
CREATE INDEX IF NOT EXISTS idx_doctors_nmc ON doctors(nmc_verified);

-- Prescriptions
CREATE INDEX IF NOT EXISTS idx_prescriptions_follow_up ON prescriptions(follow_up_date);
CREATE INDEX IF NOT EXISTS idx_prescriptions_signed ON prescriptions(is_signed);

-- Tests Ordered
CREATE INDEX IF NOT EXISTS idx_tests_ordered_prescription ON tests_ordered(prescription_id);
CREATE INDEX IF NOT EXISTS idx_tests_ordered_status ON tests_ordered(status);

-- Medicine Reminders
CREATE INDEX IF NOT EXISTS idx_medicine_reminders_patient ON medicine_reminders(patient_id);
CREATE INDEX IF NOT EXISTS idx_medicine_reminders_prescription ON medicine_reminders(prescription_id);
CREATE INDEX IF NOT EXISTS idx_medicine_reminders_active ON medicine_reminders(is_active);
CREATE INDEX IF NOT EXISTS idx_medicine_reminders_dates ON medicine_reminders(start_date, end_date);

-- Medicine Reminder Logs
CREATE INDEX IF NOT EXISTS idx_reminder_logs_reminder ON medicine_reminder_logs(reminder_id);
CREATE INDEX IF NOT EXISTS idx_reminder_logs_scheduled ON medicine_reminder_logs(scheduled_time);

-- Follow-up Reminders
CREATE INDEX IF NOT EXISTS idx_followup_reminders_patient ON follow_up_reminders(patient_id);
CREATE INDEX IF NOT EXISTS idx_followup_reminders_date ON follow_up_reminders(follow_up_date);
CREATE INDEX IF NOT EXISTS idx_followup_reminders_status ON follow_up_reminders(status);

-- Test Reminders
CREATE INDEX IF NOT EXISTS idx_test_reminders_patient ON test_reminders(patient_id);
CREATE INDEX IF NOT EXISTS idx_test_reminders_status ON test_reminders(upload_status);

-- Consent Records
CREATE INDEX IF NOT EXISTS idx_consent_patient ON consent_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_consent_doctor ON consent_records(doctor_id);
CREATE INDEX IF NOT EXISTS idx_consent_active ON consent_records(is_active);

-- Emergency Access
CREATE INDEX IF NOT EXISTS idx_emergency_doctor ON emergency_access_logs(doctor_id);
CREATE INDEX IF NOT EXISTS idx_emergency_patient ON emergency_access_logs(patient_id);
CREATE INDEX IF NOT EXISTS idx_emergency_review ON emergency_access_logs(review_status);

-- Data Erasure
CREATE INDEX IF NOT EXISTS idx_erasure_patient ON data_erasure_requests(patient_id);
CREATE INDEX IF NOT EXISTS idx_erasure_status ON data_erasure_requests(status);
CREATE INDEX IF NOT EXISTS idx_erasure_deadline ON data_erasure_requests(deadline_date);

-- Doctor Verification
CREATE INDEX IF NOT EXISTS idx_verification_doctor ON doctor_verifications(doctor_id);
CREATE INDEX IF NOT EXISTS idx_verification_status ON doctor_verifications(verification_status);

-- AI Sessions
CREATE INDEX IF NOT EXISTS idx_ai_sessions_doctor ON ai_sessions(doctor_id);

-- AI Suggestions
CREATE INDEX IF NOT EXISTS idx_ai_suggestions_session ON ai_suggestions(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_suggestions_doctor ON ai_suggestions(doctor_id);
CREATE INDEX IF NOT EXISTS idx_ai_suggestions_type ON ai_suggestions(suggestion_type);
CREATE INDEX IF NOT EXISTS idx_ai_suggestions_action ON ai_suggestions(doctor_action);

-- Messages
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id);
CREATE INDEX IF NOT EXISTS idx_messages_read ON messages(is_read);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);

-- Connections
CREATE INDEX IF NOT EXISTS idx_connections_doctor ON doctor_patient_connections(doctor_id);
CREATE INDEX IF NOT EXISTS idx_connections_patient ON doctor_patient_connections(patient_id);
CREATE INDEX IF NOT EXISTS idx_connections_active ON doctor_patient_connections(is_active);

-- Favorites
CREATE INDEX IF NOT EXISTS idx_favorites_doctor ON doctor_medicine_favorites(doctor_id);

-- Templates
CREATE INDEX IF NOT EXISTS idx_templates_doctor ON prescription_templates(doctor_id);

-- Notification Preferences
CREATE INDEX IF NOT EXISTS idx_notif_prefs_user ON notification_preferences(user_id);

-- Device Tokens
CREATE INDEX IF NOT EXISTS idx_device_tokens_user ON device_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_device_tokens_active ON device_tokens(is_active);

-- ============================================================
-- 11. COMMENTS ON NEW TABLES
-- ============================================================

COMMENT ON TABLE tests_ordered IS 'Tests ordered within a prescription, tracks upload lifecycle';
COMMENT ON TABLE digital_signatures IS 'Doctor PIN-protected digital signatures';
COMMENT ON TABLE prescription_signatures IS 'Links signature to signed prescription (immutable)';
COMMENT ON TABLE medicine_reminders IS 'Auto-generated medicine reminders from prescriptions';
COMMENT ON TABLE medicine_reminder_logs IS 'Individual reminder event log (taken/missed/snoozed)';
COMMENT ON TABLE follow_up_reminders IS 'Follow-up visit reminders (7-day, 1-day, morning-of)';
COMMENT ON TABLE test_reminders IS 'Test completion reminders before follow-up';
COMMENT ON TABLE consent_records IS 'DPDP Act consent tracking (immutable audit log)';
COMMENT ON TABLE emergency_access_logs IS 'Break-the-Glass emergency access audit trail';
COMMENT ON TABLE data_erasure_requests IS 'DPDP right to erasure workflow (30-day deadline)';
COMMENT ON TABLE doctor_verifications IS 'NMC/State Council verification queue';
COMMENT ON TABLE ai_sessions IS 'AI assistant session grouping for audit';
COMMENT ON TABLE ai_suggestions IS 'AI suggestion audit trail (no PII)';
COMMENT ON TABLE messages IS 'Doctor-patient in-app messaging';
COMMENT ON TABLE doctor_patient_connections IS 'Doctor-patient connection via QR/code/search';
COMMENT ON TABLE doctor_medicine_favorites IS 'Doctor personal medicine quick-select list';
COMMENT ON TABLE prescription_templates IS 'Reusable prescription templates for common diagnoses';
COMMENT ON TABLE notification_preferences IS 'Per-user notification channel and toggle settings';
COMMENT ON TABLE device_tokens IS 'FCM/APNS push notification device tokens';

COMMIT;
