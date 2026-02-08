import express from 'express';
import pool from '../config/database.js';
import { authenticate, authorize } from '../middleware/auth.js';

const router = express.Router();

// Generate invoice number
const generateInvoiceNumber = async () => {
  const result = await pool.query("SELECT nextval('invoice_number_seq')");
  const seq = result.rows[0].nextval;
  return `INV-${new Date().getFullYear()}-${String(seq).padStart(5, '0')}`;
};

// Get all invoices (with filters)
router.get('/', authenticate, async (req, res) => {
  try {
    const { patientId, status, fromDate, toDate } = req.query;
    
    let query = `
      SELECT i.*, 
             p.first_name || ' ' || p.last_name as patient_name,
             d.first_name || ' ' || d.last_name as doctor_name
      FROM invoices i
      LEFT JOIN patients p ON i.patient_id = p.id
      LEFT JOIN doctors d ON i.doctor_id = d.id
      WHERE 1=1
    `;
    const params = [];
    
    if (patientId) {
      params.push(patientId);
      query += ` AND i.patient_id = $${params.length}`;
    }
    
    if (status) {
      params.push(status);
      query += ` AND i.payment_status = $${params.length}`;
    }
    
    if (fromDate) {
      params.push(fromDate);
      query += ` AND i.invoice_date >= $${params.length}`;
    }
    
    if (toDate) {
      params.push(toDate);
      query += ` AND i.invoice_date <= $${params.length}`;
    }
    
    query += ' ORDER BY i.created_at DESC';
    
    const result = await pool.query(query, params);
    res.json({ invoices: result.rows });
  } catch (error) {
    console.error('Get invoices error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Get single invoice with items
router.get('/:id', authenticate, async (req, res) => {
  try {
    const { id } = req.params;
    
    // Get invoice
    const invoiceResult = await pool.query(
      `SELECT i.*, 
              p.first_name || ' ' || p.last_name as patient_name,
              p.phone as patient_phone,
              p.address as patient_address,
              d.first_name || ' ' || d.last_name as doctor_name,
              d.specialization as doctor_specialization
       FROM invoices i
       LEFT JOIN patients p ON i.patient_id = p.id
       LEFT JOIN doctors d ON i.doctor_id = d.id
       WHERE i.id = $1`,
      [id]
    );
    
    if (invoiceResult.rows.length === 0) {
      return res.status(404).json({ message: 'Invoice not found' });
    }
    
    // Get invoice items
    const itemsResult = await pool.query(
      'SELECT * FROM invoice_items WHERE invoice_id = $1 ORDER BY id',
      [id]
    );
    
    const invoice = {
      ...invoiceResult.rows[0],
      items: itemsResult.rows
    };
    
    res.json({ invoice });
  } catch (error) {
    console.error('Get invoice error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Create invoice
router.post('/', authenticate, authorize('doctor', 'staff', 'admin'), async (req, res) => {
  const client = await pool.connect();
  
  try {
    await client.query('BEGIN');
    
    const {
      patientId,
      doctorId,
      appointmentId,
      items,
      taxRate,
      discount,
      notes,
      dueDate
    } = req.body;
    
    // Calculate totals
    const subtotal = items.reduce((sum, item) => sum + parseFloat(item.total_price), 0);
    const taxAmount = subtotal * (taxRate / 100);
    const totalAmount = subtotal + taxAmount - (discount || 0);
    
    const invoiceNumber = await generateInvoiceNumber();
    
    // Insert invoice
    const invoiceResult = await client.query(
      `INSERT INTO invoices 
       (invoice_number, patient_id, doctor_id, appointment_id, subtotal, tax_rate, tax_amount, discount, total_amount, due_date, notes) 
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) 
       RETURNING *`,
      [invoiceNumber, patientId, doctorId, appointmentId, subtotal, taxRate, taxAmount, discount, totalAmount, dueDate, notes]
    );
    
    const invoice = invoiceResult.rows[0];
    
    // Insert invoice items
    for (const item of items) {
      await client.query(
        `INSERT INTO invoice_items 
         (invoice_id, item_type, item_name, description, quantity, unit_price, total_price) 
         VALUES ($1, $2, $3, $4, $5, $6, $7)`,
        [invoice.id, item.item_type, item.item_name, item.description, item.quantity, item.unit_price, item.total_price]
      );
    }
    
    await client.query('COMMIT');
    
    res.status(201).json({ 
      message: 'Invoice created successfully',
      invoice 
    });
  } catch (error) {
    await client.query('ROLLBACK');
    console.error('Create invoice error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  } finally {
    client.release();
  }
});

// Update invoice
router.put('/:id', authenticate, authorize('staff', 'admin'), async (req, res) => {
  try {
    const { id } = req.params;
    const { paymentStatus, paymentMethod, paymentDate, notes } = req.body;
    
    const result = await pool.query(
      `UPDATE invoices 
       SET payment_status = $1, payment_method = $2, payment_date = $3, notes = $4, updated_at = CURRENT_TIMESTAMP
       WHERE id = $5 
       RETURNING *`,
      [paymentStatus, paymentMethod, paymentDate, notes, id]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Invoice not found' });
    }
    
    res.json({ 
      message: 'Invoice updated successfully',
      invoice: result.rows[0] 
    });
  } catch (error) {
    console.error('Update invoice error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Delete invoice
router.delete('/:id', authenticate, authorize('admin'), async (req, res) => {
  try {
    const { id } = req.params;
    
    await pool.query('DELETE FROM invoices WHERE id = $1', [id]);
    
    res.json({ message: 'Invoice deleted successfully' });
  } catch (error) {
    console.error('Delete invoice error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Get billing statistics
router.get('/stats/summary', authenticate, authorize('admin'), async (req, res) => {
  try {
    const { fromDate, toDate } = req.query;
    
    let dateFilter = '';
    const params = [];
    
    if (fromDate) {
      params.push(fromDate);
      dateFilter += ` AND invoice_date >= $${params.length}`;
    }
    
    if (toDate) {
      params.push(toDate);
      dateFilter += ` AND invoice_date <= $${params.length}`;
    }
    
    const result = await pool.query(`
      SELECT 
        COUNT(*) FILTER (WHERE payment_status = 'paid') as total_paid_invoices,
        COUNT(*) FILTER (WHERE payment_status = 'pending') as total_pending_invoices,
        COUNT(*) FILTER (WHERE payment_status = 'overdue') as total_overdue_invoices,
        SUM(total_amount) FILTER (WHERE payment_status = 'paid') as total_revenue,
        SUM(total_amount) FILTER (WHERE payment_status = 'pending') as pending_amount,
        SUM(total_amount) FILTER (WHERE payment_status = 'overdue') as overdue_amount,
        AVG(total_amount) as average_invoice_amount
      FROM invoices
      WHERE 1=1 ${dateFilter}
    `, params);
    
    res.json({ stats: result.rows[0] });
  } catch (error) {
    console.error('Get billing stats error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

export default router;
