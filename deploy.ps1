# Healthcare Platform - Quick Deploy Script for Windows

Write-Host "🚀 Healthcare Platform Deployment" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""

# Check if Railway CLI is installed
if (!(Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "Railway CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g @railway/cli
}

# Check if Wrangler is installed
if (!(Get-Command wrangler -ErrorAction SilentlyContinue)) {
    Write-Host "Wrangler CLI not found. Installing..." -ForegroundColor Yellow
    npm install -g wrangler
}

Write-Host ""
Write-Host "📋 Deployment Options:"
Write-Host "1. Deploy Backend to Railway"
Write-Host "2. Deploy Frontend to Cloudflare Pages"
Write-Host "3. Deploy Both (Full Stack)"
Write-Host "4. Deploy to Render (Manual)"
Write-Host ""

$option = Read-Host "Select option (1-4)"

switch ($option) {
    1 {
        Write-Host "🚀 Deploying Backend to Railway..." -ForegroundColor Green
        Set-Location backend
        railway login
        railway init
        railway add
        railway up
        Write-Host "✅ Backend deployed!" -ForegroundColor Green
        railway open
        Set-Location ..
    }
    2 {
        Write-Host "🚀 Deploying Frontend to Cloudflare Pages..." -ForegroundColor Green
        Set-Location frontend
        
        # Ask for backend URL
        $backend_url = Read-Host "Enter your backend API URL"
        "VITE_API_URL=$backend_url/api/v1" | Out-File -FilePath .env.production -Encoding utf8
        
        # Build
        npm install
        npm run build
        
        # Deploy
        wrangler pages deploy dist --project-name=friendlyhealthy
        Write-Host "✅ Frontend deployed!" -ForegroundColor Green
        Set-Location ..
    }
    3 {
        Write-Host "🚀 Deploying Full Stack..." -ForegroundColor Green
        
        # Deploy Backend first
        Write-Host "Step 1: Deploying Backend to Railway..."
        Set-Location backend
        railway login
        railway init
        railway add
        railway up
        $backend_url = railway domain
        Set-Location ..
        
        # Deploy Frontend
        Write-Host "Step 2: Deploying Frontend to Cloudflare Pages..."
        Set-Location frontend
        "VITE_API_URL=$backend_url/api/v1" | Out-File -FilePath .env.production -Encoding utf8
        npm install
        npm run build
        wrangler pages deploy dist --project-name=friendlyhealthy
        Set-Location ..
        
        Write-Host "✅ Full stack deployed!" -ForegroundColor Green
        Write-Host "Backend: $backend_url" -ForegroundColor Green
        Write-Host "Frontend: Check Cloudflare Pages dashboard" -ForegroundColor Green
    }
    4 {
        Write-Host "🚀 Deploying to Render..." -ForegroundColor Green
        Write-Host "Please follow these steps:"
        Write-Host "1. Go to https://render.com"
        Write-Host "2. New → Web Service"
        Write-Host "3. Connect GitHub: tejasBorade/friendlyhealthy"
        Write-Host "4. Build Command: cd backend && pip install -r requirements.txt"
        Write-Host "5. Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port `$PORT"
        Write-Host "6. Add PostgreSQL database"
        Start-Process "https://render.com"
    }
    default {
        Write-Host "Invalid option" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Set environment variables in your hosting platform"
Write-Host "2. Run database migrations"
Write-Host "3. Test your deployment"
Write-Host "4. Configure custom domain (optional)"
Write-Host ""
Write-Host "Need help? Check CLOUDFLARE_DEPLOYMENT.md"
