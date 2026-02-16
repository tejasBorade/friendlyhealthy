-- Seed users for local development
-- Passwords: Patient@123, Doctor@123, Admin@123
INSERT OR IGNORE INTO users (id, email, password_hash, role, is_active, created_at) VALUES 
('usr-patient-001', 'patient@healthcare.com', '$2a$10$SuND/3UvAvEQkxw5EzdLTeY3av1bv3n8Sf0WkZ6OZN69Es6VAspqC', 'patient', 1, datetime('now')),
('usr-patient-002', 'rahul.sharma@email.com', '$2a$10$SuND/3UvAvEQkxw5EzdLTeY3av1bv3n8Sf0WkZ6OZN69Es6VAspqC', 'patient', 1, datetime('now')),
('usr-patient-003', 'priya.patel@email.com', '$2a$10$SuND/3UvAvEQkxw5EzdLTeY3av1bv3n8Sf0WkZ6OZN69Es6VAspqC', 'patient', 1, datetime('now')),
('usr-doctor-001', 'doctor@healthcare.com', '$2a$10$vdoIDweDHh9scEvVPBz1ruiPH3TMhOALwbEMO1cPsQ1Erbf5tC7Re', 'doctor', 1, datetime('now')),
('usr-doctor-002', 'dr.anjali@healthcare.com', '$2a$10$vdoIDweDHh9scEvVPBz1ruiPH3TMhOALwbEMO1cPsQ1Erbf5tC7Re', 'doctor', 1, datetime('now')),
('usr-doctor-003', 'dr.vikram@healthcare.com', '$2a$10$vdoIDweDHh9scEvVPBz1ruiPH3TMhOALwbEMO1cPsQ1Erbf5tC7Re', 'doctor', 1, datetime('now')),
('usr-admin-001', 'admin@healthcare.com', '$2a$10$u2KCdILjqhwAGlGuhnKyzeiaNqv13L8S4weON8Q4A7ZjvSp.QQCZO', 'admin', 1, datetime('now'));

-- Seed 3 doctor profiles
INSERT OR IGNORE INTO doctors (id, user_id, first_name, last_name, specialization, qualification, experience_years, consultation_fee, phone, city, clinic_address, is_available, created_at) VALUES
('doc-001', 'usr-doctor-001', 'John', 'Smith', 'General Medicine', 'MD, MBBS', 10, 500, '9876543210', 'Mumbai', 'Apollo Medical Center, Andheri West', 1, datetime('now')),
('doc-002', 'usr-doctor-002', 'Anjali', 'Gupta', 'Cardiology', 'MD, DM Cardiology', 15, 1000, '9876543220', 'Mumbai', 'Heart Care Clinic, Bandra East', 1, datetime('now')),
('doc-003', 'usr-doctor-003', 'Vikram', 'Mehta', 'Dermatology', 'MD Dermatology', 8, 700, '9876543230', 'Mumbai', 'Skin & Care Center, Juhu', 1, datetime('now'));

-- Seed 3 patient profiles
INSERT OR IGNORE INTO patients (id, user_id, first_name, last_name, date_of_birth, gender, phone, address, city, state, pincode, blood_group, created_at) VALUES
('pat-001', 'usr-patient-001', 'Jane', 'Doe', '1990-05-15', 'Female', '9876543211', '456 Health Street', 'Mumbai', 'Maharashtra', '400001', 'O+', datetime('now')),
('pat-002', 'usr-patient-002', 'Rahul', 'Sharma', '1985-08-22', 'Male', '9876543212', '78 Green Park Colony', 'Mumbai', 'Maharashtra', '400002', 'B+', datetime('now')),
('pat-003', 'usr-patient-003', 'Priya', 'Patel', '1992-12-10', 'Female', '9876543213', '12 Sunshine Apartments', 'Mumbai', 'Maharashtra', '400003', 'A+', datetime('now'));

-- Seed appointments (interconnected - patient visits doctor)
INSERT OR IGNORE INTO appointments (id, patient_id, doctor_id, appointment_date, appointment_time, reason, notes, status, created_at) VALUES
-- Jane Doe's appointments
('apt-001', 'pat-001', 'doc-001', '2025-01-15', '10:00', 'Annual health checkup', 'Regular checkup, no major concerns', 'completed', datetime('now')),
('apt-002', 'pat-001', 'doc-002', '2025-01-20', '14:30', 'Chest pain evaluation', 'Mild chest discomfort for 2 days', 'completed', datetime('now')),
('apt-003', 'pat-001', 'doc-003', '2025-02-10', '11:00', 'Skin rash consultation', 'Allergic reaction', 'confirmed', datetime('now')),
-- Rahul Sharma's appointments
('apt-004', 'pat-002', 'doc-001', '2025-01-18', '09:30', 'Fever and cold', 'High fever for 3 days', 'completed', datetime('now')),
('apt-005', 'pat-002', 'doc-002', '2025-01-25', '16:00', 'Heart health screening', 'Family history of heart disease', 'confirmed', datetime('now')),
-- Priya Patel's appointments
('apt-006', 'pat-003', 'doc-001', '2025-01-22', '11:30', 'Migraine issues', 'Chronic headaches', 'completed', datetime('now')),
('apt-007', 'pat-003', 'doc-003', '2025-02-05', '15:00', 'Acne treatment', 'Hormonal acne', 'pending', datetime('now'));

-- Seed prescriptions (from completed appointments)
INSERT OR IGNORE INTO prescriptions (id, appointment_id, patient_id, doctor_id, diagnosis, notes, created_at) VALUES
('prs-001', 'apt-001', 'pat-001', 'doc-001', 'General health - Good condition', 'Patient is in good health. Continue healthy lifestyle.', datetime('now')),
('prs-002', 'apt-002', 'pat-001', 'doc-002', 'Mild Anxiety-related chest discomfort', 'ECG normal. Stress-related symptoms. Recommend lifestyle changes.', datetime('now')),
('prs-003', 'apt-004', 'pat-002', 'doc-001', 'Viral Fever with Upper Respiratory Tract Infection', 'Seasonal viral infection. Rest advised for 5 days.', datetime('now')),
('prs-004', 'apt-006', 'pat-003', 'doc-001', 'Chronic Migraine', 'Triggered by stress and irregular sleep. Lifestyle modification recommended.', datetime('now'));

-- Seed prescription medications
INSERT OR IGNORE INTO prescription_medications (id, prescription_id, medication_name, dosage, frequency, duration, instructions) VALUES
-- Jane's general checkup
('med-001', 'prs-001', 'Vitamin D3', '60000 IU', 'Once weekly', '8 weeks', 'Take after breakfast'),
('med-002', 'prs-001', 'Calcium + Vitamin D', '500mg', 'Once daily', '30 days', 'Take with meals'),
-- Jane's cardiology prescription
('med-003', 'prs-002', 'Alprazolam', '0.25mg', 'Once daily at night', '15 days', 'Take before sleep. Do not drive after taking.'),
('med-004', 'prs-002', 'Pantoprazole', '40mg', 'Once daily', '15 days', 'Take 30 minutes before breakfast'),
-- Rahul's fever prescription
('med-005', 'prs-003', 'Paracetamol', '650mg', 'Three times daily', '5 days', 'Take after food. Max 4 tablets per day.'),
('med-006', 'prs-003', 'Cetirizine', '10mg', 'Once daily', '5 days', 'Take at night'),
('med-007', 'prs-003', 'Azithromycin', '500mg', 'Once daily', '3 days', 'Take 1 hour before or 2 hours after meals'),
-- Priya's migraine prescription
('med-008', 'prs-004', 'Sumatriptan', '50mg', 'As needed', '10 tablets', 'Take at onset of migraine. Max 2 tablets per day.'),
('med-009', 'prs-004', 'Propranolol', '20mg', 'Twice daily', '30 days', 'For migraine prevention. Do not stop suddenly.');

-- Seed medical records/reports
INSERT OR IGNORE INTO medical_records (id, patient_id, doctor_id, appointment_id, record_type, title, description, test_date, result_summary, created_at) VALUES
-- Jane's records
('rec-001', 'pat-001', 'doc-001', 'apt-001', 'Lab Test', 'Complete Blood Count (CBC)', 'Routine blood work during annual checkup', '2025-01-15', 'All values within normal range. Hemoglobin: 12.5 g/dL, WBC: 7500/mcL', datetime('now')),
('rec-002', 'pat-001', 'doc-002', 'apt-002', 'Diagnostic', 'ECG Report', '12-lead electrocardiogram', '2025-01-20', 'Normal sinus rhythm. No ST-T changes. Heart rate: 78 bpm', datetime('now')),
('rec-003', 'pat-001', 'doc-002', 'apt-002', 'Lab Test', 'Lipid Profile', 'Cholesterol and lipid levels', '2025-01-20', 'Total Cholesterol: 185 mg/dL, LDL: 110 mg/dL, HDL: 55 mg/dL - Normal', datetime('now')),
-- Rahul's records
('rec-004', 'pat-002', 'doc-001', 'apt-004', 'Lab Test', 'Complete Blood Count (CBC)', 'Blood test for fever evaluation', '2025-01-18', 'WBC elevated: 11000/mcL, suggestive of infection. Other values normal.', datetime('now')),
('rec-005', 'pat-002', 'doc-001', 'apt-004', 'Lab Test', 'Chest X-Ray', 'Rule out pneumonia', '2025-01-18', 'No abnormalities detected. Clear lung fields.', datetime('now')),
-- Priya's records
('rec-006', 'pat-003', 'doc-001', 'apt-006', 'Lab Test', 'Thyroid Function Test', 'To check thyroid levels', '2025-01-22', 'TSH: 2.5 mIU/L, T3: 1.2 ng/mL, T4: 8.5 mcg/dL - All normal', datetime('now'));

-- Seed billing records
INSERT OR IGNORE INTO billing (id, patient_id, appointment_id, description, amount, tax, total, status, payment_method, payment_date, due_date, created_at) VALUES
-- Jane's bills
('bill-001', 'pat-001', 'apt-001', 'General Consultation + CBC Test', 500, 90, 590, 'paid', 'Credit Card', '2025-01-15', '2025-01-22', datetime('now')),
('bill-002', 'pat-001', 'apt-002', 'Cardiology Consultation + ECG + Lipid Profile', 1500, 270, 1770, 'paid', 'UPI', '2025-01-20', '2025-01-27', datetime('now')),
('bill-003', 'pat-001', 'apt-003', 'Dermatology Consultation', 700, 126, 826, 'pending', NULL, NULL, '2025-02-17', datetime('now')),
-- Rahul's bills
('bill-004', 'pat-002', 'apt-004', 'General Consultation + CBC + Chest X-Ray', 1200, 216, 1416, 'paid', 'Net Banking', '2025-01-18', '2025-01-25', datetime('now')),
('bill-005', 'pat-002', 'apt-005', 'Cardiology Screening Package', 2500, 450, 2950, 'pending', NULL, NULL, '2025-02-01', datetime('now')),
-- Priya's bills
('bill-006', 'pat-003', 'apt-006', 'General Consultation + Thyroid Test', 800, 144, 944, 'paid', 'Debit Card', '2025-01-22', '2025-01-29', datetime('now')),
('bill-007', 'pat-003', 'apt-007', 'Dermatology Consultation', 700, 126, 826, 'pending', NULL, NULL, '2025-02-12', datetime('now'));
