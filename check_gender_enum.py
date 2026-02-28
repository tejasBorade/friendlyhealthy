import asyncpg
import asyncio

async def check_gender_enum():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    # Check the gender column type
    gender_type = await conn.fetchrow("""
        SELECT pg_enum.enumlabel
        FROM pg_type
        JOIN pg_enum ON pg_type.oid = pg_enum.enumtypid
        WHERE pg_type.typname = 'gender'
        ORDER BY pg_enum.enumsortorder
    """)
    
    if gender_type:
        print("\nGender ENUM values in database:")
        result = await conn.fetch("""
            SELECT enumlabel
            FROM pg_type
            JOIN pg_enum ON pg_type.oid = pg_enum.enumtypid
            WHERE pg_type.typname = 'gender'
            ORDER BY pg_enum.enumsortorder
        """)
        for row in result:
            print(f"  - {row['enumlabel']}")
    else:
        print("\nNo ENUM type named 'gender' found in database")
        print("Checking actual column type...")
        
        col_info = await conn.fetchrow("""
            SELECT data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = 'patients' AND column_name = 'gender'
        """)
        print(f"Column type: {col_info['data_type']} ({col_info['udt_name']})")
    
    # Check actual values in database
    sample = await conn.fetchrow("SELECT gender FROM patients LIMIT 1")
    if sample:
        print(f"\nSample gender value from database: '{sample['gender']}' (type: {type(sample['gender']).__name__})")
    
    await conn.close()

asyncio.run(check_gender_enum())
