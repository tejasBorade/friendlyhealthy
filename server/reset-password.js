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

async function resetPassword(email, newPassword) {
  try {
    const hashedPassword = await bcrypt.hash(newPassword, 10);
    const result = await pool.query(
      'UPDATE users SET password_hash = $1 WHERE email = $2 RETURNING id, email, role',
      [hashedPassword, email]
    );
    
    if (result.rows.length === 0) {
      console.log(`User not found: ${email}`);
    } else {
      console.log(`Password updated for ${email} (Role: ${result.rows[0].role})`);
    }
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await pool.end();
  }
}

// Reset password for test@example.com
const email = process.argv[2] || 'test@example.com';
const password = process.argv[3] || 'Test@123';

resetPassword(email, password);
