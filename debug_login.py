import asyncpg
import asyncio
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def debug_login():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        # Check if user exists
        user = await conn.fetchrow("""
            SELECT id, email, password_hash, role, is_active, is_deleted 
            FROM users 
            WHERE email = 'patient@test.com'
        """)
        
        if not user:
            print("User does not exist. Creating...")
            password_hash = pwd_context.hash('Test@123')
            await conn.execute("""
                INSERT INTO users (email, password_hash, role, is_active, is_verified, is_deleted)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, 'patient@test.com', password_hash, 'patient', True, False, False)
            print("User created!")
            
            # Fetch the newly created user
            user = await conn.fetchrow("""
                SELECT id, email, password_hash, role, is_active, is_deleted 
                FROM users 
                WHERE email = 'patient@test.com'
            """)
        
        print(f"User: {user['email']}")
        print(f"Role: {user['role']}")
        print(f"Active: {user['is_active']}")
        print(f"Deleted: {user['is_deleted']}")
        
        # Test password verification
        test_password = 'Test@123'
        try:
            is_valid = pwd_context.verify(test_password, user['password_hash'])
            print(f"Password verification: {is_valid}")
        except Exception as e:
            print(f"Password verification error: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

asyncio.run(debug_login())
