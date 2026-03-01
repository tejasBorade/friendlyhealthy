# Start Email Notification Services
# This script starts Redis, Backend, Celery Worker, and Celery Beat

Write-Host "=== Healthcare Platform - Email Notification Services ===" -ForegroundColor Cyan
Write-Host ""

# Check if Redis is running
Write-Host "Checking Redis..." -ForegroundColor Yellow
$redisRunning = $false
try {
    $redisTest = redis-cli ping 2>$null
    if ($redisTest -eq "PONG") {
        Write-Host "✓ Redis is already running" -ForegroundColor Green
        $redisRunning = $true
    }
} catch {
    Write-Host "✗ Redis is not running" -ForegroundColor Red
}

if (-not $redisRunning) {
    Write-Host ""
    Write-Host "Starting Redis with Docker..." -ForegroundColor Yellow
    
    # Check if redis container exists
    $redisContainer = docker ps -a --filter "name=redis" --format "{{.Names}}" 2>$null
    
    if ($redisContainer -eq "redis") {
        # Container exists, start it
        docker start redis
        Write-Host "✓ Started existing Redis container" -ForegroundColor Green
    } else {
        # Create new container
        docker run -d -p 6379:6379 --name redis redis:latest
        Write-Host "✓ Created and started new Redis container" -ForegroundColor Green
    }
    
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "=== Services Starting ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "2. Celery Worker: Processing email tasks" -ForegroundColor White
Write-Host "3. Celery Beat: Scheduling appointment reminders (9 AM daily)" -ForegroundColor White
Write-Host ""

# Function to start a process in a new window
function Start-ServiceWindow {
    param(
        [string]$Title,
        [string]$Command,
        [string]$WorkingDir = (Get-Location)
    )
    
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "Write-Host '=== $Title ===' -ForegroundColor Green; cd '$WorkingDir'; & .venv\Scripts\Activate.ps1; $Command"
    )
}

# Check if virtual environment exists
if (-not (Test-Path "backend\.venv\Scripts\Activate.ps1")) {
    Write-Host "✗ Virtual environment not found in backend\.venv" -ForegroundColor Red
    Write-Host "Please create it first: cd backend; python -m venv .venv; .venv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
    pause
    exit 1
}

# Check if .env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠ Warning: backend\.env not found" -ForegroundColor Yellow
    Write-Host "Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "✓ Created .env file" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠ IMPORTANT: Edit backend\.env and add your Gmail credentials:" -ForegroundColor Red
    Write-Host "   EMAIL_FROM=your-email@gmail.com" -ForegroundColor White
    Write-Host "   EMAIL_PASSWORD=your-gmail-app-password" -ForegroundColor White
    Write-Host ""
    Write-Host "See EMAIL_QUICK_START.md for instructions" -ForegroundColor Cyan
    Write-Host ""
    $continue = Read-Host "Have you configured Gmail credentials? (y/n)"
    if ($continue -ne "y") {
        Write-Host "Please configure .env first, then run this script again" -ForegroundColor Yellow
        pause
        exit 0
    }
}

Write-Host "Starting services in separate windows..." -ForegroundColor Yellow
Start-Sleep -Seconds 1

# Start Backend
Start-ServiceWindow -Title "Backend API (Port 8000)" `
    -Command "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" `
    -WorkingDir "$PSScriptRoot\backend"
Write-Host "✓ Started Backend API" -ForegroundColor Green
Start-Sleep -Seconds 2

# Start Celery Worker + Beat (combined)
Start-ServiceWindow -Title "Celery Worker & Beat (Email Tasks)" `
    -Command "celery -A app.services.celery_tasks.celery_app worker --beat --loglevel=info --pool=solo" `
    -WorkingDir "$PSScriptRoot\backend"
Write-Host "✓ Started Celery Worker + Beat" -ForegroundColor Green
Start-Sleep -Seconds 1

Write-Host ""
Write-Host "=== All Services Started! ===" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Redis:         Running (Docker container)" -ForegroundColor White
Write-Host "✅ Backend:       http://localhost:8000" -ForegroundColor White
Write-Host "✅ Celery Worker: Processing email notifications" -ForegroundColor White
Write-Host "✅ Celery Beat:   Scheduling appointment reminders" -ForegroundColor White
Write-Host ""
Write-Host "📧 Email notifications are now active!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test by:" -ForegroundColor Yellow
Write-Host "  1. Booking an appointment (patient receives confirmation)" -ForegroundColor White
Write-Host "  2. Updating appointment status (patient receives status update)" -ForegroundColor White
Write-Host "  3. Creating a prescription (patient receives notification)" -ForegroundColor White
Write-Host "  4. Appointment tomorrow (auto-reminder at 9 AM)" -ForegroundColor White
Write-Host ""
Write-Host "To stop services: Close each PowerShell window or press Ctrl+C" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit this launcher..." -ForegroundColor Gray
pause
