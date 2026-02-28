import asyncpg
import asyncio

async def check_constraint():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost/healthcare_db')
    
    # Check the priority check constraint
    result = await conn.fetchrow("""
        SELECT pg_get_constraintdef(oid) as definition
        FROM pg_constraint
        WHERE conname = 'notifications_priority_check'
    """)
    
    if result:
        print("Priority constraint definition:")
        print(result['definition'])
    else:
        print("No constraint found")
    
    # Also check the actual column definition
    column_info = await conn.fetchrow("""
        SELECT column_name, data_type, column_default, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'notifications' AND column_name = 'priority'
    """)
    
    print("\nPriority column info:")
    print(column_info)
    
    await conn.close()

asyncio.run(check_constraint())
