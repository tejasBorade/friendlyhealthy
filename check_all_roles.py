import asyncpg
import asyncio

async def check_roles():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        # Check all unique role values
        roles = await conn.fetch("SELECT DISTINCT role FROM users ORDER BY role")
        print("Unique role values in database:")
        for row in roles:
            print(f"  '{row['role']}'")
        
        # Check all users
        users = await conn.fetch("SELECT id, email, role FROM users")
        print(f"\nAll users ({len(users)}):")
        for user in users:
            print(f"  ID={user['id']} {user['email']:<30} role='{user['role']}'")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

asyncio.run(check_roles())
