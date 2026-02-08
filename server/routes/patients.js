import express from 'express';
import pool from '../config/database.js';
import { authenticate } from '../middleware/auth.js';

const router = express.Router();

// Get patient details
router.get('/:id', authenticate, async (req, res) => {
  try {
    const { id } = req.params;
    
    const result = await pool.query(
      'SELECT * FROM patients WHERE id = $1',
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Patient not found' });
    }

    res.json({ patient: result.rows[0] });
  } catch (error) {
    console.error('Get patient error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Get all patients (staff/admin only)
router.get('/', authenticate, async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT p.*, u.email FROM patients p JOIN users u ON p.user_id = u.id ORDER BY p.created_at DESC'
    );

    res.json({ patients: result.rows });
  } catch (error) {
    console.error('Get patients error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

export default router;
