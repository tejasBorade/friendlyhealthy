import asyncpg
import asyncio

async def check_patients_schema():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    try:
        # Get column info
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'patients'
            ORDER BY ordinal_position;
        """)
        
        print("Columns in patients table:")
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"  {col['column_name']:<30} {col['data_type']:<20} {nullable}")
            
    finally:
        await conn.close()

asyncio.run(check_patients_schema())
