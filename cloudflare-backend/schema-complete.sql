-- ============================================================
-- Healthcare Management Platform - Cloudflare D1 Database Schema
-- Converted from PostgreSQL to SQLite
-- Version: 2.0
-- Date: 2026-02-19
-- ============================================================

-- ============================================================
-- USER MANAGEMENT
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('patient', 'doctor', 'admin')),
    is_active INTEGER DEFAULT 1,
    is_verified INTEGER DEFAULT 0,
    last_login TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    is_deleted INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    gender TEXT NOT NULL CHECK(gender IN ('male', 'female', 'other')),
    phone TEXT NOT NULL,
    alternate_phone TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    country TEXT DEFAULT 'India',
    emergency_contact_name TEXT,
    emergency_contact_phone TEXT,
    blood_group TEXT,
    profile_picture TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS specializations (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    icon TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS doctors (
    id TEXT PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    gender TEXT NOT NULL CHECK(gender IN ('male', 'female', 'other')),
    phone TEXT NOT NULL,
    registration_number TEXT UNIQUE NOT NULL,
    qualification TEXT NOT NULL,
    experience_years INTEGER NOT NULL CHECK (experience_years >= 0),
    consultation_fee REAL NOT NULL CHECK (consultation_fee >= 0),
    about TEXT,
    profile_picture TEXT,
    is_verified INTEGER DEFAULT 0,
    rating REAL DEFAULT 0.00 CHECK (rating >= 0 AND rating <= 5),
    total_reviews INTEGER DEFAULT 0,
    clinic_name TEXT,
    clinic_address TEXT,
    clinic_phone TEXT,
    hospital_affiliation TEXT,
    license_number TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS doctor_specializations (
    id TEXT PRIMARY KEY,
    doctor_id TEXT NOT NULL,
    specialization_id TEXT NOT NULL,
    is_primary INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    FOREIGN KEY (specialization_id) REFERENCES specializations(id) ON DELETE CASCADE,
    UNIQUE(doctor_id, specialization_id)
);

CREATE TABLE IF NOT EXISTS clinics (
    id TEXT PRIMARY KEY,
    doctor_id TEXT NOT NULL,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip_code TEXT,
    phone TEXT,
    is_primary INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

-- ============================================================
-- AVAILABILITY & SCHEDULING
-- ============================================================

CREATE TABLE IF NOT EXISTS doctor_availability (
    id TEXT PRIMARY KEY,
    doctor_id TEXT NOT NULL,
    clinic_id TEXT,
    day_of_week TEXT NOT NULL CHECK(day_of_week IN ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    slot_duration INTEGER NOT NULL DEFAULT 30,
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    FOREIGN KEY (clinic_id) REFERENCES clinics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS doctor_leaves (
    id TEXT PRIMARY KEY,
    doctor_id TEXT NOT NULL,
    from_date TEXT NOT NULL,
    to_date TEXT NOT NULL,
    reason TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

-- ============================================================
-- APPOINTMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS appointments (
    id TEXT PRIMARY KEY,
    appointment_number TEXT UNIQUE NOT NULL,
    patient_id TEXT NOT NULL,
    doctor_id TEXT NOT NULL,
    clinic_id TEXT,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    duration INTEGER DEFAULT 30,
    status TEXT DEFAULT 'booked' CHECK(status IN ('booked', 'confirmed', 'completed', 'cancelled', 'rejected', 'no-show')),
    reason_for_visit TEXT,
    symptoms TEXT,
    doctor_notes TEXT,
    cancellation_reason TEXT,
    cancelled_by TEXT,
    cancelled_at TEXT,
    status_updated_at TEXT,
    rescheduled_from TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    FOREIGN KEY (clinic_id) REFERENCES clinics(id) ON DELETE SET NULL,
    FOREIGN KEY (cancelled_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================
-- MEDICAL HISTORY
-- ============================================================

CREATE TABLE IF NOT EXISTS patient_medical_history (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    doctor_id TEXT NOT NULL,
    appointment_id TEXT,
    recorded_date TEXT NOT NULL,
    past_illnesses TEXT,
    allergies TEXT,
    chronic_diseases TEXT,
    surgeries TEXT,
    family_medical_history TEXT,
    current_medications TEXT,
    blood_pressure TEXT,
    temperature REAL,
    weight REAL,
    height REAL,
    notes TEXT,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    version INTEGER DEFAULT 1,
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- CONSULTATIONS & PRESCRIPTIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS consultations (
    id TEXT PRIMARY KEY,
    appointment_id TEXT UNIQUE NOT NULL,
    patient_id TEXT NOT NULL,
    doctor_id TEXT NOT NULL,
    consultation_date TEXT NOT NULL,
    chief_complaint TEXT,
    diagnosis TEXT NOT NULL,
    consultation_notes TEXT,
    follow_up_required INTEGER DEFAULT 0,
    follow_up_after_days INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS prescriptions (
    id TEXT PRIMARY KEY,
    prescription_number TEXT UNIQUE NOT NULL,
    consultation_id TEXT NOT NULL,
    patient_id TEXT NOT NULL,
    doctor_id TEXT NOT NULL,
    prescription_date TEXT NOT NULL,
    notes TEXT,
    special_instructions TEXT,
    version INTEGER DEFAULT 1,
    parent_prescription_id TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (consultation_id) REFERENCES consultations(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_prescription_id) REFERENCES prescriptions(id)
);

CREATE TABLE IF NOT EXISTS prescription_medicines (
    id TEXT PRIMARY KEY,
    prescription_id TEXT NOT NULL,
    medicine_name TEXT NOT NULL,
    dosage TEXT NOT NULL,
    usage TEXT,
    frequency TEXT NOT NULL,
    duration_days INTEGER NOT NULL CHECK (duration_days > 0),
    usage_timing TEXT,
    frequency_pattern TEXT,
    special_instructions TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS prescription_history (
    id TEXT PRIMARY KEY,
    prescription_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    prescription_data TEXT NOT NULL,
    modified_by TEXT NOT NULL,
    modified_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE CASCADE,
    FOREIGN KEY (modified_by) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- MEDICAL REPORTS & DIAGNOSTICS
-- ============================================================

CREATE TABLE IF NOT EXISTS medical_reports (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    doctor_id TEXT,
    appointment_id TEXT,
    report_type TEXT NOT NULL CHECK(report_type IN ('blood_test', 'xray', 'mri', 'ct_scan', 'ecg', 'echo', 'ultrasound', 'other')),
    report_name TEXT NOT NULL,
    test_date TEXT NOT NULL,
    test_name TEXT,
    lab_name TEXT,
    lab_address TEXT,
    lab_phone TEXT,
    report_file_path TEXT NOT NULL,
    file_url TEXT,
    result_summary TEXT,
    doctor_remarks TEXT,
    test_results TEXT,
    uploaded_by TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE SET NULL,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- BILLING & PAYMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS charge_types (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    default_amount REAL NOT NULL CHECK (default_amount >= 0),
    is_taxable INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS bills (
    id TEXT PRIMARY KEY,
    bill_number TEXT UNIQUE NOT NULL,
    patient_id TEXT NOT NULL,
    appointment_id TEXT,
    bill_date TEXT NOT NULL,
    subtotal REAL NOT NULL CHECK (subtotal >= 0),
    tax_amount REAL DEFAULT 0 CHECK (tax_amount >= 0),
    discount_amount REAL DEFAULT 0 CHECK (discount_amount >= 0),
    total_amount REAL NOT NULL CHECK (total_amount >= 0),
    payment_status TEXT DEFAULT 'pending' CHECK(payment_status IN ('pending', 'paid', 'failed', 'refunded', 'partially_paid', 'overdue', 'cancelled')),
    payment_date TEXT,
    payment_method TEXT,
    transaction_id TEXT,
    due_date TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    is_deleted INTEGER DEFAULT 0,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS bill_items (
    id TEXT PRIMARY KEY,
    bill_id TEXT NOT NULL,
    charge_type_id TEXT NOT NULL,
    description TEXT,
    quantity INTEGER DEFAULT 1 CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    total_price REAL NOT NULL CHECK (total_price >= 0),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
    FOREIGN KEY (charge_type_id) REFERENCES charge_types(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS invoices (
    id TEXT PRIMARY KEY,
    invoice_number TEXT UNIQUE NOT NULL,
    patient_id TEXT NOT NULL,
    doctor_id TEXT,
    appointment_id TEXT,
    invoice_date TEXT NOT NULL DEFAULT (date('now')),
    due_date TEXT,
    subtotal REAL NOT NULL DEFAULT 0,
    tax_rate REAL DEFAULT 0,
    tax_amount REAL DEFAULT 0,
    discount REAL DEFAULT 0,
    total_amount REAL NOT NULL,
    payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'partially_paid', 'overdue', 'cancelled')),
    payment_method TEXT,
    payment_date TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE SET NULL,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS invoice_items (
    id TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL,
    item_type TEXT NOT NULL,
    item_name TEXT NOT NULL,
    description TEXT,
    quantity INTEGER DEFAULT 1,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    notification_type TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('email', 'sms', 'app', 'push', 'in_app')),
    title TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'sent', 'failed')),
    is_read INTEGER DEFAULT 0,
    is_sent INTEGER DEFAULT 0,
    send_via TEXT,
    scheduled_at TEXT,
    scheduled_time TEXT,
    sent_at TEXT,
    reference_type TEXT,
    reference_id TEXT,
    error_message TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- AUDIT LOGS
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    table_name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    record_id TEXT NOT NULL,
    entity_id TEXT,
    action TEXT NOT NULL,
    old_data TEXT,
    old_values TEXT,
    new_data TEXT,
    new_values TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================
-- REFRESH TOKENS
-- ============================================================

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    revoked_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- PATIENT CONSENT
-- ============================================================

CREATE TABLE IF NOT EXISTS patient_consents (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    consent_type TEXT NOT NULL,
    consent_text TEXT NOT NULL,
    is_agreed INTEGER NOT NULL,
    is_granted INTEGER NOT NULL,
    agreed_at TEXT,
    granted_at TEXT,
    revoked_at TEXT,
    ip_address TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- ============================================================
-- SYSTEM SETTINGS
-- ============================================================

CREATE TABLE IF NOT EXISTS system_settings (
    id TEXT PRIMARY KEY,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type TEXT,
    description TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);

-- ============================================================
-- INDEXES
-- ============================================================

-- Users
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active, is_deleted);

-- Patients
CREATE INDEX IF NOT EXISTS idx_patients_user_id ON patients(user_id);
CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone);
CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(first_name, last_name);

-- Doctors
CREATE INDEX IF NOT EXISTS idx_doctors_user_id ON doctors(user_id);
CREATE INDEX IF NOT EXISTS idx_doctors_registration ON doctors(registration_number);
CREATE INDEX IF NOT EXISTS idx_doctors_verified ON doctors(is_verified);
CREATE INDEX IF NOT EXISTS idx_doctors_rating ON doctors(rating);

-- Appointments
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor ON appointments(doctor_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_appointments_number ON appointments(appointment_number);

-- Consultations
CREATE INDEX IF NOT EXISTS idx_consultations_appointment ON consultations(appointment_id);
CREATE INDEX IF NOT EXISTS idx_consultations_patient ON consultations(patient_id);
CREATE INDEX IF NOT EXISTS idx_consultations_doctor ON consultations(doctor_id);

-- Prescriptions
CREATE INDEX IF NOT EXISTS idx_prescriptions_consultation ON prescriptions(consultation_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_patient ON prescriptions(patient_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_doctor ON prescriptions(doctor_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_number ON prescriptions(prescription_number);

-- Medical History
CREATE INDEX IF NOT EXISTS idx_medical_history_patient ON patient_medical_history(patient_id);
CREATE INDEX IF NOT EXISTS idx_medical_history_doctor ON patient_medical_history(doctor_id);
CREATE INDEX IF NOT EXISTS idx_medical_history_date ON patient_medical_history(recorded_date);

-- Medical Reports
CREATE INDEX IF NOT EXISTS idx_medical_reports_patient ON medical_reports(patient_id);
CREATE INDEX IF NOT EXISTS idx_medical_reports_doctor ON medical_reports(doctor_id);
CREATE INDEX IF NOT EXISTS idx_medical_reports_type ON medical_reports(report_type);

-- Bills
CREATE INDEX IF NOT EXISTS idx_bills_patient ON bills(patient_id);
CREATE INDEX IF NOT EXISTS idx_bills_appointment ON bills(appointment_id);
CREATE INDEX IF NOT EXISTS idx_bills_status ON bills(payment_status);
CREATE INDEX IF NOT EXISTS idx_bills_date ON bills(bill_date);
CREATE INDEX IF NOT EXISTS idx_bills_number ON bills(bill_number);

-- Invoices
CREATE INDEX IF NOT EXISTS idx_invoices_patient ON invoices(patient_id);
CREATE INDEX IF NOT EXISTS idx_invoices_invoice_number ON invoices(invoice_number);
CREATE INDEX IF NOT EXISTS idx_invoices_payment_status ON invoices(payment_status);
CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice ON invoice_items(invoice_id);

-- Notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_scheduled ON notifications(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);

-- Audit Logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_table ON audit_logs(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_logs_record ON audit_logs(record_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON audit_logs(entity_type, entity_id);

-- Doctor Time Slots
CREATE INDEX IF NOT EXISTS idx_doctor_time_slots_doctor ON doctor_availability(doctor_id);

-- Patient Consents
CREATE INDEX IF NOT EXISTS idx_patient_consents_patient ON patient_consents(patient_id);

-- ============================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================

CREATE TRIGGER IF NOT EXISTS update_users_updated_at 
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_patients_updated_at 
AFTER UPDATE ON patients
BEGIN
    UPDATE patients SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_doctors_updated_at 
AFTER UPDATE ON doctors
BEGIN
    UPDATE doctors SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_appointments_updated_at 
AFTER UPDATE ON appointments
BEGIN
    UPDATE appointments SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_consultations_updated_at 
AFTER UPDATE ON consultations
BEGIN
    UPDATE consultations SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_prescriptions_updated_at 
AFTER UPDATE ON prescriptions
BEGIN
    UPDATE prescriptions SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- ============================================================
-- INITIAL DATA - SPECIALIZATIONS
-- ============================================================

INSERT OR IGNORE INTO specializations (id, name, description) VALUES
('spec-01', 'General Physician', 'Primary care doctors who treat a wide variety of medical conditions'),
('spec-02', 'Cardiologist', 'Specialists in heart and cardiovascular system'),
('spec-03', 'Dermatologist', 'Skin, hair, and nail specialists'),
('spec-04', 'Orthopedic', 'Bone, joint, and musculoskeletal system specialists'),
('spec-05', 'Pediatrician', 'Child health specialists'),
('spec-06', 'Gynecologist', 'Women''s reproductive health specialists'),
('spec-07', 'Neurologist', 'Brain and nervous system specialists'),
('spec-08', 'ENT', 'Ear, Nose, and Throat specialists'),
('spec-09', 'Dentist', 'Oral health specialists'),
('spec-10', 'Psychiatrist', 'Mental health specialists');

-- ============================================================
-- INITIAL DATA - CHARGE TYPES
-- ============================================================

INSERT OR IGNORE INTO charge_types (id, name, description, default_amount, is_taxable) VALUES
('charge-01', 'Consultation Fee', 'General consultation charges', 500.00, 1),
('charge-02', 'Follow-up Visit', 'Follow-up consultation charges', 300.00, 1),
('charge-03', 'Emergency Consultation', 'Emergency consultation charges', 1000.00, 1),
('charge-04', 'Blood Test', 'Blood testing charges', 800.00, 1),
('charge-05', 'X-Ray', 'X-ray diagnostic charges', 1200.00, 1),
('charge-06', 'MRI Scan', 'MRI scanning charges', 5000.00, 1),
('charge-07', 'CT Scan', 'CT scanning charges', 4000.00, 1),
('charge-08', 'ECG', 'Electrocardiogram charges', 600.00, 1),
('charge-09', 'Ultrasound', 'Ultrasound scanning charges', 1500.00, 1);

-- ============================================================
-- INITIAL DATA - SYSTEM SETTINGS
-- ============================================================

INSERT OR IGNORE INTO system_settings (id, setting_key, setting_value, setting_type, description) VALUES
('setting-01', 'default_tax_rate', '18', 'number', 'Default GST/Tax rate percentage'),
('setting-02', 'appointment_slot_duration', '30', 'number', 'Default appointment duration in minutes'),
('setting-03', 'payment_reminder_days', '3', 'number', 'Days before payment due to send reminder'),
('setting-04', 'appointment_reminder_hours', '24', 'number', 'Hours before appointment to send reminder');

-- ============================================================
-- VIEWS (Implemented as comments - use in application layer)
-- ============================================================

-- SQLite doesn't support complex views with ARRAY_AGG
-- These should be implemented in the application layer:

-- v_doctor_details: Join doctors, users, and specializations
-- v_appointment_details: Join appointments, patients, doctors, and clinics

