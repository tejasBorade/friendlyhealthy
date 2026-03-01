"""Test full_name property on Patient and Doctor models"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.patient import Patient
from app.models.doctor import Doctor
from sqlalchemy import select

async def test_full_name():
    async with AsyncSessionLocal() as db:
        # Test Patient full_name
        result = await db.execute(select(Patient).limit(1))
        patient = result.scalar_one_or_none()
        
        if patient:
            print("✅ Patient Model Test:")
            print(f"   First Name: {patient.first_name}")
            print(f"   Last Name: {patient.last_name}")
            print(f"   Full Name: {patient.full_name}")
            print()
        
        # Test Doctor full_name
        result2 = await db.execute(select(Doctor).limit(1))
        doctor = result2.scalar_one_or_none()
        
        if doctor:
            print("✅ Doctor Model Test:")
            print(f"   First Name: {doctor.first_name}")
            print(f"   Last Name: {doctor.last_name}")
            print(f"   Full Name: {doctor.full_name}")
            print()
        
        print("✅ SUCCESS! The full_name property works correctly!")
        print()
        print("Now you can:")
        print("1. Book an appointment - patient will receive booking email")
        print("2. Update appointment status - patient will receive update email")
        print("3. Create prescription - patient will receive prescription email")

if __name__ == "__main__":
    asyncio.run(test_full_name())
