import asyncio
import asyncpg
from datetime import datetime, timedelta
import random
import json

async def seed_all_features():
    conn = await asyncpg.connect('postgresql://postgres:123@localhost:5432/healthcare_db')
    
    try:
        print("\n" + "="*60)
        print("  SEEDING ALL FEATURES WITH SAMPLE DATA")
        print("="*60 + "\n")
        
        # Get existing IDs
        patient_ids = [r['id'] for r in await conn.fetch("SELECT id FROM patients")]
        doctor_ids = [r['id'] for r in await conn.fetch("SELECT id FROM doctors")]
        user_ids = [r['id'] for r in await conn.fetch("SELECT id FROM users WHERE role = 'PATIENT'")]
        
        if not patient_ids or not doctor_ids:
            print("⚠ Need patients and doctors first. Please run basic seed first.")
            return
        
        # 1. APPOINTMENTS (15 total - add 10 more)
        print("📅 Seeding Appointments...")
        statuses = ['booked', 'confirmed', 'completed', 'cancelled']
        reasons = ['Routine Checkup', 'Follow-up', 'Consultation', 'Emergency', 
                   'Vaccination', 'Lab Results', 'Prescription Refill', 'Health Screening']
        
        for i in range(10):
            days_offset = random.randint(-30, 60)
            apt_date = (datetime.now() + timedelta(days=days_offset)).date()
            apt_time = datetime.strptime(f"{random.randint(9, 16)}:{random.choice(['00', '30'])}:00", "%H:%M:%S").time()
            
            await conn.execute("""
                INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, status)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT DO NOTHING
            """, random.choice(patient_ids), random.choice(doctor_ids), apt_date, apt_time, 
                random.choice(reasons), random.choice(statuses))
        
        print("✓ Added 10 appointments")
        
        # 2. PRESCRIPTIONS (10 total)
        print("\n💊 Seeding Prescriptions...")
        medications = [
            ('Amoxicillin 500mg', '1 capsule', 'Three times daily', '7 days', 'Take with food'),
            ('Ibuprofen 400mg', '1 tablet', 'Twice daily', '5 days', 'After meals'),
            ('Metformin 500mg', '1 tablet', 'Twice daily', '30 days', 'With breakfast and dinner'),
            ('Atorvastatin 10mg', '1 tablet', 'Once daily', '30 days', 'Before bed'),
            ('Omeprazole 20mg', '1 capsule', 'Once daily', '14 days', 'Before breakfast'),
            ('Cetirizine 10mg', '1 tablet', 'Once daily', '7 days', 'At bedtime'),
            ('Azithromycin 250mg', '1 tablet', 'Once daily', '5 days', 'Empty stomach'),
            ('Paracetamol 650mg', '1 tablet', 'As needed', '5 days', 'Max 4 times daily'),
            ('Losartan 50mg', '1 tablet', 'Once daily', '30 days', 'Morning'),
            ('Aspirin 75mg', '1 tablet', 'Once daily', '30 days', 'After breakfast'),
        ]
        
        for i, (med_name, dosage, frequency, duration, instructions) in enumerate(medications):
            prescribed_date = (datetime.now() - timedelta(days=random.randint(1, 60))).date()
            
            await conn.execute("""
                INSERT INTO prescriptions (
                    patient_id, doctor_id, medication_name, dosage, frequency, 
                    duration, instructions, prescribed_date, is_active, is_signed
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, true)
                ON CONFLICT DO NOTHING
            """, random.choice(patient_ids), random.choice(doctor_ids), med_name, 
                 dosage, frequency, duration, instructions, prescribed_date, 
                 random.choice([True, False]))
        
        print("✓ Added 10 prescriptions")
        
        # 3. MEDICAL RECORDS (10)
        print("\n📋 Seeding Medical Records...")
        diagnoses = ['Hypertension', 'Type 2 Diabetes', 'Asthma', 'Allergic Rhinitis',
                     'GERD', 'Migraine', 'Osteoarthritis', 'Anxiety Disorder', 
                     'Common Cold', 'Urinary Tract Infection']
        treatments = ['Medication', 'Lifestyle modification', 'Physical therapy', 
                      'Dietary changes', 'Rest and hydration', 'Follow-up in 2 weeks']
        
        for i, diagnosis in enumerate(diagnoses):
            record_date = (datetime.now() - timedelta(days=random.randint(1, 180))).date()
            
            await conn.execute("""
                INSERT INTO medical_records (
                    patient_id, doctor_id, visit_date, diagnosis, 
                    treatment, notes, blood_pressure, temperature, weight
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT DO NOTHING
            """, random.choice(patient_ids), random.choice(doctor_ids), record_date,
                 diagnosis, random.choice(treatments),
                 f'Patient presented with symptoms. {diagnosis} diagnosed. {random.choice(treatments)} prescribed.',
                 f'{random.randint(110, 140)}/{random.randint(70, 90)}',
                 round(random.uniform(97.5, 99.5), 1),
                 random.randint(50, 90))
        
        print("✓ Added 10 medical records")
        
        # 4. REPORTS (10)
        print("\n📊 Seeding Reports...")
        report_types = ['Blood Test', 'X-Ray', 'MRI Scan', 'CT Scan', 'Ultrasound',
                        'ECG', 'Lipid Profile', 'Thyroid Test', 'Kidney Function', 'Liver Function']
        
        for i, report_type in enumerate(report_types):
            report_date = (datetime.now() - timedelta(days=random.randint(1, 120))).date()
            
            await conn.execute("""
                INSERT INTO reports (
                    patient_id, doctor_id, report_type, report_date,
                    findings, file_url, test_name
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT DO NOTHING
            """, random.choice(patient_ids), random.choice(doctor_ids),
                 report_type, report_date,
                 f'{report_type} - Results within normal range. No abnormalities detected.',
                 f'/reports/patient_{random.choice(patient_ids)}_{report_type.lower().replace(" ", "_")}.pdf',
                 report_type)
        
        print("✓ Added 10 reports")
        
        # 5. DIGITAL SIGNATURES (10)
        print("\n✍️ Seeding Digital Signatures...")
        for doctor_id in random.sample(doctor_ids, min(10, len(doctor_ids))):
            await conn.execute("""
                INSERT INTO digital_signatures (
                    doctor_id, signature_image_path, signature_pin_hash, is_active
                )
                VALUES ($1, $2, $3, true)
                ON CONFLICT (doctor_id) DO NOTHING
            """, doctor_id, 
                 f'/signatures/doctor_{doctor_id}_signature.png',
                 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztP.JqJjZKW6')  # Hash of "1234"
        
        print("✓ Added digital signatures for 10 doctors")
        
        # 6. NOTIFICATIONS (15)
        print("\n🔔 Seeding Notifications...")
        notification_types = ['appointment', 'prescription', 'test', 'reminder', 'general']
        priorities = ['low', 'normal', 'high', 'urgent']
        
        for i in range(15):
            await conn.execute("""
                INSERT INTO notifications (
                    user_id, notification_type, title, message, priority, 
                    is_read, send_via
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT DO NOTHING
            """, random.choice(user_ids),
                 random.choice(notification_types),
                 f'{random.choice(notification_types).title()} Notification',
                 f'You have a new {random.choice(notification_types)} update',
                 random.choice(priorities),
                 random.choice([True, False]),
                 random.choice(['email', 'sms', 'push']))
        
        print("\n✓ Added 15 notifications")
        
        # FINAL SUMMARY
        print("\n" + "="*60)
        print("  SEEDING COMPLETE - FINAL COUNTS")
        print("="*60 + "\n")
        
        tables = [
            'users', 'patients', 'doctors', 'appointments', 'prescriptions',
            'medical_records', 'reports', 'digital_signatures', 'notifications'
        ]
        
        for table in tables:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                print(f"  {table:25} : {count:4} records")
            except:
                print(f"  {table:25} : Table not found")
        
        print("\n" + "="*60)
        print("  ✅ ALL AVAILABLE FEATURES SEEDED SUCCESSFULLY!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(seed_all_features())
