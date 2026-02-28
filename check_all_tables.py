import asyncio
import asyncpg

async def check_table_structure():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        tables = ['medical_records', 'reports', 'bills', 'templates', 'favorites', 
                  'digital_signatures', 'test_orders', 'reminders', 'notifications']
        
        for table in tables:
            print(f"\n=== {table.upper()} TABLE ===")
            try:
                result = await conn.fetch(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                
                if result:
                    for row in result:
                        print(f"  {row['column_name']:30} {row['data_type']}")
                else:
                    print(f"  ⚠ Table not found or has no columns")
            except Exception as e:
                print(f"  ❌ Error: {e}")
            
    finally:
        await conn.close()

asyncio.run(check_table_structure())
