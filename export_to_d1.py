"""
Export data from PostgreSQL to D1-compatible SQL format
"""
import asyncio
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database connection
DATABASE_URL = "postgresql+asyncpg://postgres:123@localhost/healthcare_db"

async def export_table_data(session: AsyncSession, table_name: str, output_file):
    """Export data from a table to SQL INSERT statements"""
    print(f"Exporting {table_name}...")
    
    # Get all data from table
    result = await session.execute(text(f"SELECT * FROM {table_name}"))
    rows = result.fetchall()
    columns = result.keys()
    
    if not rows:
        print(f"  No data in {table_name}")
        return
    
    output_file.write(f"\n-- {table_name} ({len(rows)} rows)\n")
    
    for row in rows:
        values = []
        for i, col in enumerate(columns):
            val = row[i]
            if val is None:
                values.append('NULL')
            elif isinstance(val, str):
                # Escape single quotes
                escaped = val.replace("'", "''")
                values.append(f"'{escaped}'")
            elif isinstance(val, (datetime,)):
                values.append(f"'{val.isoformat()}'")
            elif isinstance(val, bool):
                values.append('1' if val else '0')
            elif isinstance(val, (int, float)):
                values.append(str(val))
            else:
                values.append(f"'{str(val)}'")
        
        cols_str = ', '.join(columns)
        vals_str = ', '.join(values)
        output_file.write(f"INSERT OR IGNORE INTO {table_name} ({cols_str}) VALUES ({vals_str});\n")
    
    print(f"  Exported {len(rows)} rows from {table_name}")

async def main():
    """Main export function"""
    print("Starting PostgreSQL to D1 export...")
    
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Tables to export (in order of dependencies)
    tables = [
        'users',
        'patients',
        'doctors',
        'doctor_specializations',
        'appointments',
        'prescriptions',
        'prescription_medications',
        'medical_records',
        'test_reports',
        'bills',
        'payments',
        'notifications',
        'reviews',
        'doctor_availability',
    ]
    
    try:
        async with async_session() as session:
            with open('cloudflare-backend/d1-data-export.sql', 'w', encoding='utf-8') as f:
                f.write("-- Data export from PostgreSQL to D1\n")
                f.write(f"-- Generated at: {datetime.now().isoformat()}\n")
                f.write("-- WARNING: This will insert/update data in D1 database\n\n")
                
                for table in tables:
                    try:
                        await export_table_data(session, table, f)
                    except Exception as e:
                        print(f"  Error exporting {table}: {e}")
                        continue
        
        print("\n✅ Export completed successfully!")
        print("📁 Output file: cloudflare-backend/d1-data-export.sql")
        print("\nTo import to D1, run:")
        print("  cd cloudflare-backend")
        print("  wrangler d1 execute friendlyhealthy-db --remote --file=d1-data-export.sql")
        
    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
