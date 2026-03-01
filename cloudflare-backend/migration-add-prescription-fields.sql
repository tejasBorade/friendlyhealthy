-- Migration to add medication fields directly to prescriptions table
-- This aligns the Cloudflare D1 schema with the PostgreSQL backend

-- Add medication fields to prescriptions table
ALTER TABLE prescriptions ADD COLUMN medication_name TEXT;
ALTER TABLE prescriptions ADD COLUMN dosage TEXT;
ALTER TABLE prescriptions ADD COLUMN frequency TEXT;
ALTER TABLE prescriptions ADD COLUMN duration TEXT;
ALTER TABLE prescriptions ADD COLUMN instructions TEXT;
ALTER TABLE prescriptions ADD COLUMN prescribed_date TEXT;

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_prescriptions_prescribed_date ON prescriptions(prescribed_date);

-- Note: Existing prescription_medications table can remain for backward compatibility
-- or can be dropped if no longer needed
