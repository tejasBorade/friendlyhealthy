"""Fix enum case to match SQLAlchemy uppercase."""
import asyncio
import asyncpg

async def fix():
    conn = await asyncpg.connect(
        user='postgres', 
        password='123', 
        host='localhost', 
        port=5432, 
        database='healthcare_db'
    )
    
    print("Dropping old userrole enum...")
    await conn.execute('DROP TYPE IF EXISTS userrole CASCADE')
    
    print("Creating userrole enum with uppercase values...")
    await conn.execute(
        "CREATE TYPE userrole AS ENUM ('PATIENT', 'DOCTOR', 'ADMIN', 'VERIFICATION_ADMIN', 'COMPLIANCE_ADMIN', 'SUPPORT_ADMIN')"
    )
    
    print("SUCCESS: userrole enum recreated with uppercase values")
    await conn.close()

asyncio.run(fix())
