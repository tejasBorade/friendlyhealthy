import asyncpg
import asyncio

async def fix_roles():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        # Update all roles to uppercase
        await conn.execute("UPDATE users SET role = UPPER(role)")
        
        # Verify
        users = await conn.fetch("SELECT email, role FROM users")
        print("Updated users:")
        for user in users:
            print(f"  {user['email']} - {user['role']}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

asyncio.run(fix_roles())
