import asyncpg
import asyncio

async def fix_staff_role():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    try:
        await conn.execute("UPDATE users SET role = 'ADMIN' WHERE role = 'STAFF'")
        print("Updated STAFF role to ADMIN")
    finally:
        await conn.close()

asyncio.run(fix_staff_role())
