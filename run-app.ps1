# Start Healthcare Management Platform
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Healthcare Management Platform            ║" -ForegroundColor Cyan
Write-Host "║  Node.js + PostgreSQL + React              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Stop any existing node processes
Write-Host "🔄 Stopping existing processes..." -ForegroundColor Yellow
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Check if PostgreSQL is running
Write-Host "🔍 Checking PostgreSQL..." -ForegroundColor Yellow
$pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
if ($null -eq $pgService -or $pgService.Status -ne "Running") {
    Write-Host "❌ PostgreSQL is not running!" -ForegroundColor Red
    Write-Host "   Please start PostgreSQL service and try again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   To start PostgreSQL:" -ForegroundColor Cyan
    Write-Host "   1. Open Services (services.msc)" -ForegroundColor White
    Write-Host "   2. Find 'postgresql' service" -ForegroundColor White
    Write-Host "   3. Click 'Start'" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✅ PostgreSQL is running" -ForegroundColor Green

# Start Backend
Write-Host ""
Write-Host "🚀 Starting Backend Server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd 'c:\Users\tejas\friendlyhealthy\friendlyhealthy\server'
Write-Host '================================================' -ForegroundColor Cyan
Write-Host 'BACKEND SERVER' -ForegroundColor Green
Write-Host '================================================' -ForegroundColor Cyan
npm run dev
"@

Start-Sleep -Seconds 5

# Test backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Backend is running on http://localhost:5000" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend might still be starting..." -ForegroundColor Yellow
}

# Start Frontend
Write-Host ""
Write-Host "🎨 Starting Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
cd 'c:\Users\tejas\friendlyhealthy\friendlyhealthy\frontend'
Write-Host '================================================' -ForegroundColor Cyan
Write-Host 'FRONTEND DEV SERVER' -ForegroundColor Green
Write-Host '================================================' -ForegroundColor Cyan
npm run dev
"@

Write-Host ""
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         APPLICATION STARTING...            ║" -ForegroundColor Green
Write-Host "╠════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  Backend:  http://localhost:5000           ║" -ForegroundColor White
Write-Host "║  Frontend: http://localhost:3000           ║" -ForegroundColor White
Write-Host "║  Health:   http://localhost:5000/health    ║" -ForegroundColor White
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Opening browser in 10 seconds..." -ForegroundColor Yellow
Write-Host "   (Press Ctrl+C to cancel)" -ForegroundColor Gray
Start-Sleep -Seconds 10

Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "✅ Application started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "   - Register a new account to get started" -ForegroundColor White
Write-Host "   - Password must contain: uppercase, lowercase, number, special char" -ForegroundColor White
Write-Host "   - Example: Test@123" -ForegroundColor White
Write-Host ""
