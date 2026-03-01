import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.patient import Patient
from sqlalchemy import select

async def check_patient():
    async with AsyncSessionLocal() as db:
        # Check user
        result = await db.execute(
            select(User).where(User.email == 'mazaemailghe@gmail.com')
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ User not found!")
            return
        
        print(f"✅ User found:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print()
        
        # Check patient profile
        result = await db.execute(
            select(Patient).where(Patient.user_id == user.id)
        )
        patient = result.scalar_one_or_none()
        
        if not patient:
            print("❌ Patient profile NOT FOUND for this user!")
            print("   This is why you're getting the error.")
        else:
            print("✅ Patient profile found:")
            print(f"   Patient ID: {patient.id}")
            print(f"   Name: {patient.first_name} {patient.last_name}")
            print(f"   User ID: {patient.user_id}")

if __name__ == "__main__":
    asyncio.run(check_patient())
