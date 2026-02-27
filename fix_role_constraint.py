import asyncpg
import asyncio

async def fix_role_constraint():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        # Drop the old constraint
        await conn.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check")
        print("Dropped old constraint")
        
        # Update all roles to uppercase
        await conn.execute("UPDATE users SET role = UPPER(role)")
        print("Updated roles to uppercase")
        
        # Add new constraint with uppercase values
        await conn.execute("""
            ALTER TABLE users ADD CONSTRAINT users_role_check 
            CHECK (role IN ('PATIENT', 'DOCTOR', 'ADMIN', 'VERIFICATION_ADMIN', 'COMPLIANCE_ADMIN', 'SUPPORT_ADMIN'))
        """)
        print("Added new constraint")
        
        # Verify
        users = await conn.fetch("SELECT email, role FROM users")
        print("\nUsers:")
        for user in users:
            print(f"  {user['email']} - {user['role']}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

asyncio.run(fix_role_constraint())
