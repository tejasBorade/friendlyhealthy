import asyncio
import asyncpg

async def check_tables():
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="healthcare_db"
    )
    
    # Check what tables exist
    tables = await conn.fetch("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    print("\n=== TABLES IN DATABASE ===")
    for row in tables:
        print(f"- {row['table_name']}")
    
    # Check prescriptions table structure
    if any(row['table_name'] == 'prescriptions' for row in tables):
        print("\n=== PRESCRIPTIONS TABLE STRUCTURE ===")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'prescriptions'
            ORDER BY ordinal_position
        """)
        for col in columns:
            print(f"{col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
    
    # Check medical_records table structure
    if any(row['table_name'] == 'medical_records' for row in tables):
        print("\n=== MEDICAL_RECORDS TABLE STRUCTURE ===")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'medical_records'
            ORDER BY ordinal_position
        """)
        for col in columns:
            print(f"{col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
    
    # Check if medical_reports table exists
    if any(row['table_name'] == 'medical_reports' for row in tables):
        print("\n=== MEDICAL_REPORTS TABLE STRUCTURE ===")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'medical_reports'
            ORDER BY ordinal_position
        """)
        for col in columns:
            print(f"{col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
    
    # Check if notifications table exists
    if any(row['table_name'] == 'notifications' for row in tables):
        print("\n=== NOTIFICATIONS TABLE STRUCTURE ===")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'notifications'
            ORDER BY ordinal_position
        """)
        for col in columns:
            print(f"{col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_tables())
