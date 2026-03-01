# Test Email Notification After Fix
# Run this to test if emails are working now

Write-Host "Testing Email Notification System" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting backend with auto-reload..." -ForegroundColor Yellow
Write-Host "The full_name property has been added to Patient and Doctor models" -ForegroundColor Green
Write-Host ""

Write-Host "To test:" -ForegroundColor Cyan
Write-Host "1. Wait for backend to restart (watch the Backend API window)" -ForegroundColor White
Write-Host "2. Login as patient (patient@test.com / Test@123)" -ForegroundColor White
Write-Host "3. Book an appointment with any doctor" -ForegroundColor White
Write-Host "4. Check the email inbox for patient@test.com" -ForegroundColor White
Write-Host ""

Write-Host "Patient emails in database:" -ForegroundColor Yellow
Write-Host "  - test@example.com (Patient: John Doe)" -ForegroundColor White
Write-Host "  - patient@healthcare.com (Patient: Patient User)" -ForegroundColor White
Write-Host "  - patient@test.com (Patient: Test Patient)" -ForegroundColor White
Write-Host ""

Write-Host "If backend is already running, it should auto-reload in a few seconds..." -ForegroundColor Gray
Write-Host "If not, run: .\start-all-services.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "Press any key to continue..." -ForegroundColor Gray
pause
