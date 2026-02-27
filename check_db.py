import asyncpg
import asyncio

async def check_database():
    try:
        conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
        
        # List all tables
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        print("Tables in healthcare_db:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        if not tables:
            print("  [NO TABLES FOUND - Database is empty!]")
            
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(check_database())
