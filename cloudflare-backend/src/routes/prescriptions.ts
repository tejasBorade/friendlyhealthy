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
    const queryPatientId = c.req.query('patientId');
    const queryAppointmentId = c.req.query('appointmentId');
    
    // Get patient ID from user
    const patientResult = await c.env.DB.prepare(
      'SELECT id FROM patients WHERE user_id = ?'
    ).bind(user.sub).first();

    let prescriptions;
    
    if (patientResult) {
      // Patient: get their prescriptions
        prescriptions = await c.env.DB.prepare(`
          SELECT 
            p.id, p.appointment_id, p.patient_id, p.doctor_id, p.diagnosis, p.notes, p.created_at,
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
        let doctorQuery = `
          SELECT 
            p.id, p.appointment_id, p.patient_id, p.doctor_id, p.diagnosis, p.notes, p.created_at,
            pt.first_name as patient_first_name, pt.last_name as patient_last_name,
            a.appointment_date
          FROM prescriptions p
          JOIN patients pt ON p.patient_id = pt.id
          JOIN appointments a ON p.appointment_id = a.id
          WHERE p.doctor_id = ?
        `;
        const doctorParams = [doctorResult.id];
        if (queryPatientId) {
          doctorQuery += ' AND p.patient_id = ?';
          doctorParams.push(queryPatientId);
        }
        if (queryAppointmentId) {
          doctorQuery += ' AND p.appointment_id = ?';
          doctorParams.push(queryAppointmentId);
        }
        doctorQuery += ' ORDER BY p.created_at DESC';
        prescriptions = await c.env.DB.prepare(doctorQuery).bind(...doctorParams).all();
      } else {
        // Admin: get all prescriptions
        let adminQuery = `
          SELECT 
            p.id, p.appointment_id, p.patient_id, p.doctor_id, p.diagnosis, p.notes, p.created_at,
            pt.first_name as patient_first_name, pt.last_name as patient_last_name,
            d.first_name as doctor_first_name, d.last_name as doctor_last_name,
            a.appointment_date
          FROM prescriptions p
          JOIN patients pt ON p.patient_id = pt.id
          JOIN doctors d ON p.doctor_id = d.id
          JOIN appointments a ON p.appointment_id = a.id
          WHERE 1 = 1
        `;
        const adminParams: string[] = [];
        if (queryPatientId) {
          adminQuery += ' AND p.patient_id = ?';
          adminParams.push(queryPatientId);
        }
        if (queryAppointmentId) {
          adminQuery += ' AND p.appointment_id = ?';
          adminParams.push(queryAppointmentId);
        }
        adminQuery += ' ORDER BY p.created_at DESC';
        prescriptions = await c.env.DB.prepare(adminQuery).bind(...adminParams).all();
      }
    }

    return c.json({ prescriptions: prescriptions?.results || [] });
  } catch (error) {
    console.error('Error fetching prescriptions:', error);
    return c.json({ error: 'Failed to fetch prescriptions' }, 500);
  }
});

// Create prescription
app.post('/', authMiddleware, async (c) => {
  try {
    const user = c.get('user');
    const body = await c.req.json();

    const patientId = body.patientId ?? body.patient_id;
    const appointmentId = body.appointmentId ?? body.appointment_id;
    const diagnosis = body.diagnosis || 'General consultation';
    const notes = body.notes || body.instructions || null;

    if (!patientId || !appointmentId) {
      return c.json({ error: 'patientId and appointmentId are required' }, 400);
    }

    const doctorResult = await c.env.DB.prepare(
      'SELECT id FROM doctors WHERE user_id = ?'
    ).bind(user.sub).first();
    const doctorId = doctorResult?.id || body.doctorId || body.doctor_id;

    if (!doctorId) {
      return c.json({ error: 'Doctor profile not found' }, 400);
    }

    const prescriptionId = crypto.randomUUID();
    await c.env.DB.prepare(`
      INSERT INTO prescriptions (id, appointment_id, patient_id, doctor_id, diagnosis, notes, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `).bind(
      prescriptionId,
      String(appointmentId),
      String(patientId),
      String(doctorId),
      String(diagnosis),
      notes ? String(notes) : null,
      new Date().toISOString()
    ).run();

    const medicationName = body.medicationName || body.medication_name;
    if (medicationName) {
      await c.env.DB.prepare(`
        INSERT INTO prescription_medications (
          id, prescription_id, medication_name, dosage, frequency, duration, instructions
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
      `).bind(
        crypto.randomUUID(),
        prescriptionId,
        String(medicationName),
        String(body.dosage || ''),
        String(body.frequency || ''),
        String(body.duration || ''),
        body.instructions ? String(body.instructions) : null
      ).run();
    }

    return c.json({ id: prescriptionId, message: 'Prescription created' }, 201);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error('Error creating prescription:', message);
    return c.json({ error: 'Failed to create prescription' }, 500);
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
