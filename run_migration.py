import asyncpg
import asyncio

async def run_migration():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        print("Running migration: fix_users_schema.sql")
        
        # Read migration file
        with open('backend/migrations/fix_users_schema.sql', 'r') as f:
            sql = f.read()
        
        # Execute migration
        await conn.execute(sql)
        
        print("✓ Migration completed successfully!")
        
        # Verify columns now exist
        columns = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)
        
        print("\nColumns in users table:")
        for col in columns:
            print(f"  - {col['column_name']}")
            
    except Exception as e:
        print(f"✗ Migration failed: {e}")
    finally:
        await conn.close()

asyncio.run(run_migration())
