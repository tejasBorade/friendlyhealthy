"""Fix database enum type name to match SQLAlchemy expectations."""
import asyncio
import asyncpg
from app.core.config import settings

async def fix_enum_type():
    """Create userrole enum as alias for user_role."""
    # Convert asyncpg URL to sync URL
    db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    # Parse connection details
    # Format: postgresql://user:password@host:port/database
    parts = db_url.replace("postgresql://", "").split("@")
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    host_port = host_db[0].split(":")
    
    user = user_pass[0]
    password = user_pass[1]
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 5432
    database = host_db[1]
    
    print(f"Connecting to database: {host}:{port}/{database}")
    
    conn = await asyncpg.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )
    
    try:
        # Check if user_role enum exists
        result = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pg_type WHERE typname = 'user_role')"
        )
        print(f"user_role enum exists: {result}")
        
        # Check if userrole enum exists
        result2 = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pg_type WHERE typname = 'userrole')"
        )
        print(f"userrole enum exists: {result2}")
        
        if result and not result2:
            # Create userrole as alias (PostgreSQL doesn't support type aliases, so we'll create the type)
            print("\nCreating userrole enum type...")
            await conn.execute(
                "CREATE TYPE userrole AS ENUM ('patient', 'doctor', 'admin', 'verification_admin', 'compliance_admin', 'support_admin')"
            )
            print("SUCCESS: userrole enum created!")
        elif result2:
            print("userrole enum already exists!")
        else:
            print("Neither enum exists, creating both...")
            # Create user_role first
            await conn.execute(
                "CREATE TYPE user_role AS ENUM ('patient', 'doctor', 'admin')"
            )
            print("SUCCESS: user_role enum created!")
            # Create userrole
            await conn.execute(
                "CREATE TYPE userrole AS ENUM ('patient', 'doctor', 'admin', 'verification_admin', 'compliance_admin', 'support_admin')"
            )
            print("SUCCESS: userrole enum created!")
            
    finally:
        await conn.close()

if __name__ == "__main__":
    print("Fixing database enum type...\n")
    asyncio.run(fix_enum_type())
    print("\nDone!")
