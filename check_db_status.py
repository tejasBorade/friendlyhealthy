import asyncpg
import asyncio

async def check_db():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        # Check users count
        print("=== DATABASE STATUS ===\n")
        
        tables = ['users', 'patients', 'doctors', 'appointments', 'prescriptions']
        for table in tables:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                print(f"{table:20} : {count:3} records")
            except:
                print(f"{table:20} : Table may not exist")
        
        print("\n=== USER DETAILS ===\n")
        users = await conn.fetch("SELECT id, email, role FROM users ORDER BY id LIMIT 15")
        for user in users:
            print(f"ID: {user['id']:3} | {user['email']:30} | {user['role']}")
        
        print("\n=== PATIENT PROFILES ===\n")
        patients = await conn.fetch("SELECT id, user_id, first_name, last_name FROM patients LIMIT 15")
        if patients:
            for p in patients:
                print(f"ID: {p['id']:3} | User ID: {p['user_id']:3} | {p['first_name']} {p['last_name']}")
        else:
            print("No patient profiles found!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

asyncio.run(check_db())

