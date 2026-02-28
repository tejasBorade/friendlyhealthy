import asyncpg
import asyncio

async def create_refresh_tokens_table():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id UUID PRIMARY KEY,
                user_id INTEGER NOT NULL,
                token VARCHAR(500) UNIQUE NOT NULL,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                revoked_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster lookups
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token)")
        
        print("refresh_tokens table created successfully")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

asyncio.run(create_refresh_tokens_table())
