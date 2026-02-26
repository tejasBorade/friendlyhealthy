#!/usr/bin/env python3
"""
Check existing table schemas in the database
"""
import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'healthcare_db',
    'user': 'postgres',
    'password': '123'
}

def check_schemas():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get key table column types
        cursor.execute("""
            SELECT 
                table_name, 
                column_name, 
                data_type,
                udt_name
            FROM information_schema.columns
            WHERE table_schema = 'public' 
            AND table_name IN ('users', 'patients', 'doctors', 'prescriptions', 'medical_reports', 'prescription_medicines')
            AND column_name = 'id'
            ORDER BY table_name, ordinal_position
        """)
        
        print("Existing ID column types:")
        print("-" * 60)
        for row in cursor.fetchall():
            print(f"{row[0]:25s} | {row[1]:15s} | {row[2]:15s} | {row[3]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schemas()
