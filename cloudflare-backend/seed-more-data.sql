-- Additional dummy users, patients, and appointments

-- Insert more users (patients)
INSERT INTO users (id, email, password, role, first_name, last_name, phone, is_active, created_at) VALUES
('user-006', 'patient6@healthcare.com', '$2b$10$rFZqK7kH8WgjHgcI8kH8Ou8zTZm5xMTZm5xMTZm5xMTZm5xMTZm5xM', 'patient', 'Rahul', 'Sharma', '+91-9876543216', 1, datetime('now')),
('user-007', 'patient7@healthcare.com', '$2b$10$rFZqK7kH8WgjHgcI8kH8Ou8zTZm5xMTZm5xMTZm5xMTZm5xMTZm5xM', 'patient', 'Sneha', 'Reddy', '+91-9876543217', 1, datetime('now')),
('user-008', 'patient8@healthcare.com', '$2b$10$rFZqK7kH8WgjHgcI8kH8Ou8zTZm5xMTZm5xMTZm5xMTZm5xMTZm5xM', 'patient', 'Amit', 'Patel', '+91-9876543218', 1, datetime('now')),
('user-009', 'patient9@healthcare.com', '$2b$10$rFZqK7kH8WgjHgcI8kH8Ou8zTZm5xMTZm5xMTZm5xMTZm5xMTZm5xM', 'patient', 'Neha', 'Kumar', '+91-9876543219', 1, datetime('now')),
('user-010', 'patient10@healthcare.com', '$2b$10$rFZqK7kH8WgjHgcI8kH8Ou8zTZm5xMTZm5xMTZm5xMTZm5xMTZm5xM', 'patient', 'Suresh', 'Singh', '+91-9876543220', 1, datetime('now'));

-- Insert more patients
INSERT INTO patients (id, user_id, first_name, last_name, date_of_birth, gender, phone, email, address, city, state, pincode, blood_group, emergency_contact_name, emergency_contact_phone, created_at) VALUES
('patient-006', 'user-006', 'Rahul', 'Sharma', '1992-05-10', 'Male', '+91-9876543216', 'patient6@healthcare.com', '789 Ring Road', 'Delhi', 'Delhi', '110001', 'A+', 'Pooja Sharma', '+91-9876000006', datetime('now')),
('patient-007', 'user-007', 'Sneha', 'Reddy', '1988-08-25', 'Female', '+91-9876543217', 'patient7@healthcare.com', '456 Lake View', 'Hyderabad', 'Telangana', '500001', 'O+', 'Ravi Reddy', '+91-9876000007', datetime('now')),
('patient-008', 'user-008', 'Amit', 'Patel', '1995-03-12', 'Male', '+91-9876543218', 'patient8@healthcare.com', '123 Gandhi Nagar', 'Ahmedabad', 'Gujarat', '380001', 'B+', 'Priya Patel', '+91-9876000008', datetime('now')),
('patient-009', 'user-009', 'Neha', 'Kumar', '1990-11-30', 'Female', '+91-9876543219', 'patient9@healthcare.com', '567 Mall Road', 'Bangalore', 'Karnataka', '560001', 'AB+', 'Raj Kumar', '+91-9876000009', datetime('now')),
('patient-010', 'user-010', 'Suresh', 'Singh', '1985-01-20', 'Male', '+91-9876543220', 'patient10@healthcare.com', '890 Park Street', 'Mumbai', 'Maharashtra', '400001', 'O-', 'Geeta Singh', '+91-9876000010', datetime('now'));

-- Insert more appointments (mix of past, today, and future)
INSERT INTO appointments (id, patient_id, doctor_id, clinic_id, appointment_date, appointment_time, appointment_type, status, reason_for_visit, notes, created_at) VALUES
('appt-011', 'patient-006', 'doctor-001', 'clinic-001', date('now', '-5 days'), '09:00:00', 'consultation', 'completed', 'Regular health checkup', 'Patient in good health overall', datetime('now', '-6 days')),
('appt-012', 'patient-006', 'doctor-002', 'clinic-002', date('now', '+2 days'), '14:00:00', 'consultation', 'scheduled', 'Follow-up consultation', NULL, datetime('now', '-1 day')),
('appt-013', 'patient-007', 'doctor-003', 'clinic-003', date('now', '-3 days'), '11:30:00', 'consultation', 'completed', 'Joint pain assessment', 'Prescribed physiotherapy', datetime('now', '-4 days')),
('appt-014', 'patient-007', 'doctor-001', 'clinic-001', date('now', '+5 days'), '10:00:00', 'consultation', 'scheduled', 'Routine cardiology check', NULL, datetime('now')),
('appt-015', 'patient-008', 'doctor-004', 'clinic-004', date('now'), '15:00:00', 'consultation', 'scheduled', 'Skin allergy consultation', NULL, datetime('now', '-2 days')),
('appt-016', 'patient-008', 'doctor-002', 'clinic-002', date('now', '-7 days'), '09:30:00', 'consultation', 'completed', 'Vision problems', 'Prescribed reading glasses', datetime('now', '-8 days')),
('appt-017', 'patient-009', 'doctor-003', 'clinic-003', date('now', '+1 day'), '16:00:00', 'consultation', 'scheduled', 'Back pain treatment', NULL, datetime('now', '-1 day')),
('appt-018', 'patient-009', 'doctor-001', 'clinic-001', date('now', '-10 days'), '11:00:00', 'follow_up', 'completed', 'Follow-up after surgery', 'Recovery progressing well', datetime('now', '-11 days')),
('appt-019', 'patient-010', 'doctor-004', 'clinic-004', date('now', '+3 days'), '13:00:00', 'consultation', 'scheduled', 'Diabetes management', NULL, datetime('now')),
('appt-020', 'patient-010', 'doctor-002', 'clinic-002', date('now', '-2 days'), '10:30:00', 'consultation', 'completed', 'General consultation', 'Advised dietary changes', datetime('now', '-3 days'));

-- Insert more medical reports
INSERT INTO medical_reports (id, patient_id, doctor_id, appointment_id, report_type, report_name, test_date, test_name, lab_name, lab_address, lab_phone, report_file_path, file_url, result_summary, doctor_remarks, uploaded_by, created_at) VALUES
('report-008', 'patient-006', 'doctor-001', 'appt-011', 'blood_test', 'Complete Blood Count', date('now', '-5 days'), 'CBC', 'City Diagnostics', '123 Lab Street, Delhi', '+91-9876000101', '/reports/report-008.pdf', NULL, 'Normal', 'All values within range', 'user-002', datetime('now', '-4 days')),
('report-009', 'patient-007', 'doctor-003', 'appt-013', 'xray', 'Knee X-Ray', date('now', '-3 days'), 'Knee Joint X-Ray', 'Medical Imaging Center', '456 Scan Road, Hyderabad', '+91-9876000102', '/reports/report-009.pdf', NULL, 'Minor wear visible', 'Recommended physiotherapy', 'user-004', datetime('now', '-2 days')),
('report-010', 'patient-008', 'doctor-002', 'appt-016', 'other', 'Eye Examination', date('now', '-7 days'), 'Vision Test', 'Eye Care Clinic', '789 Vision Street, Ahmedabad', '+91-9876000103', '/reports/report-010.pdf', NULL, 'Myopia detected', 'Glasses prescribed, power -2.5', 'user-003', datetime('now', '-6 days')),
('report-011', 'patient-010', 'doctor-002', 'appt-020', 'blood_test', 'Blood Sugar Test', date('now', '-2 days'), 'Fasting Blood Sugar', 'Health Labs', '321 Medical Plaza, Mumbai', '+91-9876000104', '/reports/report-011.pdf', NULL, 'Elevated glucose levels', 'Advised dietary control and medication', 'user-003', datetime('now', '-1 day'));

-- Insert more bills
INSERT INTO bills (id, bill_number, patient_id, appointment_id, bill_date, subtotal, tax_amount, discount_amount, total_amount, payment_status, payment_method, payment_date, due_date, notes, created_at) VALUES
('bill-010', 'BILL-2026-010', 'patient-006', 'appt-011', date('now', '-5 days'), 800.00, 144.00, 0.00, 944.00, 'paid', 'UPI', datetime('now', '-5 days'), date('now', '-5 days'), 'Consultation and CBC test', datetime('now', '-5 days')),
('bill-011', 'BILL-2026-011', 'patient-007', 'appt-013', date('now', '-3 days'), 1200.00, 216.00, 100.00, 1316.00, 'paid', 'Card', datetime('now', '-3 days'), date('now', '-3 days'), 'Consultation and X-Ray', datetime('now', '-3 days')),
('bill-012', 'BILL-2026-012', 'patient-008', 'appt-016', date('now', '-7 days'), 600.00, 108.00, 0.00, 708.00, 'paid', 'Cash', datetime('now', '-7 days'), date('now', '-7 days'), 'Eye examination', datetime('now', '-7 days')),
('bill-013', 'BILL-2026-013', 'patient-009', 'appt-018', date('now', '-10 days'), 500.00, 90.00, 50.00, 540.00, 'paid', 'UPI', datetime('now', '-10 days'), date('now', '-10 days'), 'Follow-up consultation', datetime('now', '-10 days')),
('bill-014', 'BILL-2026-014', 'patient-010', 'appt-020', date('now', '-2 days'), 900.00, 162.00, 0.00, 1062.00, 'pending', NULL, NULL, date('now', '+13 days'), 'Blood sugar test and consultation', datetime('now', '-2 days'));

-- Insert bill items for the new bills
INSERT INTO bill_items (id, bill_id, charge_type_id, description, quantity, unit_price, amount, created_at) VALUES
('item-031', 'bill-010', 'charge-001', 'General Consultation', 1, 500.00, 500.00, datetime('now', '-5 days')),
('item-032', 'bill-010', 'charge-005', 'Complete Blood Count', 1, 300.00, 300.00, datetime('now', '-5 days')),
('item-033', 'bill-011', 'charge-003', 'Orthopedic Consultation', 1, 700.00, 700.00, datetime('now', '-3 days')),
('item-034', 'bill-011', 'charge-006', 'Knee X-Ray', 1, 500.00, 500.00, datetime('now', '-3 days')),
('item-035', 'bill-012', 'charge-001', 'Eye Examination', 1, 600.00, 600.00, datetime('now', '-7 days')),
('item-036', 'bill-013', 'charge-002', 'Follow-up Visit', 1, 500.00, 500.00, datetime('now', '-10 days')),
('item-037', 'bill-014', 'charge-001', 'General Consultation', 1, 500.00, 500.00, datetime('now', '-2 days')),
('item-038', 'bill-014', 'charge-005', 'Blood Sugar Test', 1, 400.00, 400.00, datetime('now', '-2 days'));

-- Insert some prescriptions for completed appointments
INSERT INTO prescriptions (id, appointment_id, patient_id, doctor_id, prescription_date, diagnosis, notes, created_at) VALUES
('presc-006', 'appt-013', 'patient-007', 'doctor-003', date('now', '-3 days'), 'Osteoarthritis - Early stage', 'Prescribed pain relief and physiotherapy', datetime('now', '-3 days')),
('presc-007', 'appt-016', 'patient-008', 'doctor-002', date('now', '-7 days'), 'Myopia', 'Glasses prescribed, regular check-ups recommended', datetime('now', '-7 days')),
('presc-008', 'appt-018', 'patient-009', 'doctor-001', date('now', '-10 days'), 'Post-operative care', 'Continue medication, avoid heavy lifting', datetime('now', '-10 days')),
('presc-009', 'appt-020', 'patient-010', 'doctor-002', date('now', '-2 days'), 'Prediabetes', 'Lifestyle modification and medication', datetime('now', '-2 days'));

-- Insert prescription medications
INSERT INTO prescription_medications (id, prescription_id, medicine_name, dosage, frequency, duration, instructions, created_at) VALUES
('med-012', 'presc-006', 'Paracetamol', '500mg', 'Three times daily', '7 days', 'Take after meals', datetime('now', '-3 days')),
('med-013', 'presc-006', 'Ibuprofen', '400mg', 'Twice daily', '7 days', 'Take with food', datetime('now', '-3 days')),
('med-014', 'presc-008', 'Amoxicillin', '500mg', 'Three times daily', '5 days', 'Complete the course', datetime('now', '-10 days')),
('med-015', 'presc-009', 'Metformin', '500mg', 'Twice daily', '30 days', 'Take with meals', datetime('now', '-2 days')),
('med-016', 'presc-009', 'Vitamin D3', '60000 IU', 'Once weekly', '8 weeks', 'Take on empty stomach', datetime('now', '-2 days'));

-- Insert some medical history for new patients
INSERT INTO medical_history (id, patient_id, condition_name, diagnosed_date, status, severity, notes, created_at) VALUES
('history-005', 'patient-006', 'Allergic Rhinitis', '2020-03-15', 'active', 'mild', 'Seasonal allergies, managed with antihistamines', datetime('now')),
('history-006', 'patient-007', 'Osteoarthritis', date('now', '-3 days'), 'active', 'mild', 'Early stage, currently undergoing physiotherapy', datetime('now', '-3 days')),
('history-007', 'patient-008', 'Myopia', date('now', '-7 days'), 'active', 'moderate', 'Requires corrective lenses', datetime('now', '-7 days')),
('history-008', 'patient-010', 'Prediabetes', date('now', '-2 days'), 'active', 'moderate', 'Under medication and lifestyle modification', datetime('now', '-2 days'));
