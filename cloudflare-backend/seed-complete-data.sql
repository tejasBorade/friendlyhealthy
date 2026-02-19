-- ============================================================
-- Complete Seed Data for Healthcare Management Platform
-- Cloudflare D1 Database
-- ============================================================

-- Passwords: Patient@123, Doctor@123, Admin@123

-- ============================================================
-- 1. USERS
-- ============================================================
INSERT OR IGNORE INTO users (id, email, password_hash, role, is_active, is_verified, created_at) VALUES 
-- Admin Users
('usr-admin-001', 'admin@healthcare.com', '$2a$10$u2KCdILjqhwAGlGuhnKyzeiaNqv13L8S4weON8Q4A7ZjvSp.QQCZO', 'admin', 1, 1, datetime('now')),

-- Doctor Users
('usr-doctor-001', 'doctor@healthcare.com', '$2a$10$vdoIDweDHh9scEvVPBz1ruiPH3TMhOALwbEMO1cPsQ1Erbf5tC7Re', 'doctor', 1, 1, datetime('now')),
('usr-doctor-002', 'dr.anjali@healthcare.com', '$2a$10$vdoIDweDHh9scEvVPBz1ruiPH3TMhOALwbEMO1cPsQ1Erbf5tC7Re', 'doctor', 1, 1, datetime('now')),
('usr-doctor-003', 'dr.vikram@healthcare.com', '$2a$10$vdoIDweDHh9scEvVPBz1ruiPH3TMhOALwbEMO1cPsQ1Erbf5tC7Re', 'doctor', 1, 1, datetime('now')),
('usr-doctor-004', 'dr.priya@healthcare.com', '$2a$10$vdoIDweDHh9scEvVPBz1ruiPH3TMhOALwbEMO1cPsQ1Erbf5tC7Re', 'doctor', 1, 1, datetime('now')),

-- Patient Users
('usr-patient-001', 'patient@healthcare.com', '$2a$10$SuND/3UvAvEQkxw5EzdLTeY3av1bv3n8Sf0WkZ6OZN69Es6VAspqC', 'patient', 1, 1, datetime('now')),
('usr-patient-002', 'rahul.sharma@email.com', '$2a$10$SuND/3UvAvEQkxw5EzdLTeY3av1bv3n8Sf0WkZ6OZN69Es6VAspqC', 'patient', 1, 1, datetime('now')),
('usr-patient-003', 'priya.patel@email.com', '$2a$10$SuND/3UvAvEQkxw5EzdLTeY3av1bv3n8Sf0WkZ6OZN69Es6VAspqC', 'patient', 1, 1, datetime('now')),
('usr-patient-004', 'amit.singh@email.com', '$2a$10$SuND/3UvAvEQkxw5EzdLTeY3av1bv3n8Sf0WkZ6OZN69Es6VAspqC', 'patient', 1, 1, datetime('now')),
('usr-patient-005', 'neha.reddy@email.com', '$2a$10$SuND/3UvAvEQkxw5EzdLTeY3av1bv3n8Sf0WkZ6OZN69Es6VAspqC', 'patient', 1, 1, datetime('now'));

-- ============================================================
-- 2. PATIENTS
-- ============================================================
INSERT OR IGNORE INTO patients (id, user_id, first_name, last_name, date_of_birth, gender, phone, alternate_phone, address, city, state, zip_code, emergency_contact_name, emergency_contact_phone, blood_group, created_at) VALUES
('pat-001', 'usr-patient-001', 'Jane', 'Doe', '1990-05-15', 'female', '9876543211', '9876543299', '456 Health Street, Andheri West', 'Mumbai', 'Maharashtra', '400001', 'Robert Doe', '9876543298', 'O+', datetime('now')),
('pat-002', 'usr-patient-002', 'Rahul', 'Sharma', '1985-08-22', 'male', '9876543212', NULL, '78 Green Park Colony, Bandra East', 'Mumbai', 'Maharashtra', '400002', 'Neeta Sharma', '9876543297', 'B+', datetime('now')),
('pat-003', 'usr-patient-003', 'Priya', 'Patel', '1992-12-10', 'female', '9876543213', '9876543296', '12 Sunshine Apartments, Juhu', 'Mumbai', 'Maharashtra', '400003', 'Raj Patel', '9876543295', 'A+', datetime('now')),
('pat-004', 'usr-patient-004', 'Amit', 'Singh', '1988-03-25', 'male', '9876543214', NULL, '45 Lake View, Powai', 'Mumbai', 'Maharashtra', '400004', 'Sunita Singh', '9876543294', 'AB+', datetime('now')),
('pat-005', 'usr-patient-005', 'Neha', 'Reddy', '1995-07-18', 'female', '9876543215', NULL, '23 Palm Heights, Malad', 'Mumbai', 'Maharashtra', '400005', 'Arun Reddy', '9876543293', 'O-', datetime('now'));

-- ============================================================
-- 3. DOCTORS
-- ============================================================
INSERT OR IGNORE INTO doctors (id, user_id, first_name, last_name, gender, phone, registration_number, qualification, experience_years, consultation_fee, about, is_verified, rating, total_reviews, clinic_name, clinic_address, clinic_phone, created_at) VALUES
('doc-001', 'usr-doctor-001', 'John', 'Smith', 'male', '9876543210', 'MH-MED-12345', 'MBBS, MD (General Medicine)', 10, 500, 'Experienced general physician specializing in preventive care and chronic disease management.', 1, 4.5, 127, 'Apollo Medical Center', 'Andheri West, Mumbai - 400053', '022-28501234', datetime('now')),
('doc-002', 'usr-doctor-002', 'Anjali', 'Gupta', 'female', '9876543220', 'MH-CARD-67890', 'MBBS, MD, DM (Cardiology)', 15, 1000, 'Senior cardiologist with expertise in interventional cardiology and heart failure management.', 1, 4.8, 245, 'Heart Care Clinic', 'Bandra East, Mumbai - 400051', '022-26401234', datetime('now')),
('doc-003', 'usr-doctor-003', 'Vikram', 'Mehta', 'male', '9876543230', 'MH-DERM-34567', 'MBBS, MD (Dermatology)', 8, 700, 'Dermatologist specializing in cosmetic dermatology, acne treatment, and skin allergies.', 1, 4.3, 89, 'Skin & Care Center', 'Juhu, Mumbai - 400049', '022-26301234', datetime('now')),
('doc-004', 'usr-doctor-004', 'Priya', 'Desai', 'female', '9876543240', 'MH-PEDI-89012', 'MBBS, MD (Pediatrics)', 12, 600, 'Pediatrician with special interest in child development, vaccination, and nutrition.', 1, 4.7, 156, 'Kids First Clinic', 'Powai, Mumbai - 400076', '022-25601234', datetime('now'));

-- ============================================================
-- 4. DOCTOR SPECIALIZATIONS
-- ============================================================
INSERT OR IGNORE INTO doctor_specializations (id, doctor_id, specialization_id, is_primary, created_at) VALUES
('ds-001', 'doc-001', 'spec-01', 1, datetime('now')),
('ds-002', 'doc-002', 'spec-02', 1, datetime('now')),
('ds-003', 'doc-003', 'spec-03', 1, datetime('now')),
('ds-004', 'doc-004', 'spec-05', 1, datetime('now'));

-- ============================================================
-- 5. CLINICS
-- ============================================================
INSERT OR IGNORE INTO clinics (id, doctor_id, name, address, city, state, zip_code, phone, is_primary, created_at) VALUES
('clinic-001', 'doc-001', 'Apollo Medical Center', 'New Link Road, Andheri West', 'Mumbai', 'Maharashtra', '400053', '022-28501234', 1, datetime('now')),
('clinic-002', 'doc-002', 'Heart Care Clinic', 'LBS Marg, Bandra East', 'Mumbai', 'Maharashtra', '400051', '022-26401234', 1, datetime('now')),
('clinic-003', 'doc-003', 'Skin & Care Center', 'Juhu Tara Road, Juhu', 'Mumbai', 'Maharashtra', '400049', '022-26301234', 1, datetime('now')),
('clinic-004', 'doc-004', 'Kids First Clinic', 'Hiranandani Gardens, Powai', 'Mumbai', 'Maharashtra', '400076', '022-25601234', 1, datetime('now'));

-- ============================================================
-- 6. DOCTOR AVAILABILITY
-- ============================================================
INSERT OR IGNORE INTO doctor_availability (id, doctor_id, clinic_id, day_of_week, start_time, end_time, slot_duration, is_active, created_at) VALUES
-- Dr. John Smith - Mon to Sat
('avail-001', 'doc-001', 'clinic-001', 'monday', '09:00', '17:00', 30, 1, datetime('now')),
('avail-002', 'doc-001', 'clinic-001', 'tuesday', '09:00', '17:00', 30, 1, datetime('now')),
('avail-003', 'doc-001', 'clinic-001', 'wednesday', '09:00', '17:00', 30, 1, datetime('now')),
('avail-004', 'doc-001', 'clinic-001', 'thursday', '09:00', '17:00', 30, 1, datetime('now')),
('avail-005', 'doc-001', 'clinic-001', 'friday', '09:00', '17:00', 30, 1, datetime('now')),
('avail-006', 'doc-001', 'clinic-001', 'saturday', '09:00', '13:00', 30, 1, datetime('now')),
-- Dr. Anjali Gupta - Mon to Fri
('avail-007', 'doc-002', 'clinic-002', 'monday', '10:00', '18:00', 30, 1, datetime('now')),
('avail-008', 'doc-002', 'clinic-002', 'tuesday', '10:00', '18:00', 30, 1, datetime('now')),
('avail-009', 'doc-002', 'clinic-002', 'wednesday', '10:00', '18:00', 30, 1, datetime('now')),
('avail-010', 'doc-002', 'clinic-002', 'thursday', '10:00', '18:00', 30, 1, datetime('now')),
('avail-011', 'doc-002', 'clinic-002', 'friday', '10:00', '18:00', 30, 1, datetime('now')),
-- Dr. Vikram Mehta - Tue, Thu, Sat
('avail-012', 'doc-003', 'clinic-003', 'tuesday', '11:00', '19:00', 30, 1, datetime('now')),
('avail-013', 'doc-003', 'clinic-003', 'thursday', '11:00', '19:00', 30, 1, datetime('now')),
('avail-014', 'doc-003', 'clinic-003', 'saturday', '10:00', '16:00', 30, 1, datetime('now')),
-- Dr. Priya Desai - Mon to Sat
('avail-015', 'doc-004', 'clinic-004', 'monday', '09:00', '15:00', 20, 1, datetime('now')),
('avail-016', 'doc-004', 'clinic-004', 'tuesday', '09:00', '15:00', 20, 1, datetime('now')),
('avail-017', 'doc-004', 'clinic-004', 'wednesday', '09:00', '15:00', 20, 1, datetime('now')),
('avail-018', 'doc-004', 'clinic-004', 'thursday', '09:00', '15:00', 20, 1, datetime('now')),
('avail-019', 'doc-004', 'clinic-004', 'friday', '09:00', '15:00', 20, 1, datetime('now')),
('avail-020', 'doc-004', 'clinic-004', 'saturday', '09:00', '13:00', 20, 1, datetime('now'));

-- ============================================================
-- 7. APPOINTMENTS
-- ============================================================
INSERT OR IGNORE INTO appointments (id, appointment_number, patient_id, doctor_id, clinic_id, appointment_date, appointment_time, duration, status, reason_for_visit, symptoms, doctor_notes, created_at) VALUES
-- Jane Doe's appointments
('apt-001', 'APT202601150001', 'pat-001', 'doc-001', 'clinic-001', '2025-01-15', '10:00', 30, 'completed', 'Annual health checkup', 'No major complaints, routine checkup required', 'Patient in good general health. Vitals normal.', datetime('now')),
('apt-002', 'APT202601200002', 'pat-001', 'doc-002', 'clinic-002', '2025-01-20', '14:30', 30, 'completed', 'Chest pain evaluation', 'Mild chest discomfort for 2 days, anxiety', 'ECG normal. Anxiety-related symptoms. Advised stress management.', datetime('now')),
('apt-003', 'APT202602100003', 'pat-001', 'doc-003', 'clinic-003', '2026-02-28', '11:00', 30, 'confirmed', 'Skin rash consultation', 'Allergic reaction on arms', NULL, datetime('now')),

-- Rahul Sharma's appointments
('apt-004', 'APT202601180004', 'pat-002', 'doc-001', 'clinic-001', '2025-01-18', '09:30', 30, 'completed', 'Fever and cold', 'High fever 102°F for 3 days, body ache', 'Viral fever. Rest advised. Symptomatic treatment given.', datetime('now')),
('apt-005', 'APT202602250005', 'pat-002', 'doc-002', 'clinic-002', '2026-03-05', '16:00', 30, 'confirmed', 'Heart health screening', 'Family history of heart disease, preventive checkup', NULL, datetime('now')),

-- Priya Patel's appointments
('apt-006', 'APT202601220006', 'pat-003', 'doc-001', 'clinic-001', '2025-01-22', '11:30', 30, 'completed', 'Migraine issues', 'Chronic headaches, 3-4 times per week', 'Chronic migraine. Lifestyle modification advised.', datetime('now')),
('apt-007', 'APT202602050007', 'pat-003', 'doc-003', 'clinic-003', '2026-03-10', '15:00', 30, 'booked', 'Acne treatment', 'Hormonal acne on face', NULL, datetime('now')),

-- Amit Singh's appointments
('apt-008', 'APT202601250008', 'pat-004', 'doc-001', 'clinic-001', '2025-01-25', '14:00', 30, 'completed', 'Diabetes follow-up', 'Diabetic patient, regular monitoring', 'Blood sugar controlled. Continue medication.', datetime('now')),

-- Neha Reddy's appointments
('apt-009', 'APT202602010009', 'pat-005', 'doc-004', 'clinic-004', '2026-02-25', '10:00', 20, 'confirmed', 'Child vaccination', 'Daughter 2 years old, vaccination due', NULL, datetime('now')),
('apt-010', 'APT202602200010', 'pat-003', 'doc-002', 'clinic-002', '2026-03-15', '11:00', 30, 'booked', 'Chest pain', 'Occasional chest pain', NULL, datetime('now'));

-- ============================================================
-- 8. CONSULTATIONS
-- ============================================================
INSERT OR IGNORE INTO consultations (id, appointment_id, patient_id, doctor_id, consultation_date, chief_complaint, diagnosis, consultation_notes, follow_up_required, follow_up_after_days, created_at) VALUES
('cons-001', 'apt-001', 'pat-001', 'doc-001', '2025-01-15 10:00:00', 'Annual health checkup', 'General health - Good condition', 'Patient is in good health. BMI normal. BP: 120/80. Continue healthy lifestyle and regular exercise.', 0, NULL, datetime('now')),
('cons-002', 'apt-002', 'pat-001', 'doc-002', '2025-01-20 14:30:00', 'Chest pain', 'Mild Anxiety-related chest discomfort', 'ECG normal. No cardiac issues. Stress and anxiety causing symptoms. Recommended stress management techniques and light exercise.', 1, 30, datetime('now')),
('cons-003', 'apt-004', 'pat-002', 'doc-001', '2025-01-18 09:30:00', 'Fever and cold', 'Viral Fever with Upper Respiratory Tract Infection', 'Temperature: 101.5°F. Throat congestion present. Seasonal viral infection. Rest advised for 5 days. Symptomatic treatment prescribed.', 1, 7, datetime('now')),
('cons-004', 'apt-006', 'pat-003', 'doc-001', '2025-01-22 11:30:00', 'Migraine', 'Chronic Migraine', 'Frequent headaches triggered by stress and irregular sleep. Patient reports 3-4 episodes per week. Lifestyle modification and prophylactic medication recommended.', 1, 21, datetime('now')),
('cons-005', 'apt-008', 'pat-004', 'doc-001', '2025-01-25 14:00:00', 'Diabetes monitoring', 'Type 2 Diabetes Mellitus - Well controlled', 'HbA1c: 6.8%. Fasting sugar: 110 mg/dL. Patient compliant with medication. Diet control good. Continue current medication regimen.', 1, 90, datetime('now'));

-- ============================================================
-- 9. PRESCRIPTIONS
-- ============================================================
INSERT OR IGNORE INTO prescriptions (id, prescription_number, consultation_id, patient_id, doctor_id, prescription_date, notes, special_instructions, version, created_at) VALUES
('prs-001', 'RX202501150001', 'cons-001', 'pat-001', 'doc-001', '2025-01-15', 'Vitamin supplements for general health maintenance', 'Continue for 2 months. Take with food.', 1, datetime('now')),
('prs-002', 'RX202501200002', 'cons-002', 'pat-001', 'doc-002', '2025-01-20', 'Medication for anxiety and gastric discomfort', 'Avoid driving after taking Alprazolam. Take Pantoprazole before breakfast.', 1, datetime('now')),
('prs-003', 'RX202501180003', 'cons-003', 'pat-002', 'doc-001', '2025-01-18', 'Symptomatic treatment for viral fever', 'Complete the full course of antibiotics. Rest and adequate fluid intake important.', 1, datetime('now')),
('prs-004', 'RX202501220004', 'cons-004', 'pat-003', 'doc-001', '2025-01-22', 'Migraine prophylaxis and acute treatment', 'Maintain sleep schedule. Avoid triggers. Take Sumatriptan at onset of migraine.', 1, datetime('now')),
('prs-005', 'RX202501250005', 'cons-005', 'pat-004', 'doc-001', '2025-01-25', 'Diabetes management continuation', 'Monitor fasting sugar weekly. Maintain diet and exercise regimen.', 1, datetime('now'));

-- ============================================================
-- 10. PRESCRIPTION MEDICINES
-- ============================================================
INSERT OR IGNORE INTO prescription_medicines (id, prescription_id, medicine_name, dosage, usage, frequency, duration_days, usage_timing, frequency_pattern, special_instructions, created_at) VALUES
-- Jane's general checkup prescription
('med-001', 'prs-001', 'Vitamin D3', '60000 IU', 'after_food', 'Once weekly', 56, 'after_food', 'Weekly', 'Take after breakfast on Sunday', datetime('now')),
('med-002', 'prs-001', 'Calcium + Vitamin D', '500mg', 'with_food', 'Once daily', 60, 'with_food', '1-0-0', 'Take with breakfast', datetime('now')),

-- Jane's cardiology prescription
('med-003', 'prs-002', 'Alprazolam', '0.25mg', 'before_sleep', 'Once daily at night', 15, 'before_sleep', '0-0-1', 'Take before sleep. Do not drive after taking.', datetime('now')),
('med-004', 'prs-002', 'Pantoprazole', '40mg', 'before_food', 'Once daily', 15, 'before_food', '1-0-0', 'Take 30 minutes before breakfast', datetime('now')),

-- Rahul's fever prescription
('med-005', 'prs-003', 'Paracetamol', '650mg', 'after_food', 'Three times daily', 5, 'after_food', '1-1-1', 'Take after food. Max 4 tablets per day. For fever above 100°F.', datetime('now')),
('med-006', 'prs-003', 'Cetirizine', '10mg', 'after_food', 'Once daily at night', 5, 'after_food', '0-0-1', 'For cold and allergy symptoms', datetime('now')),
('med-007', 'prs-003', 'Azithromycin', '500mg', 'before_food', 'Once daily', 3, 'before_food', '1-0-0', 'Take 1 hour before or 2 hours after meals. Complete course.', datetime('now')),

-- Priya's migraine prescription
('med-008', 'prs-004', 'Sumatriptan', '50mg', 'any_time', 'As needed for migraine', 30, 'any_time', 'SOS', 'Take at onset of migraine. Max 2 tablets per day. Do not exceed dose.', datetime('now')),
('med-009', 'prs-004', 'Propranolol', '20mg', 'after_food', 'Twice daily', 30, 'after_food', '1-0-1', 'For migraine prevention. Do not stop suddenly. Take after meals.', datetime('now')),

-- Amit's diabetes medication
('med-010', 'prs-005', 'Metformin', '500mg', 'after_food', 'Twice daily', 90, 'after_food', '1-0-1', 'Take after breakfast and dinner. Monitor blood sugar.', datetime('now')),
('med-011', 'prs-005', 'Glimepiride', '2mg', 'before_food', 'Once daily', 90, 'before_food', '1-0-0', 'Take before breakfast. May cause hypoglycemia - keep sugar handy.', datetime('now'));

-- ============================================================
-- 11. MEDICAL REPORTS
-- ============================================================
INSERT OR IGNORE INTO medical_reports (id, patient_id, doctor_id, appointment_id, report_type, report_name, test_date, test_name, lab_name, report_file_path, result_summary, doctor_remarks, uploaded_by, created_at) VALUES
-- Jane's reports
('rep-001', 'pat-001', 'doc-001', 'apt-001', 'blood_test', 'Complete Blood Count (CBC)', '2025-01-15', 'CBC', 'PathLab Diagnostics', '/reports/pat-001/cbc-20250115.pdf', 'All values within normal range. Hemoglobin: 12.5 g/dL, WBC: 7500/mcL, Platelets: 250000/mcL', 'Normal blood count. Good health.', 'usr-doctor-001', datetime('now')),
('rep-002', 'pat-001', 'doc-002', 'apt-002', 'ecg', 'ECG Report', '2025-01-20', '12-lead ECG', 'Heart Care Clinic Lab', '/reports/pat-001/ecg-20250120.pdf', 'Normal sinus rhythm. No ST-T changes. Heart rate: 78 bpm. No abnormalities detected.', 'Cardiac function normal. No concerns.', 'usr-doctor-002', datetime('now')),
('rep-003', 'pat-001', 'doc-002', 'apt-002', 'blood_test', 'Lipid Profile', '2025-01-20', 'Lipid Panel', 'Heart Care Clinic Lab', '/reports/pat-001/lipid-20250120.pdf', 'Total Cholesterol: 185 mg/dL, LDL: 110 mg/dL, HDL: 55 mg/dL, Triglycerides: 120 mg/dL - All Normal', 'Excellent lipid profile. Continue healthy diet.', 'usr-doctor-002', datetime('now')),

-- Rahul's reports
('rep-004', 'pat-002', 'doc-001', 'apt-004', 'blood_test', 'Complete Blood Count (CBC)', '2025-01-18', 'CBC', 'PathLab Diagnostics', '/reports/pat-002/cbc-20250118.pdf', 'WBC elevated: 11000/mcL, suggestive of infection. Hemoglobin: 14.2 g/dL normal. Other values normal.', 'Elevated WBC indicates viral infection. As expected.', 'usr-doctor-001', datetime('now')),
('rep-005', 'pat-002', 'doc-001', 'apt-004', 'xray', 'Chest X-Ray', '2025-01-18', 'Chest PA View', 'Apollo Imaging Center', '/reports/pat-002/xray-20250118.pdf', 'No abnormalities detected. Clear lung fields. Heart size normal. No infiltrates.', 'No pneumonia. Viral URTI confirmed.', 'usr-doctor-001', datetime('now')),

-- Priya's reports
('rep-006', 'pat-003', 'doc-001', 'apt-006', 'blood_test', 'Thyroid Function Test', '2025-01-22', 'Thyroid Panel (T3, T4, TSH)', 'PathLab Diagnostics', '/reports/pat-003/thyroid-20250122.pdf', 'TSH: 2.5 mIU/L (Normal: 0.5-5.0), T3: 1.2 ng/mL (Normal: 0.8-2.0), T4: 8.5 mcg/dL (Normal: 5-12) - All normal', 'Thyroid function normal. Migraine not thyroid-related.', 'usr-doctor-001', datetime('now')),

-- Amit's reports
('rep-007', 'pat-004', 'doc-001', 'apt-008', 'blood_test', 'HbA1c Test', '2025-01-25', 'Glycated Hemoglobin', 'PathLab Diagnostics', '/reports/pat-004/hba1c-20250125.pdf', 'HbA1c: 6.8% (Good control: <7%). Fasting Sugar: 110 mg/dL (Normal: 70-100)', 'Good diabetic control. Continue current treatment.', 'usr-doctor-001', datetime('now'));

-- ============================================================
-- 12. BILLS
-- ============================================================
INSERT OR IGNORE INTO bills (id, bill_number, patient_id, appointment_id, bill_date, subtotal, tax_amount, discount_amount, total_amount, payment_status, payment_date, payment_method, transaction_id, created_at) VALUES
-- Jane's bills
('bill-001', 'BILL202501150001', 'pat-001', 'apt-001', '2025-01-15', 1300.00, 234.00, 0, 1534.00, 'paid', '2025-01-15', 'Credit Card', 'TXN20250115001', datetime('now')),
('bill-002', 'BILL202501200002', 'pat-001', 'apt-002', '2025-01-20', 2600.00, 468.00, 0, 3068.00, 'paid', '2025-01-20', 'UPI', 'TXN20250120002', datetime('now')),
('bill-003', 'BILL202602100003', 'pat-001', 'apt-003', '2026-02-28', 700.00, 126.00, 0, 826.00, 'pending', NULL, NULL, NULL, datetime('now')),

-- Rahul's bills
('bill-004', 'BILL202501180004', 'pat-002', 'apt-004', '2025-01-18', 1700.00, 306.00, 0, 2006.00, 'paid', '2025-01-18', 'Net Banking', 'TXN20250118004', datetime('now')),
('bill-005', 'BILL202602250005', 'pat-002', 'apt-005', '2026-03-05', 1000.00, 180.00, 0, 1180.00, 'pending', NULL, NULL, NULL, datetime('now')),

-- Priya's bills
('bill-006', 'BILL202501220006', 'pat-003', 'apt-006', '2025-01-22', 1300.00, 234.00, 0, 1534.00, 'paid', '2025-01-22', 'Debit Card', 'TXN20250122006', datetime('now')),
('bill-007', 'BILL202602050007', 'pat-003', 'apt-007', '2026-03-10', 700.00, 126.00, 0, 826.00, 'pending', NULL, NULL, NULL, datetime('now')),

-- Amit's bills
('bill-008', 'BILL202501250008', 'pat-004', 'apt-008', '2025-01-25', 1300.00, 234.00, 0, 1534.00, 'paid', '2025-01-25', 'UPI', 'TXN20250125008', datetime('now')),

-- Neha's bills
('bill-009', 'BILL202602010009', 'pat-005', 'apt-009', '2026-02-25', 600.00, 108.00, 0, 708.00, 'pending', NULL, NULL, NULL, datetime('now'));

-- ============================================================
-- 13. BILL ITEMS
-- ============================================================
INSERT OR IGNORE INTO bill_items (id, bill_id, charge_type_id, description, quantity, unit_price, total_price, created_at) VALUES
-- Bill 001 items
('item-001', 'bill-001', 'charge-01', 'General Consultation - Dr. John Smith', 1, 500.00, 500.00, datetime('now')),
('item-002', 'bill-001', 'charge-04', 'Complete Blood Count (CBC)', 1, 800.00, 800.00, datetime('now')),

-- Bill 002 items
('item-003', 'bill-002', 'charge-01', 'Cardiology Consultation - Dr. Anjali Gupta', 1, 1000.00, 1000.00, datetime('now')),
('item-004', 'bill-002', 'charge-08', 'ECG Test', 1, 600.00, 600.00, datetime('now')),
('item-005', 'bill-002', 'charge-04', 'Lipid Profile Test', 1, 1000.00, 1000.00, datetime('now')),

-- Bill 003 items
('item-006', 'bill-003', 'charge-01', 'Dermatology Consultation - Dr. Vikram Mehta', 1, 700.00, 700.00, datetime('now')),

-- Bill 004 items
('item-007', 'bill-004', 'charge-01', 'General Consultation - Dr. John Smith', 1, 500.00, 500.00, datetime('now')),
('item-008', 'bill-004', 'charge-04', 'CBC Test', 1, 800.00, 800.00, datetime('now')),
('item-009', 'bill-004', 'charge-05', 'Chest X-Ray', 1, 400.00, 400.00, datetime('now')),

-- Bill 005 items
('item-010', 'bill-005', 'charge-01', 'Cardiology Consultation - Dr. Anjali Gupta', 1, 1000.00, 1000.00, datetime('now')),

-- Bill 006 items
('item-011', 'bill-006', 'charge-01', 'General Consultation - Dr. John Smith', 1, 500.00, 500.00, datetime('now')),
('item-012', 'bill-006', 'charge-04', 'Thyroid Function Test', 1, 800.00, 800.00, datetime('now')),

-- Bill 007 items
('item-013', 'bill-007', 'charge-01', 'Dermatology Consultation - Dr. Vikram Mehta', 1, 700.00, 700.00, datetime('now')),

-- Bill 008 items
('item-014', 'bill-008', 'charge-01', 'General Consultation - Dr. John Smith', 1, 500.00, 500.00, datetime('now')),
('item-015', 'bill-008', 'charge-04', 'HbA1c Test', 1, 800.00, 800.00, datetime('now')),

-- Bill 009 items
('item-016', 'bill-009', 'charge-01', 'Pediatric Consultation - Dr. Priya Desai', 1, 600.00, 600.00, datetime('now'));

-- ============================================================
-- 14. PATIENT MEDICAL HISTORY
-- ============================================================
INSERT OR IGNORE INTO patient_medical_history (id, patient_id, doctor_id, appointment_id, recorded_date, allergies, chronic_diseases, surgeries, family_medical_history, current_medications, blood_pressure, temperature, weight, height, notes, created_by, created_at) VALUES
('med-hist-001', 'pat-001', 'doc-001', 'apt-001', '2025-01-15', 'None known', 'None', 'Appendectomy (2010)', 'Father - Hypertension, Mother - Diabetes', 'Vitamin D3 supplements', '120/80', 98.6, 58.5, 165, 'Patient in excellent general health.', 'usr-doctor-001', datetime('now')),
('med-hist-002', 'pat-002', 'doc-001', 'apt-004', '2025-01-18', 'Penicillin allergy', 'None', 'None', 'Mother - Asthma', 'None', '125/82', 101.5, 72.0, 175, 'Viral fever episode.', 'usr-doctor-001', datetime('now')),
('med-hist-003', 'pat-003', 'doc-001', 'apt-006', '2025-01-22', 'None known', 'Chronic Migraine', 'None', 'Father - Migraine', 'Occasional painkillers', '118/78', 98.4, 54.0, 160, 'Chronic migraine patient. Stress-related triggers.', 'usr-doctor-001', datetime('now')),
('med-hist-004', 'pat-004', 'doc-001', 'apt-008', '2025-01-25', 'None known', 'Type 2 Diabetes Mellitus (5 years)', 'None', 'Father - Diabetes, Mother - Hypertension', 'Metformin 500mg, Glimepiride 2mg', '130/85', 98.2, 78.0, 172, 'Diabetic patient with good control. Compliant with medication.', 'usr-doctor-001', datetime('now'));

