import asyncpg
import asyncio

async def check_db():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        # Check enum values
        print("Checking enum values...")
        result = await conn.fetch("SELECT unnest(enum_range(NULL::userrole))::text as value")
        print("Enum values:")
        for row in result:
            print(f"  - {row['value']}")
        
        # Check users
        print("\nChecking users...")
        users = await conn.fetch("SELECT id, email, role, is_active, is_deleted FROM users WHERE email = 'patient@test.com'")
        if users:
            for user in users:
                print(f"User found: {user['email']} - Role: {user['role']} - Active: {user['is_active']} - Deleted: {user['is_deleted']}")
        else:
            print("No user found with email patient@test.com")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

asyncio.run(check_db())
