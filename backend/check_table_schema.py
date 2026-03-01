import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text


async def check_table_schema():
    db = AsyncSessionLocal()
    
    # Check medical_records columns
    result = await db.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'medical_records'
        ORDER BY ordinal_position;
    """))
    
    print("\n=== medical_records table columns ===")
    for row in result:
        print(f"{row[0]}: {row[1]}")
    
    # Check prescriptions columns
    result2 = await db.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'prescriptions'
        ORDER BY ordinal_position;
    """))
    
    print("\n=== prescriptions table columns ===")
    for row in result2:
        print(f"{row[0]}: {row[1]}")
    
    await db.close()


if __name__ == "__main__":
    asyncio.run(check_table_schema())
