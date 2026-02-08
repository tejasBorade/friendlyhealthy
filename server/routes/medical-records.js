import express from 'express';
import pool from '../config/database.js';
import { authenticate } from '../middleware/auth.js';

const router = express.Router();

// Get medical records for a patient
router.get('/:patientId', authenticate, async (req, res) => {
  try {
    const { patientId } = req.params;
    
    const result = await pool.query(
      'SELECT * FROM medical_records WHERE patient_id = $1 ORDER BY visit_date DESC',
      [patientId]
    );

    res.json({ records: result.rows });
  } catch (error) {
    console.error('Get medical records error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Add medical record
router.post('/', authenticate, async (req, res) => {
  try {
    const { 
      patientId, 
      diagnosis, 
      symptoms, 
      treatment, 
      notes, 
      visitDate,
      allergies,
      chronicDiseases,
      surgeries,
      familyHistory,
      bloodPressure,
      temperature,
      weight,
      height
    } = req.body;
    const doctorId = req.user.doctorId; // Get doctor ID from authenticated user

    const result = await pool.query(
      `INSERT INTO medical_records 
       (patient_id, doctor_id, diagnosis, symptoms, treatment, notes, visit_date, allergies, chronic_diseases, surgeries, family_history, blood_pressure, temperature, weight, height) 
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15) 
       RETURNING *`,
      [patientId, doctorId, diagnosis, symptoms, treatment, notes, visitDate, allergies, chronicDiseases, surgeries, familyHistory, bloodPressure, temperature, weight, height]
    );

    res.status(201).json({ 
      message: 'Medical record added successfully',
      record: result.rows[0] 
    });
  } catch (error) {
    console.error('Add medical record error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Update medical record
router.put('/:id', authenticate, async (req, res) => {
  try {
    const { id } = req.params;
    const { diagnosis, symptoms, treatment, notes } = req.body;

    const result = await pool.query(
      `UPDATE medical_records 
       SET diagnosis = $1, symptoms = $2, treatment = $3, notes = $4, updated_at = CURRENT_TIMESTAMP
       WHERE id = $5 
       RETURNING *`,
      [diagnosis, symptoms, treatment, notes, id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Medical record not found' });
    }

    res.json({ 
      message: 'Medical record updated successfully',
      record: result.rows[0] 
    });
  } catch (error) {
    console.error('Update medical record error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Delete medical record
router.delete('/:id', authenticate, async (req, res) => {
  try {
    const { id } = req.params;

    await pool.query('DELETE FROM medical_records WHERE id = $1', [id]);

    res.json({ message: 'Medical record deleted successfully' });
  } catch (error) {
    console.error('Delete medical record error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

export default router;
