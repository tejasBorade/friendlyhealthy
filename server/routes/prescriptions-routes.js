import express from 'express';
import pool from '../config/database.js';
import { authenticate } from '../middleware/auth.js';

const router = express.Router();

// Get prescriptions for a patient
router.get('/:patientId', authenticate, async (req, res) => {
  try {
    const { patientId } = req.params;
    
    const result = await pool.query(
      'SELECT * FROM prescriptions WHERE patient_id = $1 ORDER BY prescribed_date DESC',
      [patientId]
    );

    res.json({ prescriptions: result.rows });
  } catch (error) {
    console.error('Get prescriptions error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Add prescription
router.post('/', authenticate, async (req, res) => {
  try {
    const { 
      patientId, 
      medicationName, 
      dosage, 
      frequency, 
      duration, 
      instructions, 
      prescribedDate,
      usageTiming,
      frequencyPattern
    } = req.body;
    const doctorId = req.user.doctorId; // Get doctor ID from authenticated user

    const result = await pool.query(
      `INSERT INTO prescriptions 
       (patient_id, doctor_id, medication_name, dosage, frequency, duration, instructions, prescribed_date, usage_timing, frequency_pattern) 
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) 
       RETURNING *`,
      [patientId, doctorId, medicationName, dosage, frequency, duration, instructions, prescribedDate, usageTiming, frequencyPattern]
    );

    res.status(201).json({ 
      message: 'Prescription added successfully',
      prescription: result.rows[0] 
    });
  } catch (error) {
    console.error('Add prescription error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Update prescription
router.put('/:id', authenticate, async (req, res) => {
  try {
    const { id } = req.params;
    const { medicationName, dosage, frequency, duration, instructions } = req.body;

    const result = await pool.query(
      `UPDATE prescriptions 
       SET medication_name = $1, dosage = $2, frequency = $3, duration = $4, instructions = $5, updated_at = CURRENT_TIMESTAMP
       WHERE id = $6 
       RETURNING *`,
      [medicationName, dosage, frequency, duration, instructions, id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Prescription not found' });
    }

    res.json({ 
      message: 'Prescription updated successfully',
      prescription: result.rows[0] 
    });
  } catch (error) {
    console.error('Update prescription error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Delete prescription
router.delete('/:id', authenticate, async (req, res) => {
  try {
    const { id } = req.params;

    await pool.query('DELETE FROM prescriptions WHERE id = $1', [id]);

    res.json({ message: 'Prescription deleted successfully' });
  } catch (error) {
    console.error('Delete prescription error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

export default router;
