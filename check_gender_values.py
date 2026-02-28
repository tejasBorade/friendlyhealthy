import asyncpg
import asyncio

async def main():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    rows = await conn.fetch("SELECT id, gender FROM patients WHERE gender IS NOT NULL LIMIT 5")
    print("\nPatient Gender Values:")
    for row in rows:
        print(f"  ID: {row['id']}, Gender: '{row['gender']}'")
    
    await conn.close()

asyncio.run(main())
