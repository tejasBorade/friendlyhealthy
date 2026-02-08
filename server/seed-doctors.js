import bcrypt from 'bcryptjs';
import pkg from 'pg';
const { Pool } = pkg;
import dotenv from 'dotenv';

dotenv.config();

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
});

const doctors = [
  { firstName: 'Sarah', lastName: 'Johnson', specialization: 'Cardiology', qualification: 'MD, FACC', phone: '555-0101', email: 'sarah.johnson@healthcare.com', experienceYears: 15, consultationFee: 150 },
  { firstName: 'Michael', lastName: 'Chen', specialization: 'Neurology', qualification: 'MD, PhD', phone: '555-0102', email: 'michael.chen@healthcare.com', experienceYears: 12, consultationFee: 180 },
  { firstName: 'Emily', lastName: 'Williams', specialization: 'Pediatrics', qualification: 'MD, FAAP', phone: '555-0103', email: 'emily.williams@healthcare.com', experienceYears: 10, consultationFee: 120 },
  { firstName: 'David', lastName: 'Brown', specialization: 'Orthopedics', qualification: 'MD, FAAOS', phone: '555-0104', email: 'david.brown@healthcare.com', experienceYears: 18, consultationFee: 160 },
  { firstName: 'Lisa', lastName: 'Martinez', specialization: 'Dermatology', qualification: 'MD, FAAD', phone: '555-0105', email: 'lisa.martinez@healthcare.com', experienceYears: 8, consultationFee: 130 },
  { firstName: 'James', lastName: 'Taylor', specialization: 'Psychiatry', qualification: 'MD, Board Certified', phone: '555-0106', email: 'james.taylor@healthcare.com', experienceYears: 14, consultationFee: 170 },
  { firstName: 'Jennifer', lastName: 'Davis', specialization: 'Obstetrics & Gynecology', qualification: 'MD, FACOG', phone: '555-0107', email: 'jennifer.davis@healthcare.com', experienceYears: 11, consultationFee: 140 },
  { firstName: 'Robert', lastName: 'Anderson', specialization: 'Oncology', qualification: 'MD, FASCO', phone: '555-0108', email: 'robert.anderson@healthcare.com', experienceYears: 20, consultationFee: 200 },
  { firstName: 'Maria', lastName: 'Garcia', specialization: 'Endocrinology', qualification: 'MD, FACE', phone: '555-0109', email: 'maria.garcia@healthcare.com', experienceYears: 9, consultationFee: 145 },
  { firstName: 'William', lastName: 'Miller', specialization: 'Gastroenterology', qualification: 'MD, FACG', phone: '555-0110', email: 'william.miller@healthcare.com', experienceYears: 16, consultationFee: 155 },
  { firstName: 'Patricia', lastName: 'Wilson', specialization: 'Pulmonology', qualification: 'MD, FCCP', phone: '555-0111', email: 'patricia.wilson@healthcare.com', experienceYears: 13, consultationFee: 165 },
  { firstName: 'Richard', lastName: 'Moore', specialization: 'Urology', qualification: 'MD, FACS', phone: '555-0112', email: 'richard.moore@healthcare.com', experienceYears: 17, consultationFee: 150 },
  { firstName: 'Linda', lastName: 'Thomas', specialization: 'Ophthalmology', qualification: 'MD, FACS', phone: '555-0113', email: 'linda.thomas@healthcare.com', experienceYears: 10, consultationFee: 140 },
  { firstName: 'Christopher', lastName: 'Jackson', specialization: 'ENT (Otolaryngology)', qualification: 'MD, FACS', phone: '555-0114', email: 'christopher.jackson@healthcare.com', experienceYears: 12, consultationFee: 135 },
  { firstName: 'Barbara', lastName: 'White', specialization: 'Rheumatology', qualification: 'MD, FACR', phone: '555-0115', email: 'barbara.white@healthcare.com', experienceYears: 14, consultationFee: 150 },
  { firstName: 'Daniel', lastName: 'Harris', specialization: 'Nephrology', qualification: 'MD, FASN', phone: '555-0116', email: 'daniel.harris@healthcare.com', experienceYears: 11, consultationFee: 160 },
  { firstName: 'Susan', lastName: 'Martin', specialization: 'Hematology', qualification: 'MD, FACP', phone: '555-0117', email: 'susan.martin@healthcare.com', experienceYears: 15, consultationFee: 170 },
  { firstName: 'Joseph', lastName: 'Thompson', specialization: 'Infectious Disease', qualification: 'MD, FIDSA', phone: '555-0118', email: 'joseph.thompson@healthcare.com', experienceYears: 19, consultationFee: 175 },
  { firstName: 'Jessica', lastName: 'Lee', specialization: 'Allergy & Immunology', qualification: 'MD, FAAAAI', phone: '555-0119', email: 'jessica.lee@healthcare.com', experienceYears: 7, consultationFee: 125 },
  { firstName: 'Thomas', lastName: 'Robinson', specialization: 'Emergency Medicine', qualification: 'MD, FACEP', phone: '555-0120', email: 'thomas.robinson@healthcare.com', experienceYears: 13, consultationFee: 190 },
];

async function seedDoctors() {
  const client = await pool.connect();
  
  try {
    await client.query('BEGIN');
    
    let successCount = 0;
    let skipCount = 0;
    
    for (const doctor of doctors) {
      try {
        // Check if doctor email already exists
        const existingUser = await client.query(
          'SELECT id FROM users WHERE email = $1',
          [doctor.email]
        );
        
        if (existingUser.rows.length > 0) {
          console.log(`⚠️  Doctor already exists: ${doctor.firstName} ${doctor.lastName}`);
          skipCount++;
          continue;
        }
        
        // Create user account for doctor
        const hashedPassword = await bcrypt.hash('Doctor@123', 10);
        const userResult = await client.query(
          'INSERT INTO users (email, password_hash, role, is_active) VALUES ($1, $2, $3, $4) RETURNING id',
          [doctor.email, hashedPassword, 'doctor', true]
        );
        
        const userId = userResult.rows[0].id;
        
        // Create doctor profile
        await client.query(
          `INSERT INTO doctors (
            user_id, first_name, last_name, specialization, 
            qualification, phone, experience_years, consultation_fee, is_available
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`,
          [
            userId,
            doctor.firstName,
            doctor.lastName,
            doctor.specialization,
            doctor.qualification,
            doctor.phone,
            doctor.experienceYears,
            doctor.consultationFee,
            true
          ]
        );
        
        console.log(`✅ Created: Dr. ${doctor.firstName} ${doctor.lastName} - ${doctor.specialization}`);
        successCount++;
        
      } catch (error) {
        console.error(`❌ Error creating ${doctor.firstName} ${doctor.lastName}:`, error.message);
      }
    }
    
    await client.query('COMMIT');
    
    console.log('\n' + '='.repeat(60));
    console.log(`✅ Successfully created ${successCount} doctors`);
    console.log(`⚠️  Skipped ${skipCount} existing doctors`);
    console.log('='.repeat(60));
    console.log('\nAll doctors have the password: Doctor@123\n');
    
  } catch (error) {
    await client.query('ROLLBACK');
    console.error('Transaction error:', error);
  } finally {
    client.release();
    await pool.end();
  }
}

seedDoctors();
