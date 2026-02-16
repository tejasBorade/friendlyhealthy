import { Hono } from 'hono';

const appointments = new Hono();

// GET /appointments
appointments.get('/', async (c) => {
  try {
    const results = await c.env.DB.prepare(
      'SELECT * FROM appointments ORDER BY appointment_date DESC LIMIT 20'
    ).all();
    
    return c.json({ appointments: results.results || [] });
  } catch (error) {
    console.error('Error fetching appointments:', error);
    return c.json({ appointments: [] });
  }
});

// POST /appointments
appointments.post('/', async (c) => {
  const body = await c.req.json();
  
  const result = await c.env.DB.prepare(`
    INSERT INTO appointments (id, patient_id, doctor_id, appointment_date, appointment_time, status, created_at)
    VALUES (?, ?, ?, ?, ?, 'pending', ?)
  `).bind(
    crypto.randomUUID(),
    body.patient_id,
    body.doctor_id,
    body.appointment_date,
    body.appointment_time,
    new Date().toISOString()
  ).run();
  
  return c.json({ id: result.meta.last_row_id, message: 'Appointment created' }, 201);
});

export default appointments;
