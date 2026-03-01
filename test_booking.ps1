# Test Appointment Booking Script
Write-Host "================================================================================"
Write-Host " TESTING APPOINTMENT BOOKING"
Write-Host "================================================================================"

# Login as patient
Write-Host "`nStep 1: Patient Login" -ForegroundColor Yellow
$loginBody = @{
    email = "patient@test.com"
    password = "Test@123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
$patientToken = $response.access_token
$headers = @{ "Authorization" = "Bearer $patientToken" }
Write-Host "Success: Patient logged in (User ID: $($response.user.id))" -ForegroundColor Green

# Get a doctor ID
Write-Host "`nStep 2: Getting doctor list" -ForegroundColor Yellow
$doctors = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/doctors" -Headers $headers
$doctorId = $doctors.doctors[0].id
$doctorName = "$($doctors.doctors[0].first_name) $($doctors.doctors[0].last_name)"
Write-Host "Success: Using Doctor ID: $doctorId ($doctorName)" -ForegroundColor Green

# Book an appointment
Write-Host "`nStep 3: Booking appointment" -ForegroundColor Yellow
$tomorrow = (Get-Date).AddDays(1).ToString("yyyy-MM-dd")
$appointmentBody = @{
    doctor_id = $doctorId
    appointment_date = $tomorrow
    appointment_time = "10:00"
    reason = "Test booking - Regular checkup"
} | ConvertTo-Json

Write-Host "Request payload:" -ForegroundColor Gray
Write-Host $appointmentBody -ForegroundColor Gray

try {
    $appointment = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/appointments" -Method POST -Headers $headers -Body $appointmentBody -ContentType "application/json"
    Write-Host "SUCCESS: Appointment booked!" -ForegroundColor Green
    Write-Host "  Appointment ID: $($appointment.id)" -ForegroundColor White
    Write-Host "  Date: $($appointment.appointment_date)" -ForegroundColor White
    Write-Host "  Time: $($appointment.appointment_time)" -ForegroundColor White
    Write-Host "  Status: $($appointment.status)" -ForegroundColor White
} catch {
    Write-Host "FAILED: Appointment booking failed!" -ForegroundColor Red
    Write-Host "Error: $($_.ErrorDetails.Message)" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
}

# Test admin booking for patient
Write-Host ""
Write-Host "================================================================================"
Write-Host " TESTING ADMIN BOOKING FOR PATIENT"
Write-Host "================================================================================"

Write-Host "`nStep 4: Admin Login" -ForegroundColor Yellow
$adminLoginBody = @{
    email = "admin@healthcare.com"
    password = "Admin@123"
} | ConvertTo-Json

$adminResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $adminLoginBody -ContentType "application/json"
$adminToken = $adminResponse.access_token
$adminHeaders = @{ "Authorization" = "Bearer $adminToken" }
Write-Host "Success: Admin logged in" -ForegroundColor Green

# Get patient list
Write-Host "`nStep 5: Getting appointments to find patient ID" -ForegroundColor Yellow
$allAppointments = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/appointments" -Headers $adminHeaders
if ($allAppointments.appointments.Count -gt 0) {
    $patientId = $allAppointments.appointments[0].patient_id
    Write-Host "Success: Using Patient ID: $patientId" -ForegroundColor Green
    
    # Book appointment for patient as admin
    Write-Host "`nStep 6: Admin booking appointment for patient" -ForegroundColor Yellow
    $adminAppointmentBody = @{
        patient_id = $patientId
        doctor_id = $doctorId
        appointment_date = $tomorrow
        appointment_time = "14:00"
        reason = "Admin-created appointment"
    } | ConvertTo-Json
    
    try {
        $adminAppointment = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/appointments" -Method POST -Headers $adminHeaders -Body $adminAppointmentBody -ContentType "application/json"
        Write-Host "SUCCESS: Admin booked appointment for patient!" -ForegroundColor Green
        Write-Host "  Appointment ID: $($adminAppointment.id)" -ForegroundColor White
        Write-Host "  Patient ID: $($adminAppointment.patient_id)" -ForegroundColor White
        Write-Host "  Date: $($adminAppointment.appointment_date)" -ForegroundColor White
    } catch {
        Write-Host "FAILED: Admin booking failed!" -ForegroundColor Red
        Write-Host "Error: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "Warning: No existing appointments to get patient ID from" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================================"
Write-Host " TEST COMPLETED"
Write-Host "================================================================================"
