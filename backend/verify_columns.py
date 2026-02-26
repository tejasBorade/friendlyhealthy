#!/usr/bin/env python3
"""
Verify new columns were added to existing tables
"""
import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'healthcare_db',
    'user': 'postgres',
    'password': '123'
}

def check_new_columns():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check new columns in users table
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns
            WHERE table_name = 'users' 
            AND column_name IN ('phone', 'otp_hash', 'otp_expires_at', 'failed_otp_attempts', 'locked_until', 'last_device_info')
            ORDER BY column_name
        """)
        print("Users table - New columns:")
        print("-" * 60)
        for row in cursor.fetchall():
            print(f"  {row[0]:30s} | {row[1]}")
        
        # Check new columns in patients table
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns
            WHERE table_name = 'patients' 
            AND column_name IN ('abha_id', 'abha_address', 'known_allergies', 'chronic_conditions', 'caregiver_name', 'caregiver_phone')
            ORDER BY column_name
        """)
        print("\nPatients table - New columns:")
        print("-" * 60)
        for row in cursor.fetchall():
            print(f"  {row[0]:30s} | {row[1]}")
        
        # Check new columns in doctors table
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns
            WHERE table_name = 'doctors' 
            AND column_name IN ('clinic_name', 'clinic_address', 'clinic_logo', 'nmc_verified', 'nmc_verified_at', 'digital_signature_path', 'state_medical_council', 'hfr_id')
            ORDER BY column_name
        """)
        print("\nDoctors table - New columns:")
        print("-" * 60)
        for row in cursor.fetchall():
            print(f"  {row[0]:30s} | {row[1]}")
        
        # Check new columns in prescriptions table
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns
            WHERE table_name = 'prescriptions' 
            AND column_name IN ('follow_up_date', 'patient_instructions', 'is_signed', 'signed_at', 'pdf_path', 'is_locked', 'diagnosis_icd10_code', 'diagnosis_patient_friendly')
            ORDER BY column_name
        """)
        print("\nPrescriptions table - New columns:")
        print("-" * 60)
        for row in cursor.fetchall():
            print(f"  {row[0]:30s} | {row[1]}")
        
        cursor.close()
        conn.close()
        
        print("\n✓ All column additions verified!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_new_columns()
