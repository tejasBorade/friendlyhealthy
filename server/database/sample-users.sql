-- Create Sample Users for All Roles
-- Password for all users: Admin@123

-- 1. Admin User
INSERT INTO users (email, password_hash, role) 
VALUES ('admin@healthcare.com', '$2a$10$rYUqZXqZQmZJVGZP5X5X5.eZXqZXqZXqZXqZXqZXqZXqZXqZXqZXqZu', 'admin')
ON CONFLICT (email) DO NOTHING;

-- 2. Doctor User
INSERT INTO users (email, password_hash, role) 
VALUES ('doctor@healthcare.com', '$2a$10$rYUqZXqZQmZJVGZP5X5X5.eZXqZXqZXqZXqZXqZXqZXqZXqZXqZXqZu', 'doctor')
ON CONFLICT (email) DO NOTHING;

-- Get doctor user_id and create doctor profile
DO $$
DECLARE 
    doctor_user_id INTEGER;
BEGIN
    SELECT id INTO doctor_user_id FROM users WHERE email = 'doctor@healthcare.com';
    
    IF doctor_user_id IS NOT NULL THEN
        INSERT INTO doctors (user_id, first_name, last_name, specialization, qualification, phone, consultation_fee, is_available)
        VALUES (doctor_user_id, 'Dr. Sarah', 'Johnson', 'Cardiology', 'MD, FACC', '555-0101', 150.00, true)
        ON CONFLICT (user_id) DO NOTHING;
    END IF;
END $$;

-- 3. Staff User
INSERT INTO users (email, password_hash, role) 
VALUES ('staff@healthcare.com', '$2a$10$rYUqZXqZQmZJVGZP5X5X5.eZXqZXqZXqZXqZXqZXqZXqZXqZXqZXqZu', 'staff')
ON CONFLICT (email) DO NOTHING;

-- 4. Patient User (already created via API, but add another)
INSERT INTO users (email, password_hash, role) 
VALUES ('patient@healthcare.com', '$2a$10$rYUqZXqZQmZJVGZP5X5X5.eZXqZXqZXqZXqZXqZXqZXqZXqZXqZXqZu', 'patient')
ON CONFLICT (email) DO NOTHING;

-- Get patient user_id and create patient profile
DO $$
DECLARE 
    patient_user_id INTEGER;
BEGIN
    SELECT id INTO patient_user_id FROM users WHERE email = 'patient@healthcare.com';
    
    IF patient_user_id IS NOT NULL THEN
        INSERT INTO patients (user_id, first_name, last_name, phone, blood_group)
        VALUES (patient_user_id, 'John', 'Smith', '555-0201', 'O+')
        ON CONFLICT (user_id) DO NOTHING;
    END IF;
END $$;

-- Add more doctors
INSERT INTO users (email, password_hash, role) 
VALUES ('doctor2@healthcare.com', '$2a$10$rYUqZXqZQmZJVGZP5X5X5.eZXqZXqZXqZXqZXqZXqZXqZXqZXqZXqZu', 'doctor')
ON CONFLICT (email) DO NOTHING;

DO $$
DECLARE 
    doctor2_user_id INTEGER;
BEGIN
    SELECT id INTO doctor2_user_id FROM users WHERE email = 'doctor2@healthcare.com';
    
    IF doctor2_user_id IS NOT NULL THEN
        INSERT INTO doctors (user_id, first_name, last_name, specialization, qualification, phone, consultation_fee, is_available)
        VALUES (doctor2_user_id, 'Dr. Michael', 'Chen', 'Pediatrics', 'MD, FAAP', '555-0102', 120.00, true)
        ON CONFLICT (user_id) DO NOTHING;
    END IF;
END $$;
