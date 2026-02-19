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

// Get all medical records for current patient
app.get('/', authMiddleware, async (c) => {
  try {
    const user = c.get('user');
    const queryPatientId = c.req.query('patientId');
    
    // Get patient ID from user
    const patientResult = await c.env.DB.prepare(
      'SELECT id FROM patients WHERE user_id = ?'
    ).bind(user.sub).first();

    let records;
    
    if (patientResult) {
      // Patient: get their records
        records = await c.env.DB.prepare(`
          SELECT 
            mr.id, mr.patient_id, mr.doctor_id, mr.appointment_id,
            mr.report_type, mr.report_name, mr.doctor_remarks, mr.file_url,
            mr.test_date, mr.result_summary, mr.created_at, mr.test_name, mr.lab_name,
            d.first_name as doctor_first_name, d.last_name as doctor_last_name, d.specialization,
            a.appointment_date, a.reason_for_visit as appointment_reason
        FROM medical_reports mr
        LEFT JOIN doctors d ON mr.doctor_id = d.id
        LEFT JOIN appointments a ON mr.appointment_id = a.id
        WHERE mr.patient_id = ? AND mr.is_deleted = 0
        ORDER BY mr.test_date DESC
      `).bind(patientResult.id).all();
    } else {
      // Doctor: get records they created
      const doctorResult = await c.env.DB.prepare(
        'SELECT id FROM doctors WHERE user_id = ?'
      ).bind(user.sub).first();
      
      if (doctorResult) {
        let doctorQuery = `
          SELECT 
            mr.id, mr.patient_id, mr.doctor_id, mr.appointment_id,
            mr.report_type, mr.report_name, mr.doctor_remarks, mr.file_url,
            mr.test_date, mr.result_summary, mr.created_at, mr.test_name, mr.lab_name,
            pt.first_name as patient_first_name, pt.last_name as patient_last_name,
            a.appointment_date, a.reason_for_visit as appointment_reason
          FROM medical_reports mr
          JOIN patients pt ON mr.patient_id = pt.id
          LEFT JOIN appointments a ON mr.appointment_id = a.id
          WHERE mr.doctor_id = ? AND mr.is_deleted = 0
        `;

        const doctorParams = [doctorResult.id];
        if (queryPatientId) {
          doctorQuery += ' AND mr.patient_id = ?';
          doctorParams.push(queryPatientId);
        }

        doctorQuery += ' ORDER BY mr.test_date DESC';
        records = await c.env.DB.prepare(doctorQuery).bind(...doctorParams).all();
      } else {
        // Admin: get all records
        let adminQuery = `
          SELECT 
            mr.id, mr.patient_id, mr.doctor_id, mr.appointment_id,
            mr.report_type, mr.report_name, mr.doctor_remarks, mr.file_url,
            mr.test_date, mr.result_summary, mr.created_at, mr.test_name, mr.lab_name,
            pt.first_name as patient_first_name, pt.last_name as patient_last_name,
            d.first_name as doctor_first_name, d.last_name as doctor_last_name,
            a.appointment_date
          FROM medical_reports mr
          JOIN patients pt ON mr.patient_id = pt.id
          LEFT JOIN doctors d ON mr.doctor_id = d.id
          LEFT JOIN appointments a ON mr.appointment_id = a.id
          WHERE mr.is_deleted = 0
        `;

        const adminParams: string[] = [];
        if (queryPatientId) {
          adminQuery += ' AND mr.patient_id = ?';
          adminParams.push(queryPatientId);
        }

        adminQuery += ' ORDER BY mr.test_date DESC';
        records = await c.env.DB.prepare(adminQuery).bind(...adminParams).all();
      }
    }

    return c.json({ records: records?.results || [] });
  } catch (error) {
    console.error('Error fetching medical records:', error);
    return c.json({ error: 'Failed to fetch medical records' }, 500);
  }
});

// Create medical record
app.post('/', authMiddleware, async (c) => {
  try {
    const user = c.get('user');
    const body = await c.req.json();

    const patientId = body.patientId ?? body.patient_id;
    if (!patientId) {
      return c.json({ error: 'patientId is required' }, 400);
    }

    const patientExists = await c.env.DB.prepare(
      'SELECT id FROM patients WHERE id = ?'
    ).bind(patientId).first();
    if (!patientExists) {
      return c.json({ error: 'Invalid patientId' }, 400);
    }

    const doctorResult = await c.env.DB.prepare(
      'SELECT id FROM doctors WHERE user_id = ?'
    ).bind(user.sub).first();

    const doctorId = doctorResult?.id || body.doctorId || body.doctor_id || null;
    const reportType = body.reportType || body.report_type || body.recordType || 'other';
    const reportName = body.reportName || body.report_name || body.title || body.diagnosis || 'Medical Report';
    const doctorRemarks = body.doctorRemarks || body.doctor_remarks || body.description ||
      [body.symptoms, body.treatment, body.notes].filter(Boolean).join(' | ') ||
      null;
    const reportFilePath = body.reportFilePath || body.report_file_path || body.fileUrl || body.file_url || '/reports/default.pdf';
    const fileUrl = body.fileUrl || body.file_url || null;
    const testDate = body.testDate || body.test_date || body.visitDate || body.reportDate || new Date().toISOString().split('T')[0];
    const testName = body.testName || body.test_name || null;
    const labName = body.labName || body.lab_name || null;
    const resultSummary = body.resultSummary || body.result_summary || body.findings || body.notes || null;
    const appointmentId = body.appointmentId || body.appointment_id || null;

    const recordId = crypto.randomUUID();
    await c.env.DB.prepare(`
      INSERT INTO medical_reports (
        id, patient_id, doctor_id, appointment_id, report_type, report_name,
        doctor_remarks, report_file_path, file_url, test_date, test_name, lab_name,
        result_summary, uploaded_by, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      recordId,
      String(patientId),
      doctorId ? String(doctorId) : null,
      appointmentId ? String(appointmentId) : null,
      String(reportType),
      String(reportName),
      doctorRemarks ? String(doctorRemarks) : null,
      String(reportFilePath),
      fileUrl ? String(fileUrl) : null,
      String(testDate),
      testName ? String(testName) : null,
      labName ? String(labName) : null,
      resultSummary ? String(resultSummary) : null,
      String(user.sub),
      new Date().toISOString()
    ).run();

    return c.json({ id: recordId, message: 'Medical record created' }, 201);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error('Error creating medical record:', message);
    return c.json({ error: 'Failed to create medical record' }, 500);
  }
});

// Get single record
app.get('/:id', authMiddleware, async (c) => {
  try {
    const id = c.req.param('id');
    
    const record = await c.env.DB.prepare(`
      SELECT 
        mr.id, mr.report_type, mr.report_name, mr.doctor_remarks, mr.file_url,
        mr.test_date, mr.test_name, mr.lab_name, mr.result_summary, mr.created_at,
        pt.first_name as patient_first_name, pt.last_name as patient_last_name,
        d.first_name as doctor_first_name, d.last_name as doctor_last_name, d.specialization,
        a.appointment_date, a.reason_for_visit as appointment_reason
      FROM medical_reports mr
      JOIN patients pt ON mr.patient_id = pt.id
      LEFT JOIN doctors d ON mr.doctor_id = d.id
      LEFT JOIN appointments a ON mr.appointment_id = a.id
      WHERE mr.id = ? AND mr.is_deleted = 0
    `).bind(id).first();

    if (!record) {
      return c.json({ error: 'Record not found' }, 404);
    }

    return c.json({ record });
  } catch (error) {
    console.error('Error fetching medical record:', error);
    return c.json({ error: 'Failed to fetch medical record' }, 500);
  }
});

export default app;
