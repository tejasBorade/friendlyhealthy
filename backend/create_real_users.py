"""
Create Patient and Doctor with Real Email Addresses
Patient: mazaemailghe@gmail.com
Doctor: tejas.jrb@gmail.com
"""
import asyncio
from datetime import date
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.core.security import hash_password
from sqlalchemy import select

async def create_real_users():
    async with AsyncSessionLocal() as db:
        print("\n" + "="*70)
        print("CREATING PATIENT AND DOCTOR WITH REAL EMAIL ADDRESSES")
        print("="*70)
        
        # ===== CREATE PATIENT =====
        patient_email = "mazaemailghe@gmail.com"
        patient_password = "Patient@123"
        
        # Check if patient email already exists
        result = await db.execute(
            select(User).where(User.email == patient_email)
        )
        existing_patient_user = result.scalar_one_or_none()
        
        if existing_patient_user:
            print(f"\n⚠️  Patient user already exists with email: {patient_email}")
            print(f"   User ID: {existing_patient_user.id}")
            
            # Check if patient profile exists
            patient_profile_result = await db.execute(
                select(Patient).where(Patient.user_id == existing_patient_user.id)
            )
            patient_profile = patient_profile_result.scalar_one_or_none()
            
            if patient_profile:
                print(f"   Patient Profile ID: {patient_profile.id}")
                print(f"   Name: {patient_profile.first_name} {patient_profile.last_name}")
            else:
                print("   ⚠️  No patient profile found - creating one...")
                new_patient_profile = Patient(
                    user_id=existing_patient_user.id,
                    first_name="Maza",
                    last_name="Patient",
                    date_of_birth=date(1990, 1, 1),
                    gender="male",
                    phone="9876543210",
                    address="123 Patient Street",
                    city="Mumbai",
                    state="Maharashtra",
                    zip_code="400001",
                    country="India",
                    blood_group="O+"
                )
                db.add(new_patient_profile)
                await db.commit()
                await db.refresh(new_patient_profile)
                print(f"   ✅ Created patient profile ID: {new_patient_profile.id}")
        else:
            # Create new patient user
            print(f"\n✅ Creating new patient user: {patient_email}")
            patient_user = User(
                email=patient_email,
                password_hash=hash_password(patient_password),
                role=UserRole.PATIENT,
                is_active=True,
                is_verified=True
            )
            db.add(patient_user)
            await db.flush()  # Get the user ID
            
            # Create patient profile
            patient_profile = Patient(
                user_id=patient_user.id,
                first_name="Maza",
                last_name="Patient",
                date_of_birth=date(1990, 1, 1),
                gender="male",
                phone="9876543210",
                address="123 Patient Street",
                city="Mumbai",
                state="Maharashtra",
                zip_code="400001",
                country="India",
                blood_group="O+"
            )
            db.add(patient_profile)
            await db.commit()
            await db.refresh(patient_user)
            await db.refresh(patient_profile)
            
            print(f"   User ID: {patient_user.id}")
            print(f"   Patient Profile ID: {patient_profile.id}")
            print(f"   Name: {patient_profile.first_name} {patient_profile.last_name}")
        
        print(f"\n📧 Patient Login Credentials:")
        print(f"   Email: {patient_email}")
        print(f"   Password: {patient_password}")
        
        # ===== CREATE DOCTOR =====
        doctor_email = "tejas.jrb@gmail.com"
        doctor_password = "Doctor@123"
        
        # Check if doctor email already exists
        result = await db.execute(
            select(User).where(User.email == doctor_email)
        )
        existing_doctor_user = result.scalar_one_or_none()
        
        if existing_doctor_user:
            print(f"\n⚠️  Doctor user already exists with email: {doctor_email}")
            print(f"   User ID: {existing_doctor_user.id}")
            
            # Check if doctor profile exists
            doctor_profile_result = await db.execute(
                select(Doctor).where(Doctor.user_id == existing_doctor_user.id)
            )
            doctor_profile = doctor_profile_result.scalar_one_or_none()
            
            if doctor_profile:
                print(f"   Doctor Profile ID: {doctor_profile.id}")
                print(f"   Name: Dr. {doctor_profile.first_name} {doctor_profile.last_name}")
                print(f"   Specialization: {doctor_profile.specialization}")
            else:
                print("   ⚠️  No doctor profile found - creating one...")
                new_doctor_profile = Doctor(
                    user_id=existing_doctor_user.id,
                    first_name="Tejas",
                    last_name="Doctor",
                    specialization="General Physician",
                    qualification="MBBS, MD",
                    experience_years=10,
                    phone="9876543211",
                    consultation_fee=500.00,
                    available_days="Monday,Tuesday,Wednesday,Thursday,Friday",
                    available_hours="09:00-17:00",
                    is_available=True
                )
                db.add(new_doctor_profile)
                await db.commit()
                await db.refresh(new_doctor_profile)
                print(f"   ✅ Created doctor profile ID: {new_doctor_profile.id}")
        else:
            # Create new doctor user
            print(f"\n✅ Creating new doctor user: {doctor_email}")
            doctor_user = User(
                email=doctor_email,
                password_hash=hash_password(doctor_password),
                role=UserRole.DOCTOR,
                is_active=True,
                is_verified=True
            )
            db.add(doctor_user)
            await db.flush()  # Get the user ID
            
            # Create doctor profile
            doctor_profile = Doctor(
                user_id=doctor_user.id,
                first_name="Tejas",
                last_name="Doctor",
                specialization="General Physician",
                qualification="MBBS, MD",
                experience_years=10,
                phone="9876543211",
                consultation_fee=500.00,
                available_days="Monday,Tuesday,Wednesday,Thursday,Friday",
                available_hours="09:00-17:00",
                is_available=True
            )
            db.add(doctor_profile)
            await db.commit()
            await db.refresh(doctor_user)
            await db.refresh(doctor_profile)
            
            print(f"   User ID: {doctor_user.id}")
            print(f"   Doctor Profile ID: {doctor_profile.id}")
            print(f"   Name: Dr. {doctor_profile.first_name} {doctor_profile.last_name}")
            print(f"   Specialization: {doctor_profile.specialization}")
        
        print(f"\n📧 Doctor Login Credentials:")
        print(f"   Email: {doctor_email}")
        print(f"   Password: {doctor_password}")
        
        print("\n" + "="*70)
        print("✅ SUCCESS! ACCOUNTS CREATED/VERIFIED")
        print("="*70)
        print("\n📋 SUMMARY:")
        print(f"\n👤 PATIENT:")
        print(f"   Email: {patient_email}")
        print(f"   Password: {patient_password}")
        print(f"   Will receive email notifications at: {patient_email}")
        
        print(f"\n👨‍⚕️ DOCTOR:")
        print(f"   Email: {doctor_email}")
        print(f"   Password: {doctor_password}")
        print(f"   Will receive email notifications at: {doctor_email}")
        
        print("\n🧪 TEST EMAIL NOTIFICATIONS:")
        print("1. Login as patient (mazaemailghe@gmail.com)")
        print("2. Book appointment with Dr. Tejas")
        print("3. Check your Gmail inbox for booking confirmation")
        print("4. Login as doctor (tejas.jrb@gmail.com)")
        print("5. Change appointment status to 'confirmed'")
        print("6. Patient will receive status update email")
        print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(create_real_users())
