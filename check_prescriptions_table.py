import asyncio
import asyncpg

async def check_table():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        result = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'prescriptions'
            ORDER BY ordinal_position
        """)
        
        print("=== Prescriptions Table Columns ===\n")
        for row in result:
            print(f"  {row['column_name']:30} {row['data_type']}")
            
    finally:
        await conn.close()

asyncio.run(check_table())
