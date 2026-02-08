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

async function createMissingPatientProfiles() {
  const client = await pool.connect();
  
  try {
    // Find all users with role 'patient' who don't have patient records
    const result = await client.query(`
      SELECT u.id, u.email 
      FROM users u 
      LEFT JOIN patients p ON u.id = p.user_id 
      WHERE u.role = 'patient' AND p.id IS NULL
    `);

    console.log(`Found ${result.rows.length} patients without profiles`);

    for (const user of result.rows) {
      try {
        // Extract name from email or use default
        const emailName = user.email.split('@')[0];
        const firstName = emailName.charAt(0).toUpperCase() + emailName.slice(1);
        
        await client.query(
          `INSERT INTO patients (user_id, first_name, last_name, phone) 
           VALUES ($1, $2, $3, $4)`,
          [user.id, firstName, 'User', '555-0000']
        );
        
        console.log(`✅ Created patient profile for ${user.email}`);
      } catch (error) {
        console.error(`❌ Error creating profile for ${user.email}:`, error.message);
      }
    }

    console.log('\n✅ All patient profiles created!');
  } catch (error) {
    console.error('Error:', error);
  } finally {
    client.release();
    await pool.end();
  }
}

createMissingPatientProfiles();
