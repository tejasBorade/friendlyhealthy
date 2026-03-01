# Start All Services for Email Notifications
# This starts Redis, Backend, and Celery Worker+Beat

Write-Host "=== Starting Healthcare Platform Services ===" -ForegroundColor Cyan
Write-Host ""

# Check if Redis is already running
$redisRunning = $false
try {
    $test = Test-NetConnection -ComputerName localhost -Port 6379 -WarningAction SilentlyContinue
    if ($test.TcpTestSucceeded) {
        Write-Host "Redis is already running on port 6379" -ForegroundColor Green
        $redisRunning = $true
    }
} catch {
    $redisRunning = $false
}

if (-not $redisRunning) {
    Write-Host "Starting Redis..." -ForegroundColor Yellow
    
    # Check if redis-server.exe exists
    if (Test-Path "redis\redis-server.exe") {
        Start-Process -FilePath "$PSScriptRoot\redis\redis-server.exe" -WindowStyle Minimized
        Write-Host "Started Redis server" -ForegroundColor Green
        Start-Sleep -Seconds 2
    } else {
        Write-Host "ERROR: Redis not found. Run .\install-redis-windows.ps1 first" -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host ""
Write-Host "Starting services in separate windows..." -ForegroundColor Cyan
Write-Host ""

# Function to start service in new window
function Start-Service {
    param([string]$Title, [string]$Command)
    $venvPath = Resolve-Path "$PSScriptRoot\..\.venv\Scripts\Activate.ps1"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$venvPath'; cd '$PSScriptRoot'; Write-Host '=== $Title ===' -ForegroundColor Green; $Command"
}

# Start Backend
Start-Service -Title "Backend API (Port 8000)" -Command "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
Write-Host "Started Backend API (http://localhost:8000)" -ForegroundColor Green
Start-Sleep -Seconds 1

# Start Celery Worker (Windows requires separate processes)
Start-Service -Title "Celery Worker (Email Tasks)" -Command "python -m celery -A app.services.celery_tasks.celery_app worker --loglevel=info --pool=solo"
Write-Host "Started Celery Worker (Email notifications active)" -ForegroundColor Green
Start-Sleep -Seconds 1

# Start Celery Beat (Scheduler for reminders)
Start-Service -Title "Celery Beat (Task Scheduler)" -Command "python -m celery -A app.services.celery_tasks.celery_app beat --loglevel=info"
Write-Host "Started Celery Beat (Appointment reminders scheduled)" -ForegroundColor Green

Write-Host ""
Write-Host "=== All Services Started! ===" -ForegroundColor Green
Write-Host ""
Write-Host "  Redis:  Running" -ForegroundColor White
Write-Host "  Backend: http://localhost:8000" -ForegroundColor White
Write-Host "  Celery Worker:  Processing email tasks" -ForegroundColor White
Write-Host "  Celery Beat:    Scheduling reminders (9 AM daily)" -ForegroundColor White
Write-Host ""
Write-Host "Email notifications are now active!" -ForegroundColor Cyan
Write-Host "Test by booking an appointment or updating status" -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop: Close the PowerShell windows" -ForegroundColor Gray
Write-Host ""
pause
