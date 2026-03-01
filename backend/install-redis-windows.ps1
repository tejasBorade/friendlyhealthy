# Install Redis on Windows (without Docker)
# This script downloads and sets up Redis for Windows

Write-Host "=== Redis Installation for Windows ===" -ForegroundColor Cyan
Write-Host ""

$redisUrl = "https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip"
$redisZip = "$env:TEMP\redis.zip"
$redisDir = "$PSScriptRoot\redis"

Write-Host "Option 1: Installing Redis locally in backend folder..." -ForegroundColor Yellow
Write-Host ""

try {
    # Download Redis
    Write-Host "Downloading Redis for Windows..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $redisUrl -OutFile $redisZip -UseBasicParsing
    
    # Extract
    Write-Host "Extracting Redis..." -ForegroundColor Cyan
    Expand-Archive -Path $redisZip -DestinationPath $redisDir -Force
    
    # Clean up
    Remove-Item $redisZip
    
    Write-Host "Success! Redis installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start Redis, run:" -ForegroundColor Yellow
    Write-Host "  cd backend\redis" -ForegroundColor White
    Write-Host "  .\redis-server.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "Or use the start-redis.ps1 script created..." -ForegroundColor Gray
    
    # Create start script
    $startScriptContent = @"
# Start Redis Server
Write-Host "Starting Redis server..." -ForegroundColor Cyan
Set-Location "`$PSScriptRoot\redis"
Start-Process -FilePath ".\redis-server.exe" -NoNewWindow
Write-Host "Redis server started on port 6379" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Wait-Process -Name "redis-server"
"@
    
    $startScriptContent | Out-File -FilePath "$PSScriptRoot\start-redis.ps1" -Encoding UTF8 -Force
    Write-Host "Created start-redis.ps1 script" -ForegroundColor Green
    
} catch {
    Write-Host "Failed to download/install Redis" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative Options:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Option 2: Install Memurai (Redis alternative for Windows)" -ForegroundColor Cyan
    Write-Host "  Download from: https://www.memurai.com/get-memurai" -ForegroundColor White
    Write-Host "  Or with Chocolatey: choco install memurai-developer" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 3: Use Windows Subsystem for Linux (WSL)" -ForegroundColor Cyan
    Write-Host "  wsl --install" -ForegroundColor White
    Write-Host "  sudo apt install redis-server" -ForegroundColor White
    Write-Host "  sudo service redis-server start" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 4: Test without Redis (emails only, no background tasks)" -ForegroundColor Cyan
    Write-Host "  Set EMAIL_ENABLED=False in .env and test directly" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
