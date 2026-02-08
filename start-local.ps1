# Start local development servers
Write-Host "Starting Healthcare Platform locally..." -ForegroundColor Green

# Kill any existing node processes
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\tejas\friendlyhealthy\friendlyhealthy\cloudflare-backend'; Write-Host 'Starting Backend on http://127.0.0.1:8787' -ForegroundColor Cyan; npx wrangler dev --local --port 8787"

# Wait for backend to start
Start-Sleep -Seconds 5

# Start frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\tejas\friendlyhealthy\friendlyhealthy\frontend'; Write-Host 'Starting Frontend on http://localhost:3000' -ForegroundColor Cyan; npm run dev"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Servers are starting..." -ForegroundColor Yellow
Write-Host "Backend:  http://127.0.0.1:8787" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Opening browser in 8 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 8
Start-Process "http://localhost:3000"
