import asyncio
import asyncpg

async def check_constraints():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        # Check appointment status constraint
        result = await conn.fetch("""
            SELECT con.conname, 
                   pg_get_constraintdef(con.oid) AS constraint_def
            FROM pg_constraint con
            JOIN pg_class rel ON rel.oid = con.conrelid
            WHERE rel.relname = 'appointments' 
            AND contype = 'c'
        """)
        
        print("=== Appointments Table Constraints ===\n")
        for row in result:
            print(f"{row['conname']}:")
            print(f"  {row['constraint_def']}\n")
            
    finally:
        await conn.close()

asyncio.run(check_constraints())
