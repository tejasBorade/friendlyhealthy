"""
Script to create or reset doctor user account.
"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password

async def create_doctor_user():
    """Create or update doctor user."""
    async with AsyncSessionLocal() as db:
        # Check if doctor user exists
        result = await db.execute(
            select(User).where(User.email == "doctor@test.com")
        )
        doctor = result.scalar_one_or_none()
        
        if doctor:
            print(f"Doctor user found (ID: {doctor.id})")
            # Update password
            doctor.password_hash = hash_password("Test@123")
            doctor.role = UserRole.DOCTOR
            doctor.is_active = True
            print("Password reset to: Test@123")
        else:
            print("Doctor user not found, creating new...")
            doctor = User(
                email="doctor@test.com",
                password_hash=hash_password("Test@123"),
                role=UserRole.DOCTOR,
                is_active=True,
                is_verified=True
            )
            db.add(doctor)
            print("Doctor user created")
        
        await db.commit()
        await db.refresh(doctor)
        
        print(f"\nDoctor account ready:")
        print(f"   Email: doctor@test.com")
        print(f"   Password: Test@123")
        print(f"   Role: {doctor.role}")
        print(f"   ID: {doctor.id}")
        
        return doctor

if __name__ == "__main__":
    print("Creating/verifying doctor user...\n")
    asyncio.run(create_doctor_user())
    print("\nDone!")
