-- ============================================================
-- DROP ALL EXISTING TABLES (in correct order due to foreign keys)
-- ============================================================

-- Disable foreign key constraints
PRAGMA foreign_keys = OFF;

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS prescription_history;
DROP TABLE IF EXISTS prescription_medicines;
DROP TABLE IF EXISTS prescriptions;
DROP TABLE IF EXISTS consultations;
DROP TABLE IF EXISTS patient_medical_history;
DROP TABLE IF EXISTS medical_reports;
DROP TABLE IF EXISTS bill_items;
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS invoice_items;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS charge_types;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS doctor_leaves;
DROP TABLE IF EXISTS doctor_availability;
DROP TABLE IF EXISTS clinics;
DROP TABLE IF EXISTS doctor_specializations;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS specializations;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS patient_consents;
DROP TABLE IF EXISTS refresh_tokens;
DROP TABLE IF EXISTS system_settings;
DROP TABLE IF EXISTS users;

-- Drop any remaining old tables that might exist
DROP TABLE IF EXISTS prescription_medications;
DROP TABLE IF EXISTS billing;

-- Drop all indexes (optional, as they're dropped with tables)
DROP INDEX IF EXISTS idx_users_email;
DROP INDEX IF EXISTS idx_appointments_patient;
DROP INDEX IF EXISTS idx_appointments_doctor;
DROP INDEX IF EXISTS idx_appointments_date;
DROP INDEX IF EXISTS idx_prescriptions_patient;
DROP INDEX IF EXISTS idx_prescriptions_doctor;
DROP INDEX IF EXISTS idx_medical_records_patient;
DROP INDEX IF EXISTS idx_billing_patient;
