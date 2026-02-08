import express from 'express';
import pool from '../config/database.js';
import { authenticate } from '../middleware/auth.js';

const router = express.Router();

// Get reports for a patient
router.get('/:patientId', authenticate, async (req, res) => {
  try {
    const { patientId } = req.params;
    
    const result = await pool.query(
      'SELECT * FROM reports WHERE patient_id = $1 ORDER BY report_date DESC',
      [patientId]
    );

    res.json({ reports: result.rows });
  } catch (error) {
    console.error('Get reports error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Add/Upload report
router.post('/', authenticate, async (req, res) => {
  try {
    const { 
      patientId, 
      reportType, 
      reportDate, 
      findings, 
      testName,
      labName,
      labAddress,
      labPhone,
      doctorRemarks,
      testResults
    } = req.body;
    const doctorId = req.user.doctorId; // Get doctor ID from authenticated user
    
    // For now, we'll store file path as a placeholder
    // In production, you'd integrate with file upload service (AWS S3, etc.)
    const filePath = req.file ? `/uploads/${req.file.filename}` : null;

    const result = await pool.query(
      `INSERT INTO reports 
       (patient_id, doctor_id, report_type, report_date, findings, file_url, test_name, lab_name, lab_address, lab_phone, doctor_remarks, test_results) 
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12) 
       RETURNING *`,
      [patientId, doctorId, reportType, reportDate, findings, filePath, testName, labName, labAddress, labPhone, doctorRemarks, testResults]
    );

    res.status(201).json({ 
      message: 'Report uploaded successfully',
      report: result.rows[0] 
    });
  } catch (error) {
    console.error('Upload report error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Update report
router.put('/:id', authenticate, async (req, res) => {
  try {
    const { id } = req.params;
    const { reportType, reportDate, findings } = req.body;

    const result = await pool.query(
      `UPDATE reports 
       SET report_type = $1, report_date = $2, findings = $3, updated_at = CURRENT_TIMESTAMP
       WHERE id = $4 
       RETURNING *`,
      [reportType, reportDate, findings, id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Report not found' });
    }

    res.json({ 
      message: 'Report updated successfully',
      report: result.rows[0] 
    });
  } catch (error) {
    console.error('Update report error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Delete report
router.delete('/:id', authenticate, async (req, res) => {
  try {
    const { id } = req.params;

    await pool.query('DELETE FROM reports WHERE id = $1', [id]);

    res.json({ message: 'Report deleted successfully' });
  } catch (error) {
    console.error('Delete report error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

export default router;
