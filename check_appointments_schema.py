import asyncpg
import asyncio

async def main():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    cols = await conn.fetch("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'appointments'
        ORDER BY ordinal_position
    """)
    
    print("\n" + "="*60)
    print("  APPOINTMENTS TABLE COLUMNS")
    print("="*60)
    for col in cols:
        print(f"  {col['column_name']:30} {col['data_type']:20} {'NULL' if col['is_nullable']=='YES' else 'NOT NULL'}")
    
    await conn.close()

asyncio.run(main())
