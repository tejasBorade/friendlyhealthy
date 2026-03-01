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
      let patientQuery = `
        SELECT 
          p.id, p.consultation_id, p.patient_id, p.doctor_id, 
          p.notes, p.medication_name, p.dosage, 
          p.frequency, p.duration, p.instructions, p.prescription_date,
          p.created_at,
          d.first_name as doctor_first_name, d.last_name as doctor_last_name,
          d.qualification
        FROM prescriptions p
        JOIN doctors d ON p.doctor_id = d.id
        WHERE p.patient_id = ?
      `;
      
      const params = [patientResult.id];
      if (queryAppointmentId) {
        patientQuery += ' AND p.consultation_id = ?';
        params.push(queryAppointmentId);
      }
      patientQuery += ' ORDER BY p.prescription_date DESC, p.created_at DESC';
      prescriptions = await c.env.DB.prepare(patientQuery).bind(...params).all();
    } else {
      // Doctor: get prescriptions they wrote
      const doctorResult = await c.env.DB.prepare(
        'SELECT id FROM doctors WHERE user_id = ?'
      ).bind(user.sub).first();
      
      if (doctorResult) {
        let doctorQuery = `
          SELECT 
            p.id, p.consultation_id, p.patient_id, p.doctor_id,
            p.notes, p.medication_name, p.dosage,
            p.frequency, p.duration, p.instructions, p.prescription_date,
            p.created_at,
            pt.first_name as patient_first_name, pt.last_name as patient_last_name
          FROM prescriptions p
          JOIN patients pt ON p.patient_id = pt.id
          WHERE p.doctor_id = ?
        `;
        const doctorParams = [doctorResult.id];
        if (queryPatientId) {
          doctorQuery += ' AND p.patient_id = ?';
          doctorParams.push(queryPatientId);
        }
        if (queryAppointmentId) {
          doctorQuery += ' AND p.consultation_id = ?';
          doctorParams.push(queryAppointmentId);
        }
        doctorQuery += ' ORDER BY p.prescription_date DESC, p.created_at DESC';
        prescriptions = await c.env.DB.prepare(doctorQuery).bind(...doctorParams).all();
      } else {
        // Admin: get all prescriptions
        let adminQuery = `
          SELECT 
            p.id, p.consultation_id, p.patient_id, p.doctor_id,
            p.notes, p.medication_name, p.dosage,
            p.frequency, p.duration, p.instructions, p.prescription_date,
            p.created_at,
            pt.first_name as patient_first_name, pt.last_name as patient_last_name,
            d.first_name as doctor_first_name, d.last_name as doctor_last_name
          FROM prescriptions p
          JOIN patients pt ON p.patient_id = pt.id
          JOIN doctors d ON p.doctor_id = d.id
          WHERE 1 = 1
        `;
        const adminParams: string[] = [];
        if (queryPatientId) {
          adminQuery += ' AND p.patient_id = ?';
          adminParams.push(queryPatientId);
        }
        if (queryAppointmentId) {
          adminQuery += ' AND p.consultation_id = ?';
          adminParams.push(queryAppointmentId);
        }
        adminQuery += ' ORDER BY p.prescription_date DESC, p.created_at DESC';
        prescriptions = await c.env.DB.prepare(adminQuery).bind(...adminParams).all();
      }
    }

    // Map to frontend expected format
    const mappedPrescriptions = (prescriptions?.results || []).map((p: any) => ({
      id: p.id,
      patient_id: p.patient_id,
      doctor_id: p.doctor_id,
      appointment_id: p.consultation_id,
      consultation_id: p.consultation_id,
      medication_name: p.medication_name,
      dosage: p.dosage,
      frequency: p.frequency,
      duration: p.duration,
      instructions: p.instructions,
      prescribed_date: p.prescription_date,
      prescription_date: p.prescription_date,
      created_at: p.created_at,
      // Mapped fields for frontend compatibility
      diagnosis: p.medication_name,
      appointment_date: p.prescription_date,
      notes: p.instructions
    }));

    return c.json({ prescriptions: mappedPrescriptions });
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
    const medicationName = body.medicationName || body.medication_name;
    const dosage = body.dosage;
    const frequency = body.frequency;
    const duration = body.duration;
    const instructions = body.instructions || body.notes || null;

    if (!patientId) {
      return c.json({ error: 'patientId is required' }, 400);
    }

    if (!medicationName) {
      return c.json({ error: 'medicationName is required' }, 400);
    }

    const doctorResult = await c.env.DB.prepare(
      'SELECT id FROM doctors WHERE user_id = ?'
    ).bind(user.sub).first();
    
    if (!doctorResult) {
      return c.json({ error: 'Doctor profile not found' }, 403);
    }

    const doctorId = doctorResult.id;
    const prescribedDate = new Date().toISOString().split('T')[0];

    const prescriptionId = crypto.randomUUID();
    await c.env.DB.prepare(`
      INSERT INTO prescriptions (
        id, appointment_id, patient_id, doctor_id, 
        medication_name, dosage, frequency, duration, instructions,
        prescribed_date, diagnosis, notes, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      prescriptionId,
      appointmentId ? String(appointmentId) : null,
      String(patientId),
      String(doctorId),
      String(medicationName),
      dosage ? String(dosage) : null,
      frequency ? String(frequency) : null,
      duration ? String(duration) : null,
      instructions,
      prescribedDate,
      String(medicationName), // diagnosis maps to medication name
      instructions,
      new Date().toISOString()
    ).run();

    // Return in frontend expected format
    return c.json({ 
      id: prescriptionId,
      patient_id: patientId,
      doctor_id: doctorId,
      appointment_id: appointmentId,
      medication_name: medicationName,
      dosage,
      frequency,
      duration,
      instructions,
      prescribed_date: prescribedDate,
      created_at: new Date().toISOString(),
      // Mapped fields
      diagnosis: medicationName,
      appointment_date: prescribedDate,
      notes: instructions
    }, 201);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error('Error creating prescription:', message);
    return c.json({ error: 'Failed to create prescription' }, 500);
  }
});

// Get prescription by ID
app.get('/:id', authMiddleware, async (c) => {
  try {
    const id = c.req.param('id');
    
    const prescription = await c.env.DB.prepare(`
      SELECT 
        p.id, p.consultation_id, p.patient_id, p.doctor_id,
        p.medication_name, p.dosage, p.frequency, p.duration,
        p.instructions, p.prescription_date, p.notes, p.created_at,
        pt.first_name as patient_first_name, pt.last_name as patient_last_name,
        d.first_name as doctor_first_name, d.last_name as doctor_last_name, d.qualification
      FROM prescriptions p
      JOIN patients pt ON p.patient_id = pt.id
      JOIN doctors d ON p.doctor_id = d.id
      WHERE p.id = ?
    `).bind(id).first();

    if (!prescription) {
      return c.json({ error: 'Prescription not found' }, 404);
    }

    // Map to frontend expected format
    return c.json({ 
      prescription: {
        ...prescription,
        diagnosis: prescription.medication_name,
        appointment_date: prescription.prescribed_date,
        notes: prescription.instructions
      }
    });
  } catch (error) {
    console.error('Error fetching prescription:', error);
    return c.json({ error: 'Failed to fetch prescription' }, 500);
  }
});

export default app;
