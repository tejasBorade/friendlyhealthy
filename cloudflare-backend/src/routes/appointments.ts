import { Hono } from 'hono';
import { jwtVerify } from 'jose';

const appointments = new Hono();

// Helper: Verify JWT and get user
async function verifyToken(token: string, secret: string) {
  try {
    const encoder = new TextEncoder();
    const { payload } = await jwtVerify(token, encoder.encode(secret));
    return payload;
  } catch (error) {
    return null;
  }
}

// GET /appointments
appointments.get('/', async (c) => {
  try {
    const patientId = c.req.query('patientId');
    const doctorId = c.req.query('doctorId');

    let query = `
      SELECT
        a.id,
        a.appointment_number,
        a.patient_id,
        a.doctor_id,
        a.clinic_id,
        a.appointment_date,
        a.appointment_time,
        a.reason_for_visit,
        a.symptoms,
        a.doctor_notes,
        a.status,
        a.created_at,
        p.first_name AS patient_first_name,
        p.last_name AS patient_last_name,
        d.first_name AS doctor_first_name,
        d.last_name AS doctor_last_name,
        d.qualification
      FROM appointments a
      LEFT JOIN patients p ON a.patient_id = p.id
      LEFT JOIN doctors d ON a.doctor_id = d.id
      WHERE a.is_deleted = 0
    `;
    const params: string[] = [];

    if (patientId) {
      query += ' AND a.patient_id = ?';
      params.push(patientId);
    }
    if (doctorId) {
      query += ' AND a.doctor_id = ?';
      params.push(doctorId);
    }

    query += ' ORDER BY a.appointment_date DESC, a.appointment_time DESC LIMIT 200';

    const results = await c.env.DB.prepare(query).bind(...params).all();

    return c.json({ appointments: results.results || [] });
  } catch (error) {
    console.error('Error fetching appointments:', error);
    return c.json({ appointments: [], error: String(error) });
  }
});

// POST /appointments
appointments.post('/', async (c) => {
  try {
    // Get and verify token
    const authHeader = c.req.header('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return c.json({ error: 'Missing or invalid authorization header' }, 401);
    }

    const token = authHeader.substring(7);
    const payload = await verifyToken(token, c.env.JWT_SECRET);
    if (!payload || !payload.sub) {
      return c.json({ error: 'Invalid token' }, 401);
    }

    const userId = payload.sub as string;

    // Get user to check role
    const user = await c.env.DB.prepare(
      'SELECT id, email, role FROM users WHERE id = ?'
    ).bind(userId).first();

    if (!user) {
      return c.json({ error: 'User not found' }, 401);
    }

    const body = await c.req.json();

    let patientId = body.patient_id ?? body.patientId;
    const doctorId = body.doctor_id ?? body.doctorId;
    const clinicId = body.clinic_id ?? body.clinicId ?? null;
    const appointmentDate = body.appointment_date ?? body.appointmentDate;
    const appointmentTime = body.appointment_time ?? body.appointmentTime;
    const reasonForVisit = body.reason_for_visit ?? body.reasonForVisit ?? body.reason ?? null;

    // If patient is booking their own appointment, derive patient_id from user
    if (user.role === 'patient') {
      const patientRecord = await c.env.DB.prepare(
        'SELECT id FROM patients WHERE user_id = ?'
      ).bind(userId).first();
      
      if (!patientRecord) {
        return c.json({ error: 'Patient profile not found' }, 404);
      }
      
      patientId = patientRecord.id;
    } else if (!patientId && (user.role === 'doctor' || user.role === 'admin')) {
      // Doctor/Admin must provide patient_id
      return c.json(
        {
          error: 'Validation failed',
          message: 'patientId is required when booking for another patient',
        },
        400
      );
    }

    if (!doctorId || !appointmentDate || !appointmentTime) {
      return c.json(
        {
          error: 'Validation failed',
          message: 'doctorId, appointmentDate, and appointmentTime are required',
        },
        400
      );
    }

    const appointmentId = crypto.randomUUID();
    const appointmentNumber = `APT-${new Date().getFullYear()}-${String(Date.now()).slice(-6)}`;

    await c.env.DB.prepare(`
      INSERT INTO appointments (
        id,
        appointment_number,
        patient_id,
        doctor_id,
        clinic_id,
        appointment_date,
        appointment_time,
        reason_for_visit,
        status,
        created_at
      )
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'booked', ?)
    `).bind(
      appointmentId,
      appointmentNumber,
      String(patientId),
      String(doctorId),
      clinicId ? String(clinicId) : null,
      String(appointmentDate),
      String(appointmentTime),
      reasonForVisit ? String(reasonForVisit) : null,
      new Date().toISOString()
    ).run();

    return c.json({ id: appointmentId, message: 'Appointment created' }, 201);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error('Error creating appointment:', message);

    if (message.includes('FOREIGN KEY')) {
      return c.json(
        {
          error: 'Validation failed',
          message: 'Invalid patient ID or doctor ID',
        },
        400
      );
    }

    return c.json({ error: 'Failed to create appointment' }, 500);
  }
});

// PATCH /appointments/:id
appointments.patch('/:id', async (c) => {
  try {
    const id = c.req.param('id');
    const body = await c.req.json();
    const status = body.status;

    if (!['booked', 'confirmed', 'completed', 'cancelled', 'rejected', 'no-show'].includes(status)) {
      return c.json({ error: 'Invalid status' }, 400);
    }

    const result = await c.env.DB.prepare(`
      UPDATE appointments
      SET status = ?, status_updated_at = datetime('now'), updated_at = datetime('now')
      WHERE id = ? AND is_deleted = 0
    `).bind(status, id).run();

    if (!result.success) {
      return c.json({ error: 'Failed to update appointment' }, 500);
    }

    return c.json({ message: 'Appointment updated' });
  } catch (error) {
    console.error('Error updating appointment:', error);
    return c.json({ error: 'Failed to update appointment' }, 500);
  }
});

// DELETE /appointments/:id
appointments.delete('/:id', async (c) => {
  try {
    const id = c.req.param('id');

    const result = await c.env.DB.prepare(`
      UPDATE appointments
      SET status = 'cancelled', cancelled_at = datetime('now'), updated_at = datetime('now')
      WHERE id = ? AND is_deleted = 0
    `).bind(id).run();

    if (!result.success) {
      return c.json({ error: 'Failed to cancel appointment' }, 500);
    }

    return c.json({ message: 'Appointment cancelled' });
  } catch (error) {
    console.error('Error cancelling appointment:', error);
    return c.json({ error: 'Failed to cancel appointment' }, 500);
  }
});

export default appointments;
