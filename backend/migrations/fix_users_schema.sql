-- Migration: Fix users table schema
BEGIN;

-- Add missing columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;

-- Create index on is_deleted for better query performance
CREATE INDEX IF NOT EXISTS idx_users_is_deleted ON users(is_deleted);

COMMIT;
