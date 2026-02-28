import asyncpg
import asyncio

async def fix_refresh_tokens():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    try:
        # Drop and recreate with correct schema (INTEGER ids)
        await conn.execute("DROP TABLE IF EXISTS refresh_tokens")
        await conn.execute("""
            CREATE TABLE refresh_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                token VARCHAR(500) UNIQUE NOT NULL,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                revoked_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await conn.execute("CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id)")
        print("refresh_tokens table fixed with INTEGER id and user_id")
    finally:
        await conn.close()

asyncio.run(fix_refresh_tokens())
