-- Create custom users for Cloudflare deployment
-- Patient: mazaemailghe@gmail.com / Patient@123
-- Doctor: tejas.jrb@gmail.com / Doctor@123

-- Insert users
INSERT INTO users (id, email, password_hash, role, is_active, created_at) VALUES 
('usr-patient-custom-001', 'mazaemailghe@gmail.com', '$2a$10$SuND/3UvAvEQkxw5EzdLTeY3av1bv3n8Sf0WkZ6OZN69Es6VAspqC', 'patient', 1, datetime('now')),
('usr-doctor-custom-001', 'tejas.jrb@gmail.com', '$2a$10$vdoIDweDHh9scEvVPBz1ruiPH3TMhOALwbEMO1cPsQ1Erbf5tC7Re', 'doctor', 1, datetime('now'));

-- Insert patient profile
INSERT INTO patients (id, user_id, first_name, last_name, date_of_birth, gender, phone, address, city, state, zip_code, blood_group, created_at) VALUES
('pat-custom-001', 'usr-patient-custom-001', 'Patient', 'User', '1995-01-01', 'Male', '9999999999', '123 Custom Street', 'Mumbai', 'Maharashtra', '400001', 'O+', datetime('now'));

-- Insert doctor profile
INSERT INTO doctors (id, user_id, first_name, last_name, gender, phone, registration_number, qualification, experience_years, consultation_fee, clinic_name, clinic_address, created_at) VALUES
('doc-custom-001', 'usr-doctor-custom-001', 'Tejas', 'JRB', 'Male', '9999999998', 'MH-DOC-2024-001', 'MBBS, MD', 5, 600, 'Custom Clinic', 'Mumbai, Maharashtra', datetime('now'));
