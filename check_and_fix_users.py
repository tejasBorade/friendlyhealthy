import asyncpg
import asyncio

async def check_and_fix():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        # Check if any users exist
        users = await conn.fetch("SELECT id, email, role FROM users LIMIT 5")
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  {user['email']} - role: '{user['role']}' (type: {type(user['role'])})")
        
        if not users:
            print("\n No users found - login will fail with 'user not found' error")
            print("You need to register a user first or create one manually")
        else:
            # Try to update the role column
            print("\nUpdating role column...")
            await conn.execute("""
                -- Convert to VARCHAR first
                ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(50);
                
                -- Update all existing values to uppercase
                UPDATE users SET role = UPPER(role);
            """)
            
            # Drop and recreate enum
            await conn.execute("DROP TYPE IF EXISTS userrole CASCADE;")
            await conn.execute("""
                CREATE TYPE userrole AS ENUM (
                    'PATIENT', 'DOCTOR', 'ADMIN',
                    'VERIFICATION_ADMIN', 'COMPLIANCE_ADMIN', 'SUPPORT_ADMIN'
                );
            """)
            
            # Convert back to enum
            await conn.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole;")
            print("✓ Fixed!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

asyncio.run(check_and_fix())
