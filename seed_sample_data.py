import asyncio
import asyncpg
from datetime import datetime, timedelta
import random

async def seed_sample_data():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        # 1. Create patient profile for user ID 29 (patient@test.com)
        print("\n=== Creating Patient Profile for Test User ===")
        existing = await conn.fetchval("SELECT id FROM patients WHERE user_id = 29")
        if not existing:
            await conn.execute("""
                INSERT INTO patients (user_id, first_name, last_name, date_of_birth, gender, phone, address)
                VALUES (29, 'Test', 'Patient', '1990-01-01', 'male', '9876543210', '123 Test Street, Test City')
            """)
            print("✓ Patient profile created for user ID 29")
        else:
            print("✓ Patient profile already exists")

        # 2. Get doctor IDs
        doctors = await conn.fetch("SELECT id FROM doctors LIMIT 5")
        doctor_ids = [d['id'] for d in doctors]
        
        if not doctor_ids:
            print("⚠ No doctors found. Please add doctors first.")
            return
        
        # 3. Create sample appointments for test patient
        print("\n=== Creating Sample Appointments ===")
        patient_id = await conn.fetchval("SELECT id FROM patients WHERE user_id = 29")
        
        if not patient_id:
            print("⚠ Patient profile not found")
            return
            
        statuses = ['booked', 'confirmed', 'completed']
        reasons = ['Regular Checkup', 'Follow-up Visit', 'Consultation', 'Health Screening']
        
        for i in range(5):
            appointment_date = (datetime.now() + timedelta(days=random.randint(-30, 30))).date()
            appointment_time = datetime.strptime(f"{random.randint(9, 16)}:00:00", "%H:%M:%S").time()
            status = random.choice(statuses)
            reason = random.choice(reasons)
            doctor_id = random.choice(doctor_ids)
            
            await conn.execute("""
                INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, status)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT DO NOTHING
            """, patient_id, doctor_id, appointment_date, appointment_time, reason, status)
        
        print(f"✓ Created 5 sample appointments")
        
        # 4. Create sample prescriptions (simplified)
        print("\n=== Creating Sample Prescriptions ===")
        
        medications = [
            ('Paracetamol 500mg', '1 tablet', 'Twice daily', '5 days', 'After meals'),
            ('Amoxicillin 250mg', '1 capsule', 'Three times daily', '7 days', 'Before meals'),
            ('Ibuprofen 400mg', '1 tablet', 'As needed', '10 days', 'After meals'),
            ('Vitamin D3', '1 tablet', 'Once daily', '30 days', 'Morning'),
            ('Cetirizine 10mg', '1 tablet', 'Once daily', '7 days', 'Bedtime'),
        ]
        
        for i in range(3):
            med_name, dosage, frequency, duration, instructions = random.choice(medications)
            prescribed_date = (datetime.now() - timedelta(days=random.randint(1, 30))).date()
            
            await conn.execute("""
                INSERT INTO prescriptions (
                    patient_id, doctor_id, medication_name, dosage, frequency, 
                    duration, instructions, prescribed_date, is_active, is_signed
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, true, true)
                ON CONFLICT DO NOTHING
            """, patient_id, random.choice(doctor_ids), med_name, dosage, 
                 frequency, duration, instructions, prescribed_date)
        
        print("✓ Created sample prescriptions")
        
        # 5. Show final summary
        print("\n=== FINAL SUMMARY ===")
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        patient_count = await conn.fetchval("SELECT COUNT(*) FROM patients")
        doctor_count = await conn.fetchval("SELECT COUNT(*) FROM doctors")
        appointment_count = await conn.fetchval("SELECT COUNT(*) FROM appointments")
        prescription_count = await conn.fetchval("SELECT COUNT(*) FROM prescriptions")
        
        print(f"Users:         {user_count}")
        print(f"Patients:      {patient_count}")
        print(f"Doctors:       {doctor_count}")
        print(f"Appointments:  {appointment_count}")
        print(f"Prescriptions: {prescription_count}")
        
        print("\n✅ Sample data created successfully!")
        print("\nYou can now login with:")
        print("  Email: patient@test.com")
        print("  Password: Test@123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(seed_sample_data())
