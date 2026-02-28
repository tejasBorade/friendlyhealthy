"""Create or verify admin user"""
import asyncio

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    async with AsyncSessionLocal() as db:
        # Check for admin user
        result = await db.execute(
            select(User).where(
                User.email == "admin@healcare.com",
                User.is_deleted == False
            )
        )
        admin = result.scalar_one_or_none()
        
        if admin:
            print(f"✅ Admin user exists: {admin.email}")
            print(f"   Role: {admin.role}")
            print(f"   Active: {admin.is_active}")
            print(f"   ID: {admin.id}")
            
            # Update password to ensure it's correct
            admin.password_hash = pwd_context.hash("Admin@123")
            await db.commit()
            print("✅ Password reset to: Admin@123")
        else:
            print("❌ No admin user found. Creating new admin user...")
            admin = User(
                email="admin@healcare.com",
                password_hash=pwd_context.hash("Admin@123"),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            await db.commit()
            await db.refresh(admin)
            print(f"✅ Admin user created!")
            print(f"   Email: admin@healcare.com")
            print(f"   Password: Admin@123")
            print(f"   ID: {admin.id}")
        
        # List all admin users
        result = await db.execute(
            select(User).where(User.role == UserRole.ADMIN, User.is_deleted == False)
        )
        admins = result.scalars().all()
        print(f"\n📋 Total admin users: {len(admins)}")
        for a in admins:
            print(f"   - {a.email} (ID: {a.id}, Active: {a.is_active})")

if __name__ == "__main__":
    asyncio.run(create_admin())
