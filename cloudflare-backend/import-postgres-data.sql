-- Import PostgreSQL users, patients, and doctors to D1
-- Only includes essential columns that exist in D1 schema

-- Users (converting role to lowercase)
INSERT OR IGNORE INTO users (id, email, password_hash, role, is_active, created_at) VALUES 
(2, 'admin@healthcare.com', '$2a$10$vSADuDyO/FVkkpw17F6lF.tcNT8Q1YHykLvwa7iIWNtSp3WKRIac6', 'admin', 1, '2026-02-08T20:31:39.445206'),
(3, 'doctor@healthcare.com', '$2a$10$Y/cJxYM3JvsdoeCsEX086eUUz/cuwRP3pe/oONEeCsJk0f5dC2wrO', 'doctor', 1, '2026-02-08T20:31:39.452076'),
(5, 'patient@healthcare.com', '$2a$10$buthZAmPXt4wiUhvi5aXPel5wcb55p.2OG0QEmgKbk7E3QVJcW8GG', 'patient', 1, '2026-02-08T20:31:39.478572'),
(8, 'sarah.johnson@healthcare.com', '$2a$10$Rgq2PanKy1eXAbDsct7Dx.MH7n2W1szScLEBdR2fSwhgqeWcWrIGO', 'doctor', 1, '2026-02-08T20:53:34.955672'),
(9, 'michael.chen@healthcare.com', '$2a$10$JzkkHf67sZbIkpsQfDORiuOWa9CDARRN2tkhdBuR4ZP6QbNGUbHPG', 'doctor', 1, '2026-02-08T20:53:34.955672'),
(10, 'emily.williams@healthcare.com', '$2a$10$zqS.7B78eP2qTlfo76ItyOP9aBs7bMagpxbftxVb7aGmcEyaa//dC', 'doctor', 1, '2026-02-08T20:53:34.955672'),
(11, 'david.brown@healthcare.com', '$2a$10$zod.o0dbR/lBmcwomcqgmeLPKhXT9STxh5iN7.Gw3qyIFPcYArfz6', 'doctor', 1, '2026-02-08T20:53:34.955672'),
(12, 'lisa.martinez@healthcare.com', '$2a$10$G9sVe5WhDyb5X1X1qphu7uWJYnu3nXxH9MfjjabkxpECYWfH/AXEK', 'doctor', 1, '2026-02-08T20:53:34.955672'),
(29, 'patient@test.com', '$2b$12$UtNLTKAoCrLOY/RT720TxOPFBn3tf9v8gPT8vdn9A2k6b3RasUte2', 'patient', 1, '2026-02-28T01:03:53.612902'),
(30, 'doctor@test.com', '$2b$12$Br2bVHX1Wv8kCFViFwRWHumQR5vOxOwQhlCYcKObPksTkvXoKT54e', 'doctor', 1, '2026-03-01T14:02:34.543038'),
(31, 'mazaemailghe@gmail.com', '$2b$12$HqNLbBM8NB9kXzu/h2Z9POiDWOj7Y4w8tbXgWgczA35jIOm5eb1yK', 'patient', 1, '2026-03-01T14:37:53.025375'),
(32, 'tejas.jrb@gmail.com', '$2b$12$8tHZ5/Nn/gsun7rYk.k2Nu3zcroky2croAqqZIRcu3g7fiULKHj9S', 'doctor', 1, '2026-03-01T14:37:53.661613');

-- Patients (matching D1 schema)
INSERT OR IGNORE INTO patients (id, user_id, first_name, last_name, date_of_birth, gender, phone, address, city, state, zip_code, blood_group, created_at) VALUES 
(2, 5, 'Patient', 'User', '1990-01-01', 'male', '555-0000', '123 Test Street', 'Mumbai', 'Maharashtra', '400001', 'O+', '2026-02-08T22:17:21.829897'),
(3, 29, 'Test', 'Patient', '1990-01-01', 'male', '9876543210', '123 Test Street', 'Mumbai', 'Maharashtra', '400001', 'O+', '2026-02-28T20:54:28.452943'),
(4, 31, 'Maza', 'Patient', '1990-01-01', 'male', '9876543210', '123 Patient Street', 'Mumbai', 'Maharashtra', '400001', 'O+', '2026-03-01T14:37:53.025375');

-- Doctors (matching D1 schema)
INSERT OR IGNORE INTO doctors (id, user_id, first_name, last_name, gender, phone, registration_number, qualification, experience_years, consultation_fee, created_at) VALUES 
(1, 8, 'Sarah', 'Johnson', 'female', '555-0101', 'MH-DOC-8', 'MD, FACC', 15, 150.00, '2026-02-08T20:53:34.955672'),
(2, 9, 'Michael', 'Chen', 'male', '555-0102', 'MH-DOC-9', 'MD, PhD', 12, 180.00, '2026-02-08T20:53:34.955672'),
(3, 10, 'Emily', 'Williams', 'female', '555-0103', 'MH-DOC-10', 'MD, FAAP', 10, 120.00, '2026-02-08T20:53:34.955672'),
(4, 11, 'David', 'Brown', 'male', '555-0104', 'MH-DOC-11', 'MD, FAAOS', 18, 160.00, '2026-02-08T20:53:34.955672'),
(5, 12, 'Lisa', 'Martinez', 'female', '555-0105', 'MH-DOC-12', 'MD, FAAD', 8, 130.00, '2026-02-08T20:53:34.955672'),
(6, 30, 'Test', 'Doctor', 'male', '555-9999', 'MH-DOC-30', 'MBBS, MD', 5, 500.00, '2026-03-01T14:02:34.543038'),
(7, 32, 'Tejas', 'JRB', 'male', '555-8888', 'MH-DOC-32', 'MBBS, MD', 5, 600.00, '2026-03-01T14:37:53.661613');
