-- ============================================================
-- Complete Migration: Drop and Recreate All Tables
-- ============================================================

PRAGMA foreign_keys = OFF;

-- Drop all existing tables
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS prescription_history;
DROP TABLE IF EXISTS prescription_medicines;
DROP TABLE IF EXISTS prescription_medications;
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
DROP TABLE IF EXISTS billing;
DROP TABLE IF EXISTS users;

PRAGMA foreign_keys = ON;
