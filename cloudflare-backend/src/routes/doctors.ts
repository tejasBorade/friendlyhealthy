import { Hono } from 'hono';

const doctors = new Hono();

// GET /doctors - Get all doctors
doctors.get('/', async (c) => {
  try {
    const results = await c.env.DB.prepare(`
      SELECT d.*, u.email 
      FROM doctors d 
      JOIN users u ON d.user_id = u.id 
      WHERE d.is_deleted = 0 AND u.is_deleted = 0
    `).all();
    
    return c.json({ doctors: results.results || [] });
  } catch (error) {
    console.error('Error fetching doctors:', error);
    return c.json({ doctors: [] });
  }
});

// GET /doctors/search
doctors.get('/search', async (c) => {
  const specialization = c.req.query('specialization');
  const city = c.req.query('city');
  
  let query = `
    SELECT DISTINCT d.*, u.email 
    FROM doctors d 
    JOIN users u ON d.user_id = u.id 
  `;
  
  const params = [];
  const conditions = ['d.is_deleted = 0', 'u.is_deleted = 0'];
  
  if (specialization) {
    query += `
      JOIN doctor_specializations ds ON d.id = ds.doctor_id
      JOIN specializations s ON ds.specialization_id = s.id
    `;
    conditions.push('s.name = ?');
    params.push(specialization);
  }
  
  query += ' WHERE ' + conditions.join(' AND ');
  
  if (city) {
    query += ' AND d.clinic_address LIKE ?';
    params.push(`%${city}%`);
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
