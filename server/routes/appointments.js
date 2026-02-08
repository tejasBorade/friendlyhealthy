import express from 'express';
import pool from '../config/database.js';
import { authenticate } from '../middleware/auth.js';

const router = express.Router();

// Get all appointments (with filters)
router.get('/', authenticate, async (req, res) => {
  try {
    const { patientId, doctorId, status, date } = req.query;
    
    let query = `
      SELECT 
        a.*,
        p.first_name as patient_first_name,
        p.last_name as patient_last_name,
        d.first_name as doctor_first_name,
        d.last_name as doctor_last_name,
        d.specialization
      FROM appointments a
      JOIN patients p ON a.patient_id = p.id
      JOIN doctors d ON a.doctor_id = d.id
      WHERE 1=1
    `;
    
    const params = [];
    let paramIndex = 1;

    if (patientId) {
      query += ` AND a.patient_id = $${paramIndex}`;
      params.push(patientId);
      paramIndex++;
    }

    if (doctorId) {
      query += ` AND a.doctor_id = $${paramIndex}`;
      params.push(doctorId);
      paramIndex++;
    }

    if (status) {
      query += ` AND a.status = $${paramIndex}`;
      params.push(status);
      paramIndex++;
    }

    if (date) {
      query += ` AND a.appointment_date = $${paramIndex}`;
      params.push(date);
      paramIndex++;
    }

    query += ' ORDER BY a.appointment_date DESC, a.appointment_time DESC';

    const result = await pool.query(query, params);
    res.json({ appointments: result.rows });
  } catch (error) {
    console.error('Get appointments error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Create appointment
router.post('/', authenticate, async (req, res) => {
  try {
    const { patientId, doctorId, appointmentDate, appointmentTime, reason } = req.body;

    // Check if patient exists
    const patientCheck = await pool.query('SELECT id FROM patients WHERE id = $1', [patientId]);
    if (patientCheck.rows.length === 0) {
      return res.status(404).json({ message: 'Patient not found' });
    }

    // Check if doctor exists
    const doctorCheck = await pool.query('SELECT id FROM doctors WHERE id = $1', [doctorId]);
    if (doctorCheck.rows.length === 0) {
      return res.status(404).json({ message: 'Doctor not found' });
    }

    // Check for conflicting appointments
    const conflictCheck = await pool.query(`
      SELECT id FROM appointments 
      WHERE doctor_id = $1 
      AND appointment_date = $2 
      AND appointment_time = $3 
      AND status != 'cancelled'
    `, [doctorId, appointmentDate, appointmentTime]);

    if (conflictCheck.rows.length > 0) {
      return res.status(400).json({ message: 'Time slot already booked' });
    }

    const result = await pool.query(`
      INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, status)
      VALUES ($1, $2, $3, $4, $5, 'booked')
      RETURNING *
    `, [patientId, doctorId, appointmentDate, appointmentTime, reason]);

    res.status(201).json({ 
      message: 'Appointment created successfully',
      appointment: result.rows[0] 
    });
  } catch (error) {
    console.error('Create appointment error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Update appointment status
router.patch('/:id', authenticate, async (req, res) => {
  try {
    const { id } = req.params;
    const { status, notes } = req.body;

    const result = await pool.query(`
      UPDATE appointments 
      SET status = COALESCE($1, status),
          notes = COALESCE($2, notes),
          updated_at = CURRENT_TIMESTAMP
      WHERE id = $3
      RETURNING *
    `, [status, notes, id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Appointment not found' });
    }

    res.json({ 
      message: 'Appointment updated successfully',
      appointment: result.rows[0] 
    });
  } catch (error) {
    console.error('Update appointment error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Delete appointment
router.delete('/:id', authenticate, async (req, res) => {
  try {
    const { id } = req.params;

    const result = await pool.query('DELETE FROM appointments WHERE id = $1 RETURNING id', [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Appointment not found' });
    }

    res.json({ message: 'Appointment deleted successfully' });
  } catch (error) {
    console.error('Delete appointment error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Accept appointment (doctor)
router.patch('/:id/accept', authenticate, async (req, res) => {
  try {
    const { id } = req.params;
    
    const result = await pool.query(`
      UPDATE appointments 
      SET status = 'confirmed',
          status_updated_at = CURRENT_TIMESTAMP,
          updated_at = CURRENT_TIMESTAMP
      WHERE id = $1
      RETURNING *
    `, [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Appointment not found' });
    }

    res.json({ 
      message: 'Appointment accepted successfully',
      appointment: result.rows[0] 
    });
  } catch (error) {
    console.error('Accept appointment error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Reject appointment (doctor)
router.patch('/:id/reject', authenticate, async (req, res) => {
  try {
    const { id } = req.params;
    const { reason } = req.body;
    
    const result = await pool.query(`
      UPDATE appointments 
      SET status = 'rejected',
          cancellation_reason = $1,
          status_updated_at = CURRENT_TIMESTAMP,
          updated_at = CURRENT_TIMESTAMP
      WHERE id = $2
      RETURNING *
    `, [reason, id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Appointment not found' });
    }

    res.json({ 
      message: 'Appointment rejected',
      appointment: result.rows[0] 
    });
  } catch (error) {
    console.error('Reject appointment error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Reschedule appointment
router.post('/:id/reschedule', authenticate, async (req, res) => {
  const client = await pool.connect();
  
  try {
    await client.query('BEGIN');
    
    const { id } = req.params;
    const { newDate, newTime, reason } = req.body;
    
    // Get original appointment
    const originalResult = await client.query('SELECT * FROM appointments WHERE id = $1', [id]);
    if (originalResult.rows.length === 0) {
      await client.query('ROLLBACK');
      return res.status(404).json({ message: 'Appointment not found' });
    }
    
    const original = originalResult.rows[0];
    
    // Check for conflicts
    const conflictCheck = await client.query(`
      SELECT id FROM appointments 
      WHERE doctor_id = $1 
      AND appointment_date = $2 
      AND appointment_time = $3 
      AND status NOT IN ('cancelled', 'rejected')
      AND id != $4
    `, [original.doctor_id, newDate, newTime, id]);

    if (conflictCheck.rows.length > 0) {
      await client.query('ROLLBACK');
      return res.status(400).json({ message: 'Time slot already booked' });
    }
    
    // Update appointment
    const result = await client.query(`
      UPDATE appointments 
      SET appointment_date = $1,
          appointment_time = $2,
          status = 'booked',
          cancellation_reason = $3,
          status_updated_at = CURRENT_TIMESTAMP,
          updated_at = CURRENT_TIMESTAMP
      WHERE id = $4
      RETURNING *
    `, [newDate, newTime, reason, id]);
    
    await client.query('COMMIT');
    
    res.json({ 
      message: 'Appointment rescheduled successfully',
      appointment: result.rows[0] 
    });
  } catch (error) {
    await client.query('ROLLBACK');
    console.error('Reschedule appointment error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  } finally {
    client.release();
  }
});

export default router;
