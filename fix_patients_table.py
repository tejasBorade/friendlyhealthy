import asyncpg
import asyncio

async def fix_patients_table():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    try:
        # Add missing columns
        await conn.execute("""
            ALTER TABLE patients ADD COLUMN IF NOT EXISTS alternate_phone VARCHAR(20);
            ALTER TABLE patients ADD COLUMN IF NOT EXISTS city VARCHAR(100);
            ALTER TABLE patients ADD COLUMN IF NOT EXISTS state VARCHAR(100);
            ALTER TABLE patients ADD COLUMN IF NOT EXISTS zip_code VARCHAR(20);
            ALTER TABLE patients ADD COLUMN IF NOT EXISTS country VARCHAR(100) DEFAULT 'India';
            ALTER TABLE patients ADD COLUMN IF NOT EXISTS emergency_contact_name VARCHAR(200);
            ALTER TABLE patients ADD COLUMN IF NOT EXISTS emergency_contact_phone VARCHAR(20);
            ALTER TABLE patients ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(500);
            ALTER TABLE patients ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
        """)
        
        # Rename emergency_contact to emergency_contact_name if it exists
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'patients' AND column_name = 'emergency_contact'
            )
        """)
        
        if exists:
            # Copy data from emergency_contact to emergency_contact_name
            await conn.execute("""
                UPDATE patients SET emergency_contact_name = emergency_contact 
                WHERE emergency_contact IS NOT NULL AND emergency_contact_name IS NULL
            """)
        
        # Rename emergency_phone to emergency_contact_phone if it exists
        exists_phone = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'patients' AND column_name = 'emergency_phone'
            )
        """)
        
        if exists_phone:
            # Copy data from emergency_phone to emergency_contact_phone
            await conn.execute("""
                UPDATE patients SET emergency_contact_phone = emergency_phone 
                WHERE emergency_phone IS NOT NULL AND emergency_contact_phone IS NULL
            """)
        
        print("patients table fixed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

asyncio.run(fix_patients_table())
