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

// Get all prescriptions for current patient
app.get('/', authMiddleware, async (c) => {
  try {
    const user = c.get('user');
    
    // Get patient ID from user
    const patientResult = await c.env.DB.prepare(
      'SELECT id FROM patients WHERE user_id = ?'
    ).bind(user.sub).first();

    let prescriptions;
    
    if (patientResult) {
      // Patient: get their prescriptions
      prescriptions = await c.env.DB.prepare(`
        SELECT 
          p.id, p.appointment_id, p.diagnosis, p.notes, p.created_at,
          d.first_name as doctor_first_name, d.last_name as doctor_last_name, d.specialization,
          a.appointment_date
        FROM prescriptions p
        JOIN doctors d ON p.doctor_id = d.id
        JOIN appointments a ON p.appointment_id = a.id
        WHERE p.patient_id = ?
        ORDER BY p.created_at DESC
      `).bind(patientResult.id).all();
    } else {
      // Doctor: get prescriptions they wrote
      const doctorResult = await c.env.DB.prepare(
        'SELECT id FROM doctors WHERE user_id = ?'
      ).bind(user.sub).first();
      
      if (doctorResult) {
        prescriptions = await c.env.DB.prepare(`
          SELECT 
            p.id, p.appointment_id, p.diagnosis, p.notes, p.created_at,
            pt.first_name as patient_first_name, pt.last_name as patient_last_name,
            a.appointment_date
          FROM prescriptions p
          JOIN patients pt ON p.patient_id = pt.id
          JOIN appointments a ON p.appointment_id = a.id
          WHERE p.doctor_id = ?
          ORDER BY p.created_at DESC
        `).bind(doctorResult.id).all();
      } else {
        // Admin: get all prescriptions
        prescriptions = await c.env.DB.prepare(`
          SELECT 
            p.id, p.appointment_id, p.diagnosis, p.notes, p.created_at,
            pt.first_name as patient_first_name, pt.last_name as patient_last_name,
            d.first_name as doctor_first_name, d.last_name as doctor_last_name,
            a.appointment_date
          FROM prescriptions p
          JOIN patients pt ON p.patient_id = pt.id
          JOIN doctors d ON p.doctor_id = d.id
          JOIN appointments a ON p.appointment_id = a.id
          ORDER BY p.created_at DESC
        `).all();
      }
    }

    return c.json({ prescriptions: prescriptions?.results || [] });
  } catch (error) {
    console.error('Error fetching prescriptions:', error);
    return c.json({ error: 'Failed to fetch prescriptions' }, 500);
  }
});

// Get prescription with medications
app.get('/:id', authMiddleware, async (c) => {
  try {
    const id = c.req.param('id');
    
    const prescription = await c.env.DB.prepare(`
      SELECT 
        p.id, p.appointment_id, p.diagnosis, p.notes, p.created_at,
        pt.first_name as patient_first_name, pt.last_name as patient_last_name,
        d.first_name as doctor_first_name, d.last_name as doctor_last_name, d.specialization,
        a.appointment_date, a.reason
      FROM prescriptions p
      JOIN patients pt ON p.patient_id = pt.id
      JOIN doctors d ON p.doctor_id = d.id
      JOIN appointments a ON p.appointment_id = a.id
      WHERE p.id = ?
    `).bind(id).first();

    if (!prescription) {
      return c.json({ error: 'Prescription not found' }, 404);
    }

    const medications = await c.env.DB.prepare(`
      SELECT id, medication_name, dosage, frequency, duration, instructions
      FROM prescription_medications
      WHERE prescription_id = ?
    `).bind(id).all();

    return c.json({ 
      prescription: {
        ...prescription,
        medications: medications?.results || []
      }
    });
  } catch (error) {
    console.error('Error fetching prescription:', error);
    return c.json({ error: 'Failed to fetch prescription' }, 500);
  }
});

export default app;
