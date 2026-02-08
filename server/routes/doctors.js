import express from 'express';
import pool from '../config/database.js';
import { authenticate, authorize } from '../middleware/auth.js';

const router = express.Router();

// Get all doctors
router.get('/', async (req, res) => {
  try {
    const { specialization, available } = req.query;
    
    let query = `
      SELECT d.*, u.email 
      FROM doctors d
      JOIN users u ON d.user_id = u.id
      WHERE u.is_active = true
    `;
    
    const params = [];
    let paramIndex = 1;

    if (specialization) {
      query += ` AND d.specialization ILIKE $${paramIndex}`;
      params.push(`%${specialization}%`);
      paramIndex++;
    }

    if (available === 'true') {
      query += ` AND d.is_available = true`;
    }

    query += ' ORDER BY d.first_name, d.last_name';

    const result = await pool.query(query, params);
    res.json({ doctors: result.rows });
  } catch (error) {
    console.error('Get doctors error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Get doctor by ID
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const result = await pool.query(`
      SELECT d.*, u.email 
      FROM doctors d
      JOIN users u ON d.user_id = u.id
      WHERE d.id = $1
    `, [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Doctor not found' });
    }

    res.json({ doctor: result.rows[0] });
  } catch (error) {
    console.error('Get doctor error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Update doctor profile (authenticated)
router.put('/:id', authenticate, authorize('doctor', 'admin'), async (req, res) => {
  try {
    const { id } = req.params;
    const { 
      firstName, lastName, specialization, qualification, 
      experienceYears,phone, consultationFee, 
      clinicName, clinicAddress, clinicPhone,
      hospitalAffiliation, licenseNumber,
      availableDays, availableHours, isAvailable 
    } = req.body;

    const result = await pool.query(`
      UPDATE doctors 
      SET first_name = COALESCE($1, first_name),
          last_name = COALESCE($2, last_name),
          specialization = COALESCE($3, specialization),
          qualification = COALESCE($4, qualification),
          experience_years = COALESCE($5, experience_years),
          phone = COALESCE($6, phone),
          consultation_fee = COALESCE($7, consultation_fee),
          clinic_name = COALESCE($8, clinic_name),
          clinic_address = COALESCE($9, clinic_address),
          clinic_phone = COALESCE($10, clinic_phone),
          hospital_affiliation = COALESCE($11, hospital_affiliation),
          license_number = COALESCE($12, license_number),
          available_days = COALESCE($13, available_days),
          available_hours = COALESCE($14, available_hours),
          is_available = COALESCE($15, is_available),
          updated_at = CURRENT_TIMESTAMP
      WHERE id = $16
      RETURNING *
    `, [firstName, lastName, specialization, qualification, experienceYears, 
        phone, consultationFee, clinicName, clinicAddress, clinicPhone,
        hospitalAffiliation, licenseNumber, availableDays, availableHours, isAvailable, id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Doctor not found' });
    }

    res.json({ 
      message: 'Doctor profile updated successfully',
      doctor: result.rows[0] 
    });
  } catch (error) {
    console.error('Update doctor error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

export default router;

// Update doctor profile
router.put('/:id', authenticate, authorize('doctor', 'admin'), async (req, res) => {
  try {
    const { id } = req.params;
    const {
      firstName,
      lastName,
      specialization,
      qualification,
      experienceYears,
      phone,
      consultationFee,
      clinicName,
      clinicAddress,
      clinicPhone,
      hospitalAffiliation,
      licenseNumber,
      availableDays,
      availableHours,
      isAvailable
    } = req.body;
    
    const result = await pool.query(`
      UPDATE doctors 
      SET 
        first_name = COALESCE($1, first_name),
        last_name = COALESCE($2, last_name),
        specialization = COALESCE($3, specialization),
        qualification = COALESCE($4, qualification),
        experience_years = COALESCE($5, experience_years),
        phone = COALESCE($6, phone),
        consultation_fee = COALESCE($7, consultation_fee),
        clinic_name = COALESCE($8, clinic_name),
        clinic_address = COALESCE($9, clinic_address),
        clinic_phone = COALESCE($10, clinic_phone),
        hospital_affiliation = COALESCE($11, hospital_affiliation),
        license_number = COALESCE($12, license_number),
        available_days = COALESCE($13, available_days),
        available_hours = COALESCE($14, available_hours),
        is_available = COALESCE($15, is_available),
        updated_at = CURRENT_TIMESTAMP
      WHERE id = $16
      RETURNING *
    `, [
      firstName, lastName, specialization, qualification, experienceYears,
      phone, consultationFee, clinicName, clinicAddress, clinicPhone,
      hospitalAffiliation, licenseNumber, availableDays, availableHours,
      isAvailable, id
    ]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Doctor not found' });
    }
    
    res.json({ 
      message: 'Doctor profile updated successfully',
      doctor: result.rows[0] 
    });
  } catch (error) {
    console.error('Update doctor error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Add doctor time slot
router.post('/:id/time-slots', authenticate, authorize('doctor', 'admin'), async (req, res) => {
  try {
    const { id } = req.params;
    const { dayOfWeek, startTime, endTime, slotDuration } = req.body;
    
    const result = await pool.query(`
      INSERT INTO doctor_time_slots (doctor_id, day_of_week, start_time, end_time, slot_duration)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `, [id, dayOfWeek, startTime, endTime, slotDuration || 30]);
    
    res.status(201).json({ 
      message: 'Time slot added successfully',
      timeSlot: result.rows[0] 
    });
  } catch (error) {
    console.error('Add time slot error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Delete doctor time slot
router.delete('/:doctorId/time-slots/:slotId', authenticate, authorize('doctor', 'admin'), async (req, res) => {
  try {
    const { slotId } = req.params;
    
    await pool.query('DELETE FROM doctor_time_slots WHERE id = $1', [slotId]);
    
    res.json({ message: 'Time slot deleted successfully' });
  } catch (error) {
    console.error('Delete time slot error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Get available time slots for booking
router.get('/:id/available-slots', async (req, res) => {
  try {
    const { id } = req.params;
    const { date } = req.query;
    
    if (!date) {
      return res.status(400).json({ message: 'Date parameter is required' });
    }
    
    // Get day of week (0-6)
    const dayOfWeek = new Date(date).getDay();
    
    // Get doctor's time slots for this day
    const slotsResult = await pool.query(
      `SELECT * FROM doctor_time_slots 
       WHERE doctor_id = $1 AND day_of_week = $2 AND is_available = true`,
      [id, dayOfWeek]
    );
    
    if (slotsResult.rows.length === 0) {
      return res.json({ availableSlots: [] });
    }
    
    // Get booked appointments for this date
    const bookedResult = await pool.query(
      `SELECT appointment_time FROM appointments 
       WHERE doctor_id = $1 AND appointment_date = $2 AND status NOT IN ('cancelled', 'rejected')`,
      [id, date]
    );
    
    const bookedTimes = bookedResult.rows.map(row => row.appointment_time);
    
    // Generate available slots
    const availableSlots = [];
    for (const slot of slotsResult.rows) {
      const start = new Date(`2000-01-01 ${slot.start_time}`);
      const end = new Date(`2000-01-01 ${slot.end_time}`);
      const duration = slot.slot_duration;
      
      let current = start;
      while (current < end) {
        const timeStr = current.toTimeString().slice(0, 5);
        if (!bookedTimes.includes(timeStr)) {
          availableSlots.push(timeStr);
        }
        current = new Date(current.getTime() + duration * 60000);
      }
    }
    
    res.json({ availableSlots });
  } catch (error) {
    console.error('Get available slots error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});
