import asyncpg
import asyncio

async def check_users():
    try:
        conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
        
        # Count users
        users = await conn.fetch("SELECT id, email, role FROM users ORDER BY created_at DESC LIMIT 10;")
        
        print(f"Total users found: {len(users)}")
        if users:
            print("\nUsers:")
            for user in users:
                print(f"  ID: {user['id']}, Email: {user['email']}, Role: {user['role']}")
        else:
            print("  [NO USERS IN DATABASE - Need to create a test user]")
            
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(check_users())
