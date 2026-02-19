-- Complete seed data for 10 patients with logins, medical history, and prescriptions
-- Password for all patients: Patient@123

-- First, let's ensure we have 10 patients total by checking existing and adding more

-- Add more users for patients (total should be 10)
INSERT INTO users (id, email, password_hash, role, is_active, created_at) VALUES
('user-patient-011', 'rajesh.kumar@gmail.com', '$2b$10$rFZqK7kH8WgjHgcI8kH8Ou8zTZm5xMTZm5xMTZm5xMTZm5xMTZm5xM', 'patient', 1, datetime('now')),
('user-patient-012', 'anita.sharma@gmail.com', '$2b$10$rFZqK7kH8WgjHgcI8kH8Ou8zTZm5xMTZm5xMTZm5xMTZm5xMTZm5xM', 'patient', 1, datetime('now')),
('user-patient-013', 'vikram.singh@gmail.com', '$2b$10$rFZqK7kH8WgjHgcI8kH8Ou8zTZm5xMTZm5xMTZm5xMTZm5xMTZm5xM', 'patient', 1, datetime('now')),
('user-patient-014', 'priya.mehta@gmail.com', '$2b$10$rFZqK7kH8WgjHgcI8kH8Ou8zTZm5xMTZm5xMTZm5xMTZm5xMTZm5xM', 'patient', 1, datetime('now')),
('user-patient-015', 'arjun.patel@gmail.com', '$2b$10$rFZqK7kH8WgjHgcI8kH8Ou8zTZm5xMTZm5xMTZm5xMTZm5xMTZm5xM', 'patient', 1, datetime('now'));

-- Add corresponding patient profiles
INSERT INTO patients (id, user_id, first_name, last_name, date_of_birth, gender, phone, address, city, state, zip_code, blood_group, emergency_contact_name, emergency_contact_phone, created_at) VALUES
('patient-011', 'user-patient-011', 'Rajesh', 'Kumar', '1980-06-15', 'male', '+91-9876543221', '101 Residency Road', 'Bangalore', 'Karnataka', '560025', 'A+', 'Sunita Kumar', '+91-9876000011', datetime('now')),
('patient-012', 'user-patient-012', 'Anita', 'Sharma', '1992-09-20', 'female', '+91-9876543222', '202 Civil Lines', 'Jaipur', 'Rajasthan', '302001', 'B+', 'Rohit Sharma', '+91-9876000012', datetime('now')),
('patient-013', 'user-patient-013', 'Vikram', 'Singh', '1975-03-10', 'male', '+91-9876543223', '303 Station Road', 'Lucknow', 'Uttar Pradesh', '226001', 'O+', 'Meera Singh', '+91-9876000013', datetime('now')),
('patient-014', 'user-patient-014', 'Priya', 'Mehta', '1998-12-25', 'female', '+91-9876543224', '404 Beach Road', 'Chennai', 'Tamil Nadu', '600001', 'AB+', 'Sanjay Mehta', '+91-9876000014', datetime('now')),
('patient-015', 'user-patient-015', 'Arjun', 'Patel', '1987-04-30', 'male', '+91-9876543225', '505 SG Highway', 'Ahmedabad', 'Gujarat', '380015', 'A-', 'Kavita Patel', '+91-9876000015', datetime('now'));

-- Add more appointments for all patients with different doctors
INSERT INTO appointments (id, appointment_number, patient_id, doctor_id, clinic_id, appointment_date, appointment_time, status, reason_for_visit, symptoms, doctor_notes, created_at) VALUES
-- Recent completed appointments
('appt-101', 'APT-2026-000101', 'patient-001', 'doc-001', 'clinic-001', date('now', '-15 days'), '09:00:00', 'completed', 'Diabetes management checkup', 'Fatigue, frequent urination', 'Blood sugar levels stable, continue current medication', datetime('now', '-16 days')),
('appt-102', 'APT-2026-000102', 'patient-002', 'doc-004', 'clinic-004', date('now', '-12 days'), '10:30:00', 'completed', 'Asthma review', 'Shortness of breath', 'Adjusted inhaler dosage', datetime('now', '-13 days')),
('appt-103', 'APT-2026-000103', 'patient-003', 'doc-002', 'clinic-002', date('now', '-10 days'), '14:00:00', 'completed', 'Migraine treatment', 'Severe headache, nausea', 'Prescribed preventive medication', datetime('now', '-11 days')),
('appt-104', 'APT-2026-000104', 'patient-004', 'doc-002', 'clinic-002', date('now', '-8 days'), '11:00:00', 'completed', 'PCOD follow-up', 'Irregular periods', 'Hormonal therapy adjusted', datetime('now', '-9 days')),
('appt-105', 'APT-2026-000105', 'patient-005', 'doc-001', 'clinic-001', date('now', '-6 days'), '15:30:00', 'completed', 'Gastritis consultation', 'Stomach pain, acidity', 'Prescribed antacids, dietary advice', datetime('now', '-7 days')),
('appt-106', 'APT-2026-000106', 'patient-011', 'doc-001', 'clinic-001', date('now', '-14 days'), '09:30:00', 'completed', 'Diabetes and BP check', 'Dizziness', 'Blood sugar and BP controlled well', datetime('now', '-15 days')),
('appt-107', 'APT-2026-000107', 'patient-012', 'doc-002', 'clinic-002', date('now', '-11 days'), '16:00:00', 'completed', 'Anxiety management', 'Panic attacks', 'Medication adjusted, counseling recommended', datetime('now', '-12 days')),
('appt-108', 'APT-2026-000108', 'patient-013', 'doc-001', 'clinic-001', date('now', '-9 days'), '10:00:00', 'completed', 'Kidney function review', 'Fatigue, back pain', 'Kidney function stable, continue monitoring', datetime('now', '-10 days')),
('appt-109', 'APT-2026-000109', 'patient-014', 'doc-004', 'clinic-004', date('now', '-7 days'), '13:00:00', 'completed', 'Anemia checkup', 'Weakness, pale skin', 'Hemoglobin improved, continue iron supplements', datetime('now', '-8 days')),
('appt-110', 'APT-2026-000110', 'patient-015', 'doc-003', 'clinic-003', date('now', '-5 days'), '11:30:00', 'completed', 'Psoriasis treatment', 'Skin rashes', 'Topical cream working well', datetime('now', '-6 days')),

-- Upcoming appointments
('appt-111', 'APT-2026-000111', 'patient-001', 'doc-001', 'clinic-001', date('now', '+7 days'), '09:00:00', 'confirmed', 'Diabetes follow-up', NULL, NULL, datetime('now', '-1 day')),
('appt-112', 'APT-2026-000112', 'patient-002', 'doc-004', 'clinic-004', date('now', '+10 days'), '10:00:00', 'booked', 'Asthma review', NULL, NULL, datetime('now', '-2 days')),
('appt-113', 'APT-2026-000113', 'patient-006', 'doc-001', 'clinic-001', date('now', '+3 days'), '14:30:00', 'confirmed', 'General health checkup', NULL, NULL, datetime('now')),
('appt-114', 'APT-2026-000114', 'patient-011', 'doc-001', 'clinic-001', date('now', '+14 days'), '09:30:00', 'booked', 'Diabetes monitoring', NULL, NULL, datetime('now')),
('appt-115', 'APT-2026-000115', 'patient-013', 'doc-001', 'clinic-001', date('now', '+21 days'), '10:00:00', 'booked', 'Kidney function test', NULL, NULL, datetime('now'));

-- Add prescriptions for completed appointments
INSERT INTO prescriptions (id, appointment_id, patient_id, doctor_id, prescription_date, diagnosis, notes, created_at) VALUES
('presc-101', 'appt-101', 'patient-001', 'doc-001', date('now', '-15 days'), 'Type 2 Diabetes Mellitus', 'Continue current medication regimen, monitor blood sugar daily', datetime('now', '-15 days')),
('presc-102', 'appt-102', 'patient-002', 'doc-004', date('now', '-12 days'), 'Bronchial Asthma', 'Inhaler dosage increased, avoid triggers', datetime('now', '-12 days')),
('presc-103', 'appt-103', 'patient-003', 'doc-002', date('now', '-10 days'), 'Chronic Migraine', 'Preventive medication started', datetime('now', '-10 days')),
('presc-104', 'appt-104', 'patient-004', 'doc-002', date('now', '-8 days'), 'Polycystic Ovarian Disease', 'Hormonal therapy adjusted', datetime('now', '-8 days')),
('presc-105', 'appt-105', 'patient-005', 'doc-001', date('now', '-6 days'), 'Chronic Gastritis', 'Antacids and dietary modifications', datetime('now', '-6 days')),
('presc-106', 'appt-106', 'patient-011', 'doc-001', date('now', '-14 days'), 'Type 2 Diabetes with Hypertension', 'Both conditions well controlled', datetime('now', '-14 days')),
('presc-107', 'appt-107', 'patient-012', 'doc-002', date('now', '-11 days'), 'Generalized Anxiety Disorder', 'Medication adjusted, therapy recommended', datetime('now', '-11 days')),
('presc-108', 'appt-108', 'patient-013', 'doc-001', date('now', '-9 days'), 'Chronic Kidney Disease Stage 2', 'Continue monitoring, protein intake restricted', datetime('now', '-9 days')),
('presc-109', 'appt-109', 'patient-014', 'doc-004', date('now', '-7 days'), 'Iron Deficiency Anemia', 'Hemoglobin improving, continue supplements', datetime('now', '-7 days')),
('presc-110', 'appt-110', 'patient-015', 'doc-003', date('now', '-5 days'), 'Psoriasis', 'Topical treatment effective', datetime('now', '-5 days'));

-- Add medications for each prescription
INSERT INTO prescription_medications (id, prescription_id, medicine_name, dosage, frequency, duration, instructions, created_at) VALUES
-- Presc 101 (Diabetes)
('med-101', 'presc-101', 'Metformin', '500mg', 'Twice daily', '30 days', 'Take with meals', datetime('now', '-15 days')),
('med-102', 'presc-101', 'Glimepiride', '2mg', 'Once daily', '30 days', 'Take before breakfast', datetime('now', '-15 days')),

-- Presc 102 (Asthma)
('med-103', 'presc-102', 'Salbutamol Inhaler', '100mcg', 'As needed', '30 days', 'Use during breathlessness', datetime('now', '-12 days')),
('med-104', 'presc-102', 'Budesonide Inhaler', '200mcg', 'Twice daily', '30 days', 'Rinse mouth after use', datetime('now', '-12 days')),
('med-105', 'presc-102', 'Montelukast', '10mg', 'Once daily at night', '30 days', 'Take before sleep', datetime('now', '-12 days')),

-- Presc 103 (Migraine)
('med-106', 'presc-103', 'Propranolol', '40mg', 'Twice daily', '30 days', 'Take with food', datetime('now', '-10 days')),
('med-107', 'presc-103', 'Sumatriptan', '50mg', 'As needed', '10 tablets', 'Take at onset of headache', datetime('now', '-10 days')),

-- Presc 104 (PCOD)
('med-108', 'presc-104', 'Metformin', '500mg', 'Twice daily', '30 days', 'Take with meals', datetime('now', '-8 days')),
('med-109', 'presc-104', 'Oral Contraceptive', 'Standard dose', 'Once daily', '21 days', 'Take at same time daily', datetime('now', '-8 days')),

-- Presc 105 (Gastritis)
('med-110', 'presc-105', 'Pantoprazole', '40mg', 'Once daily', '30 days', 'Take before breakfast', datetime('now', '-6 days')),
('med-111', 'presc-105', 'Sucralfate Suspension', '10ml', 'Three times daily', '15 days', 'Take on empty stomach', datetime('now', '-6 days')),

-- Presc 106 (Diabetes + HTN)
('med-112', 'presc-106', 'Insulin Glargine', '20 units', 'Once daily at night', '30 days', 'Subcutaneous injection', datetime('now', '-14 days')),
('med-113', 'presc-106', 'Amlodipine', '5mg', 'Once daily', '30 days', 'Take in morning', datetime('now', '-14 days')),
('med-114', 'presc-106', 'Atenolol', '50mg', 'Once daily', '30 days', 'Take with food', datetime('now', '-14 days')),

-- Presc 107 (Anxiety)
('med-115', 'presc-107', 'Escitalopram', '10mg', 'Once daily', '30 days', 'Take in morning', datetime('now', '-11 days')),
('med-116', 'presc-107', 'Clonazepam', '0.5mg', 'Once at night', '15 days', 'Only during panic attacks', datetime('now', '-11 days')),

-- Presc 108 (CKD)
('med-117', 'presc-108', 'Tablet Calcium Carbonate', '500mg', 'Three times daily', '30 days', 'Take with meals', datetime('now', '-9 days')),
('med-118', 'presc-108', 'Enalapril', '5mg', 'Once daily', '30 days', 'For blood pressure', datetime('now', '-9 days')),

-- Presc 109 (Anemia)
('med-119', 'presc-109', 'Ferrous Sulfate', '200mg', 'Once daily', '60 days', 'Take on empty stomach with vitamin C', datetime('now', '-7 days')),
('med-120', 'presc-109', 'Folic Acid', '5mg', 'Once daily', '60 days', 'Take after breakfast', datetime('now', '-7 days')),

-- Presc 110 (Psoriasis)
('med-121', 'presc-110', 'Clobetasol Cream', '0.05%', 'Twice daily', '14 days', 'Apply thin layer on affected areas', datetime('now', '-5 days')),
('med-122', 'presc-110', 'Moisturizing Lotion', 'As needed', 'Three times daily', '30 days', 'Keep skin hydrated', datetime('now', '-5 days'));
