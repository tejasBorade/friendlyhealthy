import asyncpg
import asyncio

async def fix_enum():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        # Check current enum values
        result = await conn.fetch("SELECT unnest(enum_range(NULL::userrole))::text as value")
        print("Current enum values:")
        for row in result:
            print(f"  - {row['value']}")
        
        # Drop and recreate the enum with uppercase values
        print("\nRecreating enum with uppercase values...")
        
        # First, check if there are any users
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        print(f"Found {user_count} users in database")
        
        if user_count > 0:
            # Update existing data to uppercase
            print("Updating existing user roles to uppercase...")
            await conn.execute("""
                ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(50);
                UPDATE users SET role = UPPER(role);
            """)
        else:
            await conn.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(50);")
        
        # Drop old enum and create new one
        await conn.execute("DROP TYPE IF EXISTS userrole CASCADE;")
        await conn.execute("""
            CREATE TYPE userrole AS ENUM (
                'PATIENT', 'DOCTOR', 'ADMIN', 
                'VERIFICATION_ADMIN', 'COMPLIANCE_ADMIN', 'SUPPORT_ADMIN'
            );
        """)
        
        # Update column to use new enum
        await conn.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole;")
        
        print("✓ Enum fixed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

asyncio.run(fix_enum())
