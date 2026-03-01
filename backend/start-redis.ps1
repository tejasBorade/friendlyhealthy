# Start Redis Server
Write-Host "Starting Redis server..." -ForegroundColor Cyan
Set-Location "$PSScriptRoot\redis"
Start-Process -FilePath ".\redis-server.exe" -NoNewWindow
Write-Host "Redis server started on port 6379" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Wait-Process -Name "redis-server"
