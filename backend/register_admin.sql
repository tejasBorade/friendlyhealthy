-- Check if admin user exists
SELECT id, email, role, is_active FROM users WHERE email = 'admin@healcare.com' AND is_deleted = false;

-- If no admin exists, create one
-- Password hash for "Admin@123"
INSERT INTO users (email, password_hash, role, is_active, is_verified, is_deleted, failed_otp_attempts)
VALUES ('admin@healcare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqH.ROcVibKuTN0u7.6gjfG', 'admin', true, true, false, 0)
ON CONFLICT (email) DO UPDATE SET 
    password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqH.ROcVibKuTN0u7.6gjfG',
    is_active = true,
    is_verified = true;

-- Verify
SELECT id, email, role, is_active, is_verified FROM users WHERE email = 'admin@healfare.com' OR role = 'admin';
