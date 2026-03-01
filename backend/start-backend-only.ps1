# Start Backend Only (No Redis/Celery)
# Use this if you want to test the API without email notifications

Write-Host "=== Starting Backend API Only ===" -ForegroundColor Cyan
Write-Host "Note: Email notifications will be logged but not sent (no Celery)" -ForegroundColor Yellow
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠ Warning: .env not found" -ForegroundColor Yellow
    Write-Host "Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created .env file" -ForegroundColor Green
    Write-Host ""
    Write-Host "Please edit .env and add your Gmail credentials if you want email notifications later" -ForegroundColor Cyan
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "$PSScriptRoot\..\.venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Starting FastAPI backend on http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
