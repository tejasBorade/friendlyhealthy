#!/usr/bin/env python3
"""
Execute SQL migration script against PostgreSQL database
"""
import psycopg2
import sys
import os

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'healthcare_db',
    'user': 'postgres',
    'password': '123'
}

# Migration file path
MIGRATION_FILE = os.path.join(os.path.dirname(__file__), 'migrations', '001_symptotrack_schema_integer.sql')

def run_migration():
    """Execute the SQL migration script"""
    try:
        # Read the SQL file
        print(f"Reading migration file: {MIGRATION_FILE}")
        with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Connect to PostgreSQL
        print(f"Connecting to database: {DB_CONFIG['database']}...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_session(autocommit=False)
        cursor = conn.cursor()
        
        # Execute the script
        print("Executing migration script...")
        cursor.execute(sql_script)
        
        # Commit the transaction
        conn.commit()
        print("✓ Migration executed successfully!")
        
        # Get table count to verify
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        table_count = cursor.fetchone()[0]
        print(f"✓ Total tables in database: {table_count}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return 0
        
    except psycopg2.Error as e:
        print(f"✗ Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return 1
    except FileNotFoundError:
        print(f"✗ Migration file not found: {MIGRATION_FILE}")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_migration())
