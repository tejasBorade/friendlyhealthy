import asyncpg
import asyncio

async def check_id_types():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    # Check patients table
    patients_cols = await conn.fetch("""
        SELECT column_name, data_type, udt_name
        FROM information_schema.columns
        WHERE table_name = 'patients' AND column_name IN ('id', 'user_id')
        ORDER BY ordinal_position
    """)
    
    print("\n" + "="*60)
    print("  PATIENTS TABLE ID TYPES")
    print("="*60)
    for col in patients_cols:
        print(f"  {col['column_name']:20} : {col['data_type']:20} ({col['udt_name']})")
    
    # Check doctors table
    doctors_cols = await conn.fetch("""
        SELECT column_name, data_type, udt_name
        FROM information_schema.columns
        WHERE table_name = 'doctors' AND column_name IN ('id', 'user_id')
        ORDER BY ordinal_position
    """)
    
    print("\n" + "="*60)
    print("  DOCTORS TABLE ID TYPES")
    print("="*60)
    for col in doctors_cols:
        print(f"  {col['column_name']:20} : {col['data_type']:20} ({col['udt_name']})")
    
    # Check appointments table
    appointments_cols = await conn.fetch("""
        SELECT column_name, data_type, udt_name
        FROM information_schema.columns
        WHERE table_name = 'appointments' AND column_name IN ('id', 'patient_id', 'doctor_id')
        ORDER BY ordinal_position
    """)
    
    print("\n" + "="*60)
    print("  APPOINTMENTS TABLE ID TYPES")
    print("="*60)
    for col in appointments_cols:
        print(f"  {col['column_name']:20} : {col['data_type']:20} ({col['udt_name']})")
    
    # Check users table
    users_cols = await conn.fetch("""
        SELECT column_name, data_type, udt_name
        FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'id'
        ORDER BY ordinal_position
    """)
    
    print("\n" + "="*60)
    print("  USERS TABLE ID TYPES")
    print("="*60)
    for col in users_cols:
        print(f"  {col['column_name']:20} : {col['data_type']:20} ({col['udt_name']})")
    
    # Sample data from each table
    sample_patient = await conn.fetchrow("SELECT id, user_id FROM patients LIMIT 1")
    print("\n" + "="*60)
    print("  SAMPLE PATIENT IDS")
    print("="*60)
    if sample_patient:
        print(f"  id: {sample_patient['id']} (type: {type(sample_patient['id']).__name__})")
        print(f"  user_id: {sample_patient['user_id']} (type: {type(sample_patient['user_id']).__name__})")
    
    sample_doctor = await conn.fetchrow("SELECT id, user_id FROM doctors LIMIT 1")
    print("\n" + "="*60)
    print("  SAMPLE DOCTOR IDS")
    print("="*60)
    if sample_doctor:
        print(f"  id: {sample_doctor['id']} (type: {type(sample_doctor['id']).__name__})")
        print(f"  user_id: {sample_doctor['user_id']} (type: {type(sample_doctor['user_id']).__name__})")
    
    await conn.close()

asyncio.run(check_id_types())
