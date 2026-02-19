import { Hono } from 'hono';

const appointments = new Hono();

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
        d.specialization
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
    return c.json({ appointments: [] });
  }
});

// POST /appointments
appointments.post('/', async (c) => {
  try {
    const body = await c.req.json();

    const patientId = body.patient_id ?? body.patientId;
    const doctorId = body.doctor_id ?? body.doctorId;
    const clinicId = body.clinic_id ?? body.clinicId ?? null;
    const appointmentDate = body.appointment_date ?? body.appointmentDate;
    const appointmentTime = body.appointment_time ?? body.appointmentTime;
    const reasonForVisit = body.reason_for_visit ?? body.reasonForVisit ?? body.reason ?? null;

    if (!patientId || !doctorId || !appointmentDate || !appointmentTime) {
      return c.json(
        {
          error: 'Validation failed',
          message: 'patientId, doctorId, appointmentDate, and appointmentTime are required',
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
