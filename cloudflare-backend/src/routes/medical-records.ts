import { Hono } from 'hono';
import { verify } from 'hono/jwt';

const app = new Hono();

// Auth middleware
const authMiddleware = async (c, next) => {
  try {
    const authHeader = c.req.header('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return c.json({ error: 'Unauthorized' }, 401);
    }
    const token = authHeader.substring(7);
    const payload = await verify(token, c.env.JWT_SECRET);
    c.set('user', payload);
    await next();
  } catch (error) {
    return c.json({ error: 'Invalid token' }, 401);
  }
};

// Get all medical records for current patient
app.get('/', authMiddleware, async (c) => {
  try {
    const user = c.get('user');
    
    // Get patient ID from user
    const patientResult = await c.env.DB.prepare(
      'SELECT id FROM patients WHERE user_id = ?'
    ).bind(user.sub).first();

    let records;
    
    if (patientResult) {
      // Patient: get their records
      records = await c.env.DB.prepare(`
        SELECT 
          mr.id, mr.record_type, mr.title, mr.description, mr.file_url,
          mr.test_date, mr.result_summary, mr.created_at,
          d.first_name as doctor_first_name, d.last_name as doctor_last_name, d.specialization,
          a.appointment_date, a.reason as appointment_reason
        FROM medical_records mr
        LEFT JOIN doctors d ON mr.doctor_id = d.id
        LEFT JOIN appointments a ON mr.appointment_id = a.id
        WHERE mr.patient_id = ?
        ORDER BY mr.test_date DESC
      `).bind(patientResult.id).all();
    } else {
      // Doctor: get records they created
      const doctorResult = await c.env.DB.prepare(
        'SELECT id FROM doctors WHERE user_id = ?'
      ).bind(user.sub).first();
      
      if (doctorResult) {
        records = await c.env.DB.prepare(`
          SELECT 
            mr.id, mr.record_type, mr.title, mr.description, mr.file_url,
            mr.test_date, mr.result_summary, mr.created_at,
            pt.first_name as patient_first_name, pt.last_name as patient_last_name,
            a.appointment_date, a.reason as appointment_reason
          FROM medical_records mr
          JOIN patients pt ON mr.patient_id = pt.id
          LEFT JOIN appointments a ON mr.appointment_id = a.id
          WHERE mr.doctor_id = ?
          ORDER BY mr.test_date DESC
        `).bind(doctorResult.id).all();
      } else {
        // Admin: get all records
        records = await c.env.DB.prepare(`
          SELECT 
            mr.id, mr.record_type, mr.title, mr.description, mr.file_url,
            mr.test_date, mr.result_summary, mr.created_at,
            pt.first_name as patient_first_name, pt.last_name as patient_last_name,
            d.first_name as doctor_first_name, d.last_name as doctor_last_name,
            a.appointment_date
          FROM medical_records mr
          JOIN patients pt ON mr.patient_id = pt.id
          LEFT JOIN doctors d ON mr.doctor_id = d.id
          LEFT JOIN appointments a ON mr.appointment_id = a.id
          ORDER BY mr.test_date DESC
        `).all();
      }
    }

    return c.json({ records: records?.results || [] });
  } catch (error) {
    console.error('Error fetching medical records:', error);
    return c.json({ error: 'Failed to fetch medical records' }, 500);
  }
});

// Get single record
app.get('/:id', authMiddleware, async (c) => {
  try {
    const id = c.req.param('id');
    
    const record = await c.env.DB.prepare(`
      SELECT 
        mr.id, mr.record_type, mr.title, mr.description, mr.file_url,
        mr.test_date, mr.result_summary, mr.created_at,
        pt.first_name as patient_first_name, pt.last_name as patient_last_name,
        d.first_name as doctor_first_name, d.last_name as doctor_last_name, d.specialization,
        a.appointment_date, a.reason as appointment_reason
      FROM medical_records mr
      JOIN patients pt ON mr.patient_id = pt.id
      LEFT JOIN doctors d ON mr.doctor_id = d.id
      LEFT JOIN appointments a ON mr.appointment_id = a.id
      WHERE mr.id = ?
    `).bind(id).first();

    if (!record) {
      return c.json({ error: 'Record not found' }, 404);
    }

    return c.json({ record });
  } catch (error) {
    console.error('Error fetching medical record:', error);
    return c.json({ error: 'Failed to fetch medical record' }, 500);
  }
});

export default app;
