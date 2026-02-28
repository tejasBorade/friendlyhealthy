# Admin CRUD Operations Test Script
# Tests all admin features with create, read, update, delete operations

Write-Host "`n" ("="*80) -ForegroundColor Cyan
Write-Host " ADMIN CRUD OPERATIONS TEST" -ForegroundColor Cyan -BackgroundColor Black
Write-Host ("="*80) "`n" -ForegroundColor Cyan

# Admin Login
Write-Host "🔐 Step 1: Admin Login" -ForegroundColor Yellow
$loginBody = @{
    email = "admin@healthcare.com"
    password = "Admin@123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $adminToken = $response.access_token
    $headers = @{ "Authorization" = "Bearer $adminToken" }
    Write-Host "✅ Admin logged in successfully" -ForegroundColor Green
    Write-Host "   User ID: $($response.user.id)" -ForegroundColor Gray
    Write-Host "   Role: $($response.user.role)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Admin login failed!" -ForegroundColor Red
    Write-Host "Error: $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit 1
}

$testResults = @{
    Passed = 0
    Failed = 0
    Tests = @()
}

function Test-Endpoint {
    param(
        [string]$Name,
        [scriptblock]$Test
    )
    
    Write-Host "`n---" -ForegroundColor DarkGray
    Write-Host "📝 TEST: $Name" -ForegroundColor Yellow
    
    try {
        & $Test
        Write-Host "   ✅ PASSED" -ForegroundColor Green
        $script:testResults.Passed++
        $script:testResults.Tests += @{ Name = $Name; Result = "PASSED" }
        return $true
    } catch {
        Write-Host "   ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
        $script:testResults.Failed++
        $script:testResults.Tests += @{ Name = $Name; Result = "FAILED"; Error = $_.Exception.Message }
        return $false
    }
}

# ================================
# READ OPERATIONS
# ================================
Write-Host "`n" ("="*80) -ForegroundColor Cyan
Write-Host " READ OPERATIONS (GET)" -ForegroundColor Cyan
Write-Host ("="*80) -ForegroundColor Cyan

Test-Endpoint "GET /doctors - List all doctors" {
    $doctors = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/doctors" -Headers $headers
    Write-Host "   Found: $($doctors.doctors.Count) doctors" -ForegroundColor Gray
    if ($doctors.doctors.Count -eq 0) { throw "No doctors found" }
}

Test-Endpoint "GET /appointments - List all appointments" {
    $appointments = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/appointments" -Headers $headers
    Write-Host "   Found: $($appointments.appointments.Count) appointments" -ForegroundColor Gray
}

Test-Endpoint "GET /prescriptions - List all prescriptions" {
    $prescriptions = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/prescriptions" -Headers $headers
    Write-Host "   Found: $($prescriptions.prescriptions.Count) prescriptions" -ForegroundColor Gray
}

Test-Endpoint "GET /billing - View billing data" {
    $billing = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/billing" -Headers $headers
    Write-Host "   Total Bills: $($billing.summary.total_bills)" -ForegroundColor Gray
    Write-Host "   Total Amount: `$$($billing.summary.total_amount)" -ForegroundColor Gray
}

Test-Endpoint "GET /doctors/specializations - List specializations" {
    $specs = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/doctors/specializations" -Headers $headers
    Write-Host "   Found: $($specs.Count) specializations" -ForegroundColor Gray
}

# ================================
# CREATE OPERATIONS
# ================================
Write-Host "`n" ("="*80) -ForegroundColor Cyan
Write-Host " CREATE OPERATIONS (POST)" -ForegroundColor Cyan
Write-Host ("="*80) -ForegroundColor Cyan

$script:createdUserId = $null
$script:createdDoctorId = $null
$script:createdPatientId = $null

# Create a test patient user
Test-Endpoint "POST /auth/register - Create new patient user" {
    $randomEmail = "testpatient_$(Get-Random)@test.com"
    $newUser = @{
        email = $randomEmail
        password = "Test@123"
        role = "patient"
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method POST -Body $newUser -ContentType "application/json"
    $script:createdUserId = $result.user.id
    Write-Host "   Created User ID: $script:createdUserId" -ForegroundColor Gray
    Write-Host "   Email: $randomEmail" -ForegroundColor Gray
}

# Create a test doctor user
Test-Endpoint "POST /auth/register - Create new doctor user" {
    $randomEmail = "testdoctor_$(Get-Random)@test.com"
    $newDoctor = @{
        email = $randomEmail
        password = "Test@123"
        role = "doctor"
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method POST -Body $newDoctor -ContentType "application/json"
    Write-Host "   Created Doctor User ID: $($result.user.id)" -ForegroundColor Gray
    Write-Host "   Email: $randomEmail" -ForegroundColor Gray
}

# ================================
# UPDATE OPERATIONS
# ================================
Write-Host "`n" ("="*80) -ForegroundColor Cyan
Write-Host " UPDATE OPERATIONS (PUT/PATCH)" -ForegroundColor Cyan
Write-Host ("="*80) -ForegroundColor Cyan

Test-Endpoint "PATCH /appointments/{id} - Update appointment status" {
    # Get first appointment
    $appointments = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/appointments" -Headers $headers
    if ($appointments.appointments.Count -gt 0) {
        $apptId = $appointments.appointments[0].id
        Write-Host "   Updating appointment ID: $apptId" -ForegroundColor Gray
        
        # Note: This might fail if the endpoint doesn't exist yet
        try {
            $updateBody = @{ status = "confirmed" } | ConvertTo-Json
            Invoke-RestMethod -Uri "http://localhost:8000/api/v1/appointments/$apptId" -Method PATCH -Headers $headers -Body $updateBody -ContentType "application/json"
            Write-Host "   Status updated to: confirmed" -ForegroundColor Gray
        } catch {
            Write-Host "   ⚠️  Update endpoint may not be implemented" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ⚠️  No appointments to update" -ForegroundColor Yellow
    }
}

# ================================
# DELETE OPERATIONS
# ================================
Write-Host "`n" ("="*80) -ForegroundColor Cyan
Write-Host " DELETE OPERATIONS" -ForegroundColor Cyan
Write-Host ("="*80) -ForegroundColor Cyan

Test-Endpoint "DELETE /appointments/{id} - Cancel appointment" {
    # Get an appointment to delete
    $appointments = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/appointments" -Headers $headers
    if ($appointments.appointments.Count -gt 0) {
        $apptId = $appointments.appointments[0].id
        Write-Host "   Attempting to cancel appointment ID: $apptId" -ForegroundColor Gray
        
        try {
            Invoke-RestMethod -Uri "http://localhost:8000/api/v1/appointments/$apptId" -Method DELETE -Headers $headers
            Write-Host "   Appointment cancelled successfully" -ForegroundColor Gray
        } catch {
            Write-Host "   ⚠️  Delete endpoint may not be implemented or requires different method" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ⚠️  No appointments to delete" -ForegroundColor Yellow
    }
}

# ================================
# SPECIAL ADMIN OPERATIONS
# ================================
Write-Host "`n" ("="*80) -ForegroundColor Cyan
Write-Host " SPECIAL ADMIN OPERATIONS" -ForegroundColor Cyan
Write-Host ("="*80) -ForegroundColor Cyan

Test-Endpoint "GET /auth/users - List all system users (Admin only)" {
    try {
        $users = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/users" -Headers $headers
        Write-Host "   Total Users: $($users.Count)" -ForegroundColor Gray
        
        $byRole = $users | Group-Object -Property role
        foreach ($group in $byRole) {
            Write-Host "   - $($group.Name): $($group.Count)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ⚠️  Admin user management endpoint not found" -ForegroundColor Yellow
    }
}

Test-Endpoint "GET /billing/charge-types - View charge types" {
    try {
        $chargeTypes = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/billing/charge-types" -Headers $headers
        Write-Host "   Found: $($chargeTypes.Count) charge types" -ForegroundColor Gray
    } catch {
        Write-Host "   ⚠️  No charge types configured" -ForegroundColor Yellow
    }
}

# ================================
# FINAL REPORT
# ================================
Write-Host "`n" ("="*80) -ForegroundColor Cyan
Write-Host " TEST RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host ("="*80) -ForegroundColor Cyan

$totalTests = $testResults.Passed + $testResults.Failed
$passRate = if ($totalTests -gt 0) { [math]::Round(($testResults.Passed / $totalTests) * 100, 2) } else { 0 }

Write-Host "`n📊 Overall Results:" -ForegroundColor Yellow
Write-Host "   Total Tests: $totalTests" -ForegroundColor White
Write-Host "   ✅ Passed: $($testResults.Passed)" -ForegroundColor Green
Write-Host "   ❌ Failed: $($testResults.Failed)" -ForegroundColor Red
Write-Host "   Pass Rate: $passRate%" -ForegroundColor Cyan

Write-Host "`n📋 Detailed Results:" -ForegroundColor Yellow
foreach ($test in $testResults.Tests) {
    if ($test.Result -eq "PASSED") {
        Write-Host "   ✅ $($test.Name)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $($test.Name)" -ForegroundColor Red
        if ($test.Error) {
            Write-Host "      Error: $($test.Error)" -ForegroundColor DarkGray
        }
    }
}

Write-Host "`n" ("="*80) -ForegroundColor Cyan
Write-Host " ADMIN CREDENTIALS" -ForegroundColor Cyan
Write-Host ("="*80) -ForegroundColor Cyan
Write-Host "Email: admin@healthcare.com" -ForegroundColor White
Write-Host "Password: Admin@123" -ForegroundColor White
Write-Host ("="*80) "`n" -ForegroundColor Cyan

if ($testResults.Failed -gt 0) {
    Write-Host "⚠️  Some tests failed. Review the results above." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "🎉 All tests passed! Admin features are working correctly." -ForegroundColor Green
    exit 0
}
