import { Hono } from 'hono';

const doctors = new Hono();

// GET /doctors/search
doctors.get('/search', async (c) => {
  const specialization = c.req.query('specialization');
  const city = c.req.query('city');
  
  let query = `
    SELECT d.*, u.email 
    FROM doctors d 
    JOIN users u ON d.user_id = u.id 
    WHERE d.is_available = 1
  `;
  
  const params = [];
  if (specialization) {
    query += ' AND d.specialization = ?';
    params.push(specialization);
  }
  if (city) {
    query += ' AND d.city = ?';
    params.push(city);
  }
  
  const results = await c.env.DB.prepare(query).bind(...params).all();
  
  return c.json(results.results);
});

// GET /doctors/:id
doctors.get('/:id', async (c) => {
  const id = c.req.param('id');
  
  const doctor = await c.env.DB.prepare(
    'SELECT d.*, u.email FROM doctors d JOIN users u ON d.user_id = u.id WHERE d.id = ?'
  ).bind(id).first();
  
  if (!doctor) {
    return c.json({ error: 'Doctor not found' }, 404);
  }
  
  return c.json(doctor);
});

export default doctors;
