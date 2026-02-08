-- Add notes column to medical_records if it doesn't exist
ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS notes TEXT;

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    report_type VARCHAR(100) NOT NULL,
    report_date DATE NOT NULL,
    findings TEXT,
    file_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for reports
CREATE INDEX IF NOT EXISTS idx_reports_patient ON reports(patient_id);
CREATE INDEX IF NOT EXISTS idx_reports_doctor ON reports(doctor_id);
CREATE INDEX IF NOT EXISTS idx_reports_date ON reports(report_date);
