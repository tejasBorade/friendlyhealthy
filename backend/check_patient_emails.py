"""Check patient email addresses in database"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.patient import Patient
from app.models.user import User
from sqlalchemy import select

async def check_patients():
    async with AsyncSessionLocal() as db:
        # Get all patients with their user information
        result = await db.execute(
            select(Patient, User)
            .join(User, Patient.user_id == User.id)
            .limit(10)
        )
        patients = result.all()
        
        print("\n" + "="*70)
        print("PATIENTS WITH EMAIL ADDRESSES")
        print("="*70)
        
        if not patients:
            print("❌ NO PATIENTS FOUND!")
            print("\nChecking if patients exist without user links...")
            
            # Check patients without joins
            result2 = await db.execute(select(Patient).limit(10))
            all_patients = result2.scalars().all()
            
            print(f"\nTotal patients in database: {len(all_patients)}")
            for p in all_patients:
                print(f"  - Patient ID: {p.id}, Name: {p.first_name} {p.last_name}, User ID: {p.user_id}")
            
            # Check users
            result3 = await db.execute(select(User).where(User.role == 'PATIENT').limit(10))
            patient_users = result3.scalars().all()
            
            print(f"\nTotal users with role=PATIENT: {len(patient_users)}")
            for u in patient_users:
                print(f"  - User ID: {u.id}, Email: {u.email}")
        else:
            for patient, user in patients:
                print(f"\n✅ Patient ID: {patient.id}")
                print(f"   Name: {patient.first_name} {patient.last_name}")
                print(f"   User ID: {user.id}")
                print(f"   Email: {user.email}")
                print(f"   Role: {user.role}")
                print(f"   Active: {user.is_active}")
        
        print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(check_patients())
