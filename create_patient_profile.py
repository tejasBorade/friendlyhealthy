import asyncpg
import asyncio

async def create_patient_profile():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    try:
        # Check if patient profile exists for user_id 29
        exists = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM patients WHERE user_id = 29)")
        
        if not exists:
            # Create patient profile
            await conn.execute("""
                INSERT INTO patients (
                    user_id, first_name, last_name, date_of_birth, 
                    gender, phone, blood_group, country
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, 29, 'Test', 'Patient', '1990-01-01', 'male', '+1234567890', 'O+', 'India')
            print("Patient profile created for user_id 29")
        else:
            print("Patient profile already exists for user_id 29")
            
    finally:
        await conn.close()

asyncio.run(create_patient_profile())
