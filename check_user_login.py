import asyncpg
import asyncio
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def check_user():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        # Check if user exists
        user = await conn.fetchrow("""
            SELECT id, email, password_hash, role, is_active, is_deleted 
            FROM users 
            WHERE email = 'patient@test.com'
        """)
        
        if user:
            print("User exists:")
            print(f"  Email: {user['email']}")
            print(f"  Role: {user['role']}")
            print(f"  Active: {user['is_active']}")
            print(f"  Deleted: {user['is_deleted']}")
            print(f"  Password hash length: {len(user['password_hash']) if user['password_hash'] else 0}")
            
            # Test password verification
            if user['password_hash']:
                try:
                    result = pwd_context.verify('Test@123', user['password_hash'])
                    print(f"  Password verification: {'SUCCESS' if result else 'FAILED'}")
                except Exception as e:
                    print(f"  Password verification ERROR: {e}")
        else:
            print("User NOT FOUND in database")
            print("\nTrying to create user...")
            
            # Create user manually
            password_hash = pwd_context.hash('Test@123')
            await conn.execute("""
                INSERT INTO users (email, password_hash, role, is_active, is_verified, is_deleted)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, 'patient@test.com', password_hash, 'PATIENT', True, False, False)
            
            print("User created successfully!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

asyncio.run(check_user())
