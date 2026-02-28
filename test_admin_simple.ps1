# Admin CRUD Operations Test Script
Write-Host "================================================================================"
Write-Host " ADMIN CRUD OPERATIONS TEST"
Write-Host "================================================================================"

# Admin Login
Write-Host "`nStep 1: Admin Login" -ForegroundColor Yellow
$loginBody = @{
    email = "admin@healthcare.com"
    password = "Admin@123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $adminToken = $response.access_token
    $headers = @{ "Authorization" = "Bearer $adminToken" }
    Write-Host "Success: Admin logged in successfully" -ForegroundColor Green
    Write-Host "User ID: $($response.user.id)"
    Write-Host "Role: $($response.user.role)"
} catch {
    Write-Host "FAILED: Admin login failed!" -ForegroundColor Red
    Write-Host "Error: $($_.ErrorDetails.Message)"
    exit 1
}

# READ OPERATIONS
Write-Host "`n================================================================================"
Write-Host " READ OPERATIONS (GET)"
Write-Host "================================================================================"

Write-Host "`nTest 1: GET /doctors" -ForegroundColor Yellow
try {
    $doctors = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/doctors" -Headers $headers
    Write-Host "Success: Found $($doctors.doctors.Count) doctors" -ForegroundColor Green
} catch {
    Write-Host "FAILED" -ForegroundColor Red
}

Write-Host "`nTest 2: GET /appointments" -ForegroundColor Yellow
try {
    $appointments = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/appointments" -Headers $headers
    Write-Host "Success: Found $($appointments.appointments.Count) appointments" -ForegroundColor Green
} catch {
    Write-Host "FAILED" -ForegroundColor Red
}

Write-Host "`nTest 3: GET /prescriptions" -ForegroundColor Yellow
try {
    $prescriptions = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/prescriptions" -Headers $headers
    Write-Host "Success: Found $($prescriptions.prescriptions.Count) prescriptions" -ForegroundColor Green
} catch {
    Write-Host "FAILED" -ForegroundColor Red
}

Write-Host "`nTest 4: GET /billing" -ForegroundColor Yellow
try {
    $billing = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/billing" -Headers $headers
    Write-Host "Success: Total Bills=$($billing.summary.total_bills), Amount=$($billing.summary.total_amount)" -ForegroundColor Green
} catch {
    Write-Host "FAILED" -ForegroundColor Red
}

Write-Host "`nTest 5: GET /doctors/specializations" -ForegroundColor Yellow
try {
    $specs = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/doctors/specializations" -Headers $headers
    Write-Host "Success: Found $($specs.Count) specializations" -ForegroundColor Green
} catch {
    Write-Host "FAILED" -ForegroundColor Red
}

# CREATE OPERATIONS
Write-Host "`n================================================================================"
Write-Host " CREATE OPERATIONS (POST)"
Write-Host "================================================================================"

Write-Host "`nTest 6: POST /auth/register - Create new patient" -ForegroundColor Yellow
try {
    $randomEmail = "testpatient_$(Get-Random)@test.com"
    $newUser = @{
        email = $randomEmail
        password = "Test@123"
        role = "patient"
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method POST -Body $newUser -ContentType "application/json"
    Write-Host "Success: Created user $randomEmail with ID $($result.user.id)" -ForegroundColor Green
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nTest 7: POST /auth/register - Create new doctor" -ForegroundColor Yellow
try {
    $randomEmail = "testdoctor_$(Get-Random)@test.com"
    $newDoctor = @{
        email = $randomEmail
        password = "Test@123"
        role = "doctor"
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method POST -Body $newDoctor -ContentType "application/json"
    Write-Host "Success: Created doctor $randomEmail with ID $($result.user.id)" -ForegroundColor Green
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# SPECIAL ADMIN OPERATIONS
Write-Host "`n================================================================================"
Write-Host " SPECIAL ADMIN OPERATIONS"
Write-Host "================================================================================"

Write-Host "`nTest 8: GET /auth/users - List all users (Admin only)" -ForegroundColor Yellow
try {
    $users = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/users" -Headers $headers
    Write-Host "Success: Found $($users.Count) total users" -ForegroundColor Green
    $byRole = $users | Group-Object -Property role
    foreach ($group in $byRole) {
        Write-Host "  - $($group.Name): $($group.Count) users"
    }
} catch {
    Write-Host "WARNING: Admin user management endpoint not implemented" -ForegroundColor Yellow
}

Write-Host "`nTest 9: GET /billing/charge-types" -ForegroundColor Yellow
try {
    $chargeTypes = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/billing/charge-types" -Headers $headers
    Write-Host "Success: Found $($chargeTypes.Count) charge types" -ForegroundColor Green
} catch {
    Write-Host "WARNING: No charge types found" -ForegroundColor Yellow
}

Write-Host "`n================================================================================"
Write-Host " TEST COMPLETED"
Write-Host "================================================================================"
Write-Host "`nAdmin Credentials:"
Write-Host "Email: admin@healthcare.com"
Write-Host "Password: Admin@123"
Write-Host "================================================================================"
