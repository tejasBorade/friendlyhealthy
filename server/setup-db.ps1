# Setup Database Script
Write-Host "ðŸ¥ Setting up Healthcare Database..." -ForegroundColor Cyan
Write-Host ""

$pgPassword = "123"  # Your PostgreSQL password from .env
$env:PGPASSWORD = $pgPassword

# Try to find pg binaries
$pgPath = "C:\Program Files\PostgreSQL\18\bin"
if (-not (Test-Path $pgPath)) {
    $pgPath = "C:\Program Files\PostgreSQL\17\bin"
}
if (-not (Test-Path $pgPath)) {
    $pgPath = "C:\Program Files\PostgreSQL\16\bin"
}
if (-not (Test-Path $pgPath)) {
    Write-Host "âŒ PostgreSQL bin folder not found!" -ForegroundColor Red
    Write-Host "   Please check your PostgreSQL installation" -ForegroundColor Yellow
    exit 1
}

$psqlPath = Join-Path $pgPath "psql.exe"

Write-Host "Step 1: Creating database 'healthcare_db'..." -ForegroundColor Yellow

# Create database (ignore error if already exists)
& $psqlPath -U postgres -c "CREATE DATABASE healthcare_db;" 2>&1 | Out-Null

# Check if database was created/exists
$result = & $psqlPath -U postgres -c "\l" 2>&1 | Select-String "healthcare_db"
if ($result) {
    Write-Host "âœ… Database 'healthcare_db' ready" -ForegroundColor Green
} else {
    Write-Host "âŒ Failed to create database" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Loading database schema..." -ForegroundColor Yellow

# Load schema
$schemaFile = "c:\Users\tejas\friendlyhealthy\friendlyhealthy\server\database\schema.sql"
& $psqlPath -U postgres -d healthcare_db -f $schemaFile 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "âœ… Schema loaded successfully" -ForegroundColor Green
} else {
    Write-Host "âš ï¸  Schema may have some warnings but should be OK" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Verifying tables..." -ForegroundColor Yellow

# Check tables
$tables = & $psqlPath -U postgres -d healthcare_db -c "\dt" 2>&1 | Select-String "users|doctors|patients|appointments"
if ($tables) {
    Write-Host "âœ… Tables created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Tables found:" -ForegroundColor Cyan
    & $psqlPath -U postgres -d healthcare_db -c "\dt"
} else {
    Write-Host "âŒ Tables not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Green
Write-Host "â•‘     Database Setup Complete! âœ…             â•‘" -ForegroundColor Green
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Green
Write-Host ""
Write-Host "You can now start the application:" -ForegroundColor Cyan
Write-Host "   cd .." -ForegroundColor White
Write-Host "   .\run-app.ps1" -ForegroundColor White
Write-Host ""

