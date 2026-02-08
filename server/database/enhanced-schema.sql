-- Enhanced Healthcare Management Platform Database Schema
-- Comprehensive schema with all required features

-- =====================================================
-- 1. ENHANCED DOCTORS TABLE
-- =====================================================
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS clinic_name VARCHAR(255);
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS clinic_address TEXT;
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS clinic_phone VARCHAR(20);
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS hospital_affiliation VARCHAR(255);
ALTER TABLE doctors ADD COLUMN IF NOT EXISTS license_number VARCHAR(100);

-- =====================================================
-- 2. DOCTOR TIME SLOTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS doctor_time_slots (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6), -- 0=Sunday, 6=Saturday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_duration INTEGER DEFAULT 30, -- minutes
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 3. ENHANCED APPOINTMENTS TABLE
-- =====================================================
ALTER TABLE appointments ADD COLUMN IF NOT EXISTS status_updated_at TIMESTAMP;
ALTER TABLE appointments ADD COLUMN IF NOT EXISTS cancellation_reason TEXT;
ALTER TABLE appointments ADD COLUMN IF NOT EXISTS rescheduled_from INTEGER REFERENCES appointments(id);
ALTER TABLE appointments DROP CONSTRAINT IF EXISTS appointments_status_check;
ALTER TABLE appointments ADD CONSTRAINT appointments_status_check 
    CHECK (status IN ('booked', 'confirmed', 'completed', 'cancelled', 'no-show', 'rejected'));

-- =====================================================
-- 4. ENHANCED MEDICAL RECORDS TABLE
-- =====================================================
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS allergies TEXT;
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS chronic_diseases TEXT;
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS surgeries TEXT;
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS family_history TEXT;
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS blood_pressure VARCHAR(20);
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS temperature DECIMAL(5,2);
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS weight DECIMAL(5,2);
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS height DECIMAL(5,2);

-- =====================================================
-- 5. ENHANCED PRESCRIPTIONS TABLE
-- =====================================================
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS usage_timing VARCHAR(50); -- before_food, after_food, with_food
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS frequency_pattern VARCHAR(20); -- e.g., 1-0-1 (morning-afternoon-evening)
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS parent_prescription_id INTEGER REFERENCES prescriptions(id);
ALTER TABLE prescriptions ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- =====================================================
-- 6. BILLING & INVOICES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE SET NULL,
    appointment_id INTEGER REFERENCES appointments(id) ON DELETE SET NULL,
    invoice_date DATE DEFAULT CURRENT_DATE,
    due_date DATE,
    subtotal DECIMAL(10, 2) NOT NULL DEFAULT 0,
    tax_rate DECIMAL(5, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    discount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'partially_paid', 'overdue', 'cancelled')),
    payment_method VARCHAR(50),
    payment_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 7. INVOICE ITEMS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS invoice_items (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES invoices(id) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL, -- consultation, test, checkup, followup
    item_name VARCHAR(255) NOT NULL,
    description TEXT,
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 8. ENHANCED REPORTS TABLE
-- =====================================================
ALTER TABLE reports ADD COLUMN IF NOT EXISTS test_name VARCHAR(255);
ALTER TABLE reports ADD COLUMN IF NOT EXISTS lab_name VARCHAR(255);
ALTER TABLE reports ADD COLUMN IF NOT EXISTS lab_address TEXT;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS lab_phone VARCHAR(20);
ALTER TABLE reports ADD COLUMN IF NOT EXISTS doctor_remarks TEXT;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS test_results JSONB; -- Store structured test results

-- =====================================================
-- 9. NOTIFICATIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL, -- appointment_reminder, prescription_ready, payment_due, etc.
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    is_read BOOLEAN DEFAULT false,
    is_sent BOOLEAN DEFAULT false,
    send_via VARCHAR(50), -- email, sms, push, in_app
    scheduled_time TIMESTAMP,
    sent_at TIMESTAMP,
    reference_type VARCHAR(50), -- appointment, prescription, invoice, etc.
    reference_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 10. AUDIT LOGS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL, -- create, update, delete, view
    entity_type VARCHAR(50) NOT NULL, -- medical_record, prescription, invoice, etc.
    entity_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 11. PATIENT CONSENT TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS patient_consents (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    consent_type VARCHAR(100) NOT NULL, -- data_sharing, teleconsultation, treatment, research
    consent_text TEXT NOT NULL,
    is_granted BOOLEAN NOT NULL,
    granted_at TIMESTAMP,
    revoked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 12. SYSTEM SETTINGS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50), -- string, number, boolean, json
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- CREATE INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_doctor_time_slots_doctor ON doctor_time_slots(doctor_id);
CREATE INDEX IF NOT EXISTS idx_invoices_patient ON invoices(patient_id);
CREATE INDEX IF NOT EXISTS idx_invoices_invoice_number ON invoices(invoice_number);
CREATE INDEX IF NOT EXISTS idx_invoices_payment_status ON invoices(payment_status);
CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice ON invoice_items(invoice_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_patient_consents_patient ON patient_consents(patient_id);

-- =====================================================
-- INSERT DEFAULT SYSTEM SETTINGS
-- =====================================================
INSERT INTO system_settings (setting_key, setting_value, setting_type, description)
VALUES 
    ('default_tax_rate', '18', 'number', 'Default GST/Tax rate percentage'),
    ('appointment_slot_duration', '30', 'number', 'Default appointment duration in minutes'),
    ('payment_reminder_days', '3', 'number', 'Days before payment due to send reminder'),
    ('appointment_reminder_hours', '24', 'number', 'Hours before appointment to send reminder')
ON CONFLICT (setting_key) DO NOTHING;

-- =====================================================
-- UPDATE SEQUENCE FOR INVOICE NUMBERS
-- =====================================================
CREATE SEQUENCE IF NOT EXISTS invoice_number_seq START 10001;
