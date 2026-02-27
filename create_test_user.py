import asyncpg
import asyncio
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        password_hash = pwd_context.hash('Test@123')
        
        # Create user with lowercase role
        await conn.execute("""
            INSERT INTO users (email, password_hash, role, is_active, is_verified, is_deleted)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (email) DO UPDATE SET password_hash = $2
        """, 'patient@test.com', password_hash, 'patient', True, False, False)
        
        print("User created/updated successfully!")
        
        # Verify user exists
        user = await conn.fetchrow("SELECT email, role FROM users WHERE email = 'patient@test.com'")
        if user:
            print(f"User: {user['email']} - Role: {user['role']}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

asyncio.run(create_user())
