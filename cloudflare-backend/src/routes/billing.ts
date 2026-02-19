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

// Get all bills for current user
app.get('/', authMiddleware, async (c) => {
  try {
    const user = c.get('user');
    
    // Get patient ID from user
    const patientResult = await c.env.DB.prepare(
      'SELECT id FROM patients WHERE user_id = ?'
    ).bind(user.sub).first();

    let bills;
    
    if (patientResult) {
      // Patient: get their bills
      bills = await c.env.DB.prepare(`
        SELECT 
          b.id, b.bill_number, b.subtotal, b.tax_amount, b.discount_amount, b.total_amount, b.payment_status,
          b.payment_method, b.payment_date, b.due_date, b.bill_date, b.notes, b.created_at,
          a.appointment_date,
          d.first_name as doctor_first_name, d.last_name as doctor_last_name
        FROM bills b
        LEFT JOIN appointments a ON b.appointment_id = a.id
        LEFT JOIN doctors d ON a.doctor_id = d.id
        WHERE b.patient_id = ? AND b.is_deleted = 0
        ORDER BY b.created_at DESC
      `).bind(patientResult.id).all();
    } else {
      // Admin: get all bills
      bills = await c.env.DB.prepare(`
        SELECT 
          b.id, b.bill_number, b.subtotal, b.tax_amount, b.discount_amount, b.total_amount, b.payment_status,
          b.payment_method, b.payment_date, b.due_date, b.bill_date, b.notes, b.created_at,
          pt.first_name as patient_first_name, pt.last_name as patient_last_name,
          a.appointment_date,
          d.first_name as doctor_first_name, d.last_name as doctor_last_name
        FROM bills b
        JOIN patients pt ON b.patient_id = pt.id
        LEFT JOIN appointments a ON b.appointment_id = a.id
        LEFT JOIN doctors d ON a.doctor_id = d.id
        WHERE b.is_deleted = 0
        ORDER BY b.created_at DESC
      `).all();
    }

    // Calculate summary
    const allBills = bills?.results || [];
    const summary = {
      total_amount: allBills.reduce((sum: number, b: any) => sum + (b.total_amount || 0), 0),
      paid_amount: allBills.filter((b: any) => b.payment_status === 'paid').reduce((sum: number, b: any) => sum + (b.total_amount || 0), 0),
      pending_amount: allBills.filter((b: any) => b.payment_status === 'pending').reduce((sum: number, b: any) => sum + (b.total_amount || 0), 0),
      total_bills: allBills.length,
      paid_bills: allBills.filter((b: any) => b.payment_status === 'paid').length,
      pending_bills: allBills.filter((b: any) => b.payment_status === 'pending').length,
    };

    return c.json({ bills: allBills, summary });
  } catch (error) {
    console.error('Error fetching bills:', error);
    return c.json({ error: 'Failed to fetch bills' }, 500);
  }
});

// Get single bill
app.get('/:id', authMiddleware, async (c) => {
  try {
    const id = c.req.param('id');
    
    const bill = await c.env.DB.prepare(`
      SELECT 
        b.id, b.bill_number, b.subtotal, b.tax_amount, b.discount_amount, b.total_amount, b.payment_status,
        b.payment_method, b.payment_date, b.due_date, b.bill_date, b.notes, b.created_at,
        pt.first_name as patient_first_name, pt.last_name as patient_last_name,
        pt.phone as patient_phone, pt.address as patient_address,
        a.appointment_date, a.reason_for_visit as appointment_reason,
        d.first_name as doctor_first_name, d.last_name as doctor_last_name
      FROM bills b
      JOIN patients pt ON b.patient_id = pt.id
      LEFT JOIN appointments a ON b.appointment_id = a.id
      LEFT JOIN doctors d ON a.doctor_id = d.id
      WHERE b.id = ? AND b.is_deleted = 0
    `).bind(id).first();

    if (!bill) {
      return c.json({ error: 'Bill not found' }, 404);
    }

    return c.json({ bill });
  } catch (error) {
    console.error('Error fetching bill:', error);
    return c.json({ error: 'Failed to fetch bill' }, 500);
  }
});

// Update bill payment status
app.patch('/:id/pay', authMiddleware, async (c) => {
  try {
    const id = c.req.param('id');
    const { payment_method } = await c.req.json();
    
    await c.env.DB.prepare(`
      UPDATE bills 
      SET payment_status = 'paid', payment_method = ?, payment_date = datetime('now'), updated_at = datetime('now')
      WHERE id = ? AND is_deleted = 0
    `).bind(payment_method || 'Online', id).run();

    return c.json({ message: 'Payment successful' });
  } catch (error) {
    console.error('Error updating payment:', error);
    return c.json({ error: 'Failed to update payment' }, 500);
  }
});

export default app;
