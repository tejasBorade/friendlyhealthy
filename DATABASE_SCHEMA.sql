-- Healthcare Management Platform - PostgreSQL Database Schema
-- Version: 1.0
-- Date: 2026-02-07

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for encryption
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- ENUM TYPES
-- ============================================================

CREATE TYPE user_role AS ENUM ('patient', 'doctor', 'admin');
CREATE TYPE appointment_status AS ENUM ('booked', 'confirmed', 'completed', 'cancelled', 'rejected');
CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'failed', 'refunded');
CREATE TYPE gender AS ENUM ('male', 'female', 'other');
CREATE TYPE notification_type AS ENUM ('email', 'sms', 'app');
CREATE TYPE notification_status AS ENUM ('pending', 'sent', 'failed');
CREATE TYPE day_of_week AS ENUM ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday');
CREATE TYPE report_type AS ENUM ('blood_test', 'xray', 'mri', 'ct_scan', 'ecg', 'echo', 'ultrasound', 'other');

-- ============================================================
-- USER MANAGEMENT
-- ============================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender gender NOT NULL,
    phone VARCHAR(20) NOT NULL,
    alternate_phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    zip_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'India',
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    blood_group VARCHAR(10),
    profile_picture VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE specializations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE doctors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    gender gender NOT NULL,
    phone VARCHAR(20) NOT NULL,
    registration_number VARCHAR(100) UNIQUE NOT NULL,
    qualification VARCHAR(500) NOT NULL,
    experience_years INTEGER NOT NULL CHECK (experience_years >= 0),
    consultation_fee DECIMAL(10, 2) NOT NULL CHECK (consultation_fee >= 0),
    about TEXT,
    profile_picture VARCHAR(500),
    is_verified BOOLEAN DEFAULT FALSE,
    rating DECIMAL(3, 2) DEFAULT 0.00 CHECK (rating >= 0 AND rating <= 5),
    total_reviews INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE doctor_specializations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctor_id UUID NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    specialization_id UUID NOT NULL REFERENCES specializations(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doctor_id, specialization_id)
);

CREATE TABLE clinics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctor_id UUID NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    zip_code VARCHAR(20),
    phone VARCHAR(20),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- ============================================================
-- AVAILABILITY & SCHEDULING
-- ============================================================

CREATE TABLE doctor_availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctor_id UUID NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    clinic_id UUID REFERENCES clinics(id) ON DELETE CASCADE,
    day_of_week day_of_week NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_duration INTEGER NOT NULL DEFAULT 30, -- in minutes
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CHECK (end_time > start_time)
);

CREATE TABLE doctor_leaves (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doctor_id UUID NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CHECK (to_date >= from_date)
);

-- ============================================================
-- APPOINTMENTS
-- ============================================================

CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_number VARCHAR(50) UNIQUE NOT NULL,
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id UUID NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    clinic_id UUID REFERENCES clinics(id) ON DELETE SET NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    duration INTEGER DEFAULT 30, -- in minutes
    status appointment_status DEFAULT 'booked',
    reason_for_visit TEXT,
    symptoms TEXT,
    doctor_notes TEXT,
    cancellation_reason TEXT,
    cancelled_by UUID REFERENCES users(id) ON DELETE SET NULL,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- ============================================================
-- MEDICAL HISTORY
-- ============================================================

CREATE TABLE patient_medical_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id UUID NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    appointment_id UUID REFERENCES appointments(id) ON DELETE SET NULL,
    recorded_date DATE NOT NULL,
    past_illnesses TEXT,
    allergies TEXT,
    chronic_diseases TEXT,
    surgeries TEXT,
    family_medical_history TEXT,
    current_medications TEXT,
    notes TEXT,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- ============================================================
-- CONSULTATIONS & PRESCRIPTIONS
-- ============================================================

CREATE TABLE consultations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_id UUID UNIQUE NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id UUID NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    consultation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    chief_complaint TEXT,
    diagnosis TEXT NOT NULL,
    consultation_notes TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_after_days INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE prescriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prescription_number VARCHAR(50) UNIQUE NOT NULL,
    consultation_id UUID NOT NULL REFERENCES consultations(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id UUID NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    prescription_date DATE NOT NULL,
    notes TEXT,
    special_instructions TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE prescription_medicines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prescription_id UUID NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
    medicine_name VARCHAR(200) NOT NULL,
    dosage VARCHAR(100) NOT NULL, -- e.g., "500mg"
    usage VARCHAR(50), -- e.g., "after food", "before food"
    frequency VARCHAR(50) NOT NULL, -- e.g., "1-0-1" (morning-afternoon-evening)
    duration_days INTEGER NOT NULL CHECK (duration_days > 0),
    special_instructions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prescription_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prescription_id UUID NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    prescription_data JSONB NOT NULL,
    modified_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- MEDICAL REPORTS & DIAGNOSTICS
-- ============================================================

CREATE TABLE medical_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id UUID REFERENCES doctors(id) ON DELETE SET NULL,
    report_type report_type NOT NULL,
    report_name VARCHAR(200) NOT NULL,
    test_date DATE NOT NULL,
    lab_name VARCHAR(200),
    lab_address TEXT,
    report_file_path VARCHAR(500) NOT NULL,
    doctor_remarks TEXT,
    uploaded_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- ============================================================
-- BILLING & PAYMENTS
-- ============================================================

CREATE TABLE charge_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    default_amount DECIMAL(10, 2) NOT NULL CHECK (default_amount >= 0),
    is_taxable BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bill_number VARCHAR(50) UNIQUE NOT NULL,
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    appointment_id UUID REFERENCES appointments(id) ON DELETE SET NULL,
    bill_date DATE NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL CHECK (subtotal >= 0),
    tax_amount DECIMAL(10, 2) DEFAULT 0 CHECK (tax_amount >= 0),
    discount_amount DECIMAL(10, 2) DEFAULT 0 CHECK (discount_amount >= 0),
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    payment_status payment_status DEFAULT 'pending',
    payment_date TIMESTAMP WITH TIME ZONE,
    payment_method VARCHAR(50),
    transaction_id VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE bill_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bill_id UUID NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
    charge_type_id UUID NOT NULL REFERENCES charge_types(id) ON DELETE CASCADE,
    description TEXT,
    quantity INTEGER DEFAULT 1 CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    total_price DECIMAL(10, 2) NOT NULL CHECK (total_price >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type notification_type NOT NULL,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    status notification_status DEFAULT 'pending',
    scheduled_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- AUDIT LOGS
-- ============================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL, -- INSERT, UPDATE, DELETE
    old_data JSONB,
    new_data JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- REFRESH TOKENS
-- ============================================================

CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================
-- PATIENT CONSENT
-- ============================================================

CREATE TABLE patient_consents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    consent_type VARCHAR(100) NOT NULL,
    consent_text TEXT NOT NULL,
    is_agreed BOOLEAN NOT NULL,
    agreed_at TIMESTAMP WITH TIME ZONE,
    ip_address VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES
-- ============================================================

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active, is_deleted);

-- Patients
CREATE INDEX idx_patients_user_id ON patients(user_id);
CREATE INDEX idx_patients_phone ON patients(phone);
CREATE INDEX idx_patients_name ON patients(first_name, last_name);

-- Doctors
CREATE INDEX idx_doctors_user_id ON doctors(user_id);
CREATE INDEX idx_doctors_registration ON doctors(registration_number);
CREATE INDEX idx_doctors_verified ON doctors(is_verified);
CREATE INDEX idx_doctors_rating ON doctors(rating);

-- Appointments
CREATE INDEX idx_appointments_patient ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor ON appointments(doctor_id);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_appointments_number ON appointments(appointment_number);

-- Consultations
CREATE INDEX idx_consultations_appointment ON consultations(appointment_id);
CREATE INDEX idx_consultations_patient ON consultations(patient_id);
CREATE INDEX idx_consultations_doctor ON consultations(doctor_id);

-- Prescriptions
CREATE INDEX idx_prescriptions_consultation ON prescriptions(consultation_id);
CREATE INDEX idx_prescriptions_patient ON prescriptions(patient_id);
CREATE INDEX idx_prescriptions_doctor ON prescriptions(doctor_id);
CREATE INDEX idx_prescriptions_number ON prescriptions(prescription_number);

-- Medical History
CREATE INDEX idx_medical_history_patient ON patient_medical_history(patient_id);
CREATE INDEX idx_medical_history_doctor ON patient_medical_history(doctor_id);
CREATE INDEX idx_medical_history_date ON patient_medical_history(recorded_date);

-- Medical Reports
CREATE INDEX idx_medical_reports_patient ON medical_reports(patient_id);
CREATE INDEX idx_medical_reports_doctor ON medical_reports(doctor_id);
CREATE INDEX idx_medical_reports_type ON medical_reports(report_type);

-- Bills
CREATE INDEX idx_bills_patient ON bills(patient_id);
CREATE INDEX idx_bills_appointment ON bills(appointment_id);
CREATE INDEX idx_bills_status ON bills(payment_status);
CREATE INDEX idx_bills_date ON bills(bill_date);
CREATE INDEX idx_bills_number ON bills(bill_number);

-- Notifications
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_scheduled ON notifications(scheduled_at);

-- Audit Logs
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_table ON audit_logs(table_name);
CREATE INDEX idx_audit_logs_record ON audit_logs(record_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);

-- ============================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_doctors_updated_at BEFORE UPDATE ON doctors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_consultations_updated_at BEFORE UPDATE ON consultations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prescriptions_updated_at BEFORE UPDATE ON prescriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- STORED PROCEDURES
-- ============================================================

-- Generate appointment number
CREATE OR REPLACE FUNCTION generate_appointment_number()
RETURNS VARCHAR AS $$
DECLARE
    new_number VARCHAR;
    counter INTEGER;
BEGIN
    SELECT COUNT(*) + 1 INTO counter FROM appointments WHERE appointment_date = CURRENT_DATE;
    new_number := 'APT' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || LPAD(counter::TEXT, 4, '0');
    RETURN new_number;
END;
$$ LANGUAGE plpgsql;

-- Generate bill number
CREATE OR REPLACE FUNCTION generate_bill_number()
RETURNS VARCHAR AS $$
DECLARE
    new_number VARCHAR;
    counter INTEGER;
BEGIN
    SELECT COUNT(*) + 1 INTO counter FROM bills WHERE bill_date = CURRENT_DATE;
    new_number := 'BILL' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || LPAD(counter::TEXT, 4, '0');
    RETURN new_number;
END;
$$ LANGUAGE plpgsql;

-- Generate prescription number
CREATE OR REPLACE FUNCTION generate_prescription_number()
RETURNS VARCHAR AS $$
DECLARE
    new_number VARCHAR;
    counter INTEGER;
BEGIN
    SELECT COUNT(*) + 1 INTO counter FROM prescriptions WHERE prescription_date = CURRENT_DATE;
    new_number := 'RX' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || LPAD(counter::TEXT, 4, '0');
    RETURN new_number;
END;
$$ LANGUAGE plpgsql;

-- Check doctor availability
CREATE OR REPLACE FUNCTION check_doctor_availability(
    p_doctor_id UUID,
    p_date DATE,
    p_time TIME
)
RETURNS BOOLEAN AS $$
DECLARE
    v_day_of_week day_of_week;
    v_available BOOLEAN;
    v_on_leave BOOLEAN;
    v_has_appointment BOOLEAN;
BEGIN
    -- Get day of week
    v_day_of_week := LOWER(TO_CHAR(p_date, 'Day'))::day_of_week;
    
    -- Check if doctor has availability for this day and time
    SELECT EXISTS (
        SELECT 1 FROM doctor_availability
        WHERE doctor_id = p_doctor_id
        AND day_of_week = v_day_of_week
        AND start_time <= p_time
        AND end_time > p_time
        AND is_active = TRUE
    ) INTO v_available;
    
    -- Check if doctor is on leave
    SELECT EXISTS (
        SELECT 1 FROM doctor_leaves
        WHERE doctor_id = p_doctor_id
        AND p_date BETWEEN from_date AND to_date
    ) INTO v_on_leave;
    
    -- Check if doctor has an appointment at this time
    SELECT EXISTS (
        SELECT 1 FROM appointments
        WHERE doctor_id = p_doctor_id
        AND appointment_date = p_date
        AND appointment_time = p_time
        AND status NOT IN ('cancelled', 'rejected')
    ) INTO v_has_appointment;
    
    RETURN v_available AND NOT v_on_leave AND NOT v_has_appointment;
END;
$$ LANGUAGE plpgsql;

-- Get available slots for doctor
CREATE OR REPLACE FUNCTION get_available_slots(
    p_doctor_id UUID,
    p_date DATE
)
RETURNS TABLE (
    slot_time TIME,
    is_available BOOLEAN
) AS $$
DECLARE
    v_day_of_week day_of_week;
    v_start_time TIME;
    v_end_time TIME;
    v_slot_duration INTEGER;
    v_current_time TIME;
BEGIN
    v_day_of_week := LOWER(TO_CHAR(p_date, 'Day'))::day_of_week;
    
    -- Get doctor availability for the day
    SELECT start_time, end_time, slot_duration
    INTO v_start_time, v_end_time, v_slot_duration
    FROM doctor_availability
    WHERE doctor_id = p_doctor_id
    AND day_of_week = v_day_of_week
    AND is_active = TRUE
    LIMIT 1;
    
    IF v_start_time IS NULL THEN
        RETURN;
    END IF;
    
    v_current_time := v_start_time;
    
    WHILE v_current_time < v_end_time LOOP
        RETURN QUERY
        SELECT 
            v_current_time,
            check_doctor_availability(p_doctor_id, p_date, v_current_time);
        
        v_current_time := v_current_time + (v_slot_duration || ' minutes')::INTERVAL;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- INITIAL DATA - SPECIALIZATIONS
-- ============================================================

INSERT INTO specializations (name, description) VALUES
('General Physician', 'Primary care doctors who treat a wide variety of medical conditions'),
('Cardiologist', 'Specialists in heart and cardiovascular system'),
('Dermatologist', 'Skin, hair, and nail specialists'),
('Orthopedic', 'Bone, joint, and musculoskeletal system specialists'),
('Pediatrician', 'Child health specialists'),
('Gynecologist', 'Women''s reproductive health specialists'),
('Neurologist', 'Brain and nervous system specialists'),
('ENT', 'Ear, Nose, and Throat specialists'),
('Dentist', 'Oral health specialists'),
('Psychiatrist', 'Mental health specialists');

-- ============================================================
-- INITIAL DATA - CHARGE TYPES
-- ============================================================

INSERT INTO charge_types (name, description, default_amount, is_taxable) VALUES
('Consultation Fee', 'General consultation charges', 500.00, TRUE),
('Follow-up Visit', 'Follow-up consultation charges', 300.00, TRUE),
('Emergency Consultation', 'Emergency consultation charges', 1000.00, TRUE),
('Blood Test', 'Blood testing charges', 800.00, TRUE),
('X-Ray', 'X-ray diagnostic charges', 1200.00, TRUE),
('MRI Scan', 'MRI scanning charges', 5000.00, TRUE),
('CT Scan', 'CT scanning charges', 4000.00, TRUE),
('ECG', 'Electrocardiogram charges', 600.00, TRUE),
('Ultrasound', 'Ultrasound scanning charges', 1500.00, TRUE);

-- ============================================================
-- VIEWS
-- ============================================================

-- Doctor details with specializations
CREATE OR REPLACE VIEW v_doctor_details AS
SELECT 
    d.id,
    d.user_id,
    d.first_name,
    d.last_name,
    d.first_name || ' ' || d.last_name AS full_name,
    d.gender,
    d.phone,
    d.registration_number,
    d.qualification,
    d.experience_years,
    d.consultation_fee,
    d.about,
    d.profile_picture,
    d.is_verified,
    d.rating,
    d.total_reviews,
    u.email,
    u.is_active,
    ARRAY_AGG(DISTINCT s.name) AS specializations,
    d.created_at,
    d.updated_at
FROM doctors d
JOIN users u ON d.user_id = u.id
LEFT JOIN doctor_specializations ds ON d.id = ds.doctor_id
LEFT JOIN specializations s ON ds.specialization_id = s.id
WHERE d.is_deleted = FALSE AND u.is_deleted = FALSE
GROUP BY d.id, u.email, u.is_active;

-- Appointment details
CREATE OR REPLACE VIEW v_appointment_details AS
SELECT 
    a.id,
    a.appointment_number,
    a.appointment_date,
    a.appointment_time,
    a.duration,
    a.status,
    a.reason_for_visit,
    p.first_name || ' ' || p.last_name AS patient_name,
    p.phone AS patient_phone,
    p.gender AS patient_gender,
    d.first_name || ' ' || d.last_name AS doctor_name,
    d.qualification AS doctor_qualification,
    c.name AS clinic_name,
    a.created_at,
    a.updated_at
FROM appointments a
JOIN patients p ON a.patient_id = p.id
JOIN doctors d ON a.doctor_id = d.id
LEFT JOIN clinics c ON a.clinic_id = c.id
WHERE a.is_deleted = FALSE;

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE users IS 'Core user authentication and role management';
COMMENT ON TABLE patients IS 'Patient demographic and contact information';
COMMENT ON TABLE doctors IS 'Doctor profiles and professional details';
COMMENT ON TABLE appointments IS 'Appointment bookings and scheduling';
COMMENT ON TABLE consultations IS 'Consultation records and diagnosis';
COMMENT ON TABLE prescriptions IS 'Digital prescriptions with version control';
COMMENT ON TABLE medical_reports IS 'Diagnostic and lab reports';
COMMENT ON TABLE bills IS 'Billing and payment information';
COMMENT ON TABLE audit_logs IS 'Audit trail for all sensitive operations';
