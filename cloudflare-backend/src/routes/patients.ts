import { Hono } from 'hono';
import { verify } from 'hono/jwt';

const app = new Hono();

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

// GET /patients
app.get('/', authMiddleware, async (c) => {
  try {
    const search = c.req.query('search');
    let query = `
      SELECT
        p.id, p.user_id, p.first_name, p.last_name, p.date_of_birth, p.gender,
        p.phone, p.address, p.city, p.state, p.pincode, p.blood_group,
        u.email
      FROM patients p
      LEFT JOIN users u ON p.user_id = u.id
      WHERE 1 = 1
    `;
    const params: string[] = [];

    if (search) {
      query += ' AND (LOWER(p.first_name) LIKE ? OR LOWER(p.last_name) LIKE ? OR LOWER(p.id) LIKE ?)';
      const pattern = `%${search.toLowerCase()}%`;
      params.push(pattern, pattern, pattern);
    }

    query += ' ORDER BY p.first_name ASC, p.last_name ASC';
    const results = await c.env.DB.prepare(query).bind(...params).all();
    return c.json({ patients: results.results || [] });
  } catch (error) {
    console.error('Error fetching patients:', error);
    return c.json({ patients: [] });
  }
});

// GET /patients/:id
app.get('/:id', authMiddleware, async (c) => {
  try {
    const id = c.req.param('id');
    const patient = await c.env.DB.prepare(`
      SELECT
        p.id, p.user_id, p.first_name, p.last_name, p.date_of_birth, p.gender,
        p.phone, p.address, p.city, p.state, p.pincode, p.blood_group,
        p.emergency_contact_name, p.emergency_contact_phone,
        u.email
      FROM patients p
      LEFT JOIN users u ON p.user_id = u.id
      WHERE p.id = ?
    `).bind(id).first();

    if (!patient) {
      return c.json({ error: 'Patient not found' }, 404);
    }

    return c.json({ patient });
  } catch (error) {
    console.error('Error fetching patient:', error);
    return c.json({ error: 'Failed to fetch patient' }, 500);
  }
});

export default app;
