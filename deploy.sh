#!/bin/bash

# Healthcare Platform - Quick Deploy Script

echo "🚀 Healthcare Platform Deployment"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}Railway CLI not found. Installing...${NC}"
    npm install -g @railway/cli
fi

# Check if Wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo -e "${YELLOW}Wrangler CLI not found. Installing...${NC}"
    npm install -g wrangler
fi

echo ""
echo "📋 Deployment Options:"
echo "1. Deploy Backend to Railway"
echo "2. Deploy Frontend to Cloudflare Pages"
echo "3. Deploy Both (Full Stack)"
echo "4. Deploy to Render"
echo "5. Deploy to Heroku"
echo ""
read -p "Select option (1-5): " option

case $option in
    1)
        echo -e "${GREEN}🚀 Deploying Backend to Railway...${NC}"
        cd backend
        railway login
        railway init
        railway add postgresql
        railway up
        echo -e "${GREEN}✅ Backend deployed!${NC}"
        railway open
        ;;
    2)
        echo -e "${GREEN}🚀 Deploying Frontend to Cloudflare Pages...${NC}"
        cd frontend
        
        # Ask for backend URL
        read -p "Enter your backend API URL: " backend_url
        echo "VITE_API_URL=$backend_url/api/v1" > .env.production
        
        # Build
        npm install
        npm run build
        
        # Deploy
        wrangler pages deploy dist --project-name=friendlyhealthy
        echo -e "${GREEN}✅ Frontend deployed!${NC}"
        ;;
    3)
        echo -e "${GREEN}🚀 Deploying Full Stack...${NC}"
        
        # Deploy Backend first
        echo "Step 1: Deploying Backend to Railway..."
        cd backend
        railway login
        railway init
        railway add postgresql
        railway up
        backend_url=$(railway domain)
        cd ..
        
        # Deploy Frontend
        echo "Step 2: Deploying Frontend to Cloudflare Pages..."
        cd frontend
        echo "VITE_API_URL=$backend_url/api/v1" > .env.production
        npm install
        npm run build
        wrangler pages deploy dist --project-name=friendlyhealthy
        cd ..
        
        echo -e "${GREEN}✅ Full stack deployed!${NC}"
        echo -e "${GREEN}Backend: $backend_url${NC}"
        echo -e "${GREEN}Frontend: Check Cloudflare Pages dashboard${NC}"
        ;;
    4)
        echo -e "${GREEN}🚀 Deploying to Render...${NC}"
        echo "Please follow these steps:"
        echo "1. Go to https://render.com"
        echo "2. New → Web Service"
        echo "3. Connect GitHub: tejasBorade/friendlyhealthy"
        echo "4. Build Command: cd backend && pip install -r requirements.txt"
        echo "5. Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
        echo "6. Add PostgreSQL database"
        ;;
    5)
        echo -e "${GREEN}🚀 Deploying to Heroku...${NC}"
        
        # Check if Heroku CLI is installed
        if ! command -v heroku &> /dev/null; then
            echo -e "${RED}Heroku CLI not found. Please install from: https://devcenter.heroku.com/articles/heroku-cli${NC}"
            exit 1
        fi
        
        heroku login
        heroku create friendlyhealthy-api
        heroku addons:create heroku-postgresql:essential-0
        
        # Set environment variables
        echo "Setting environment variables..."
        heroku config:set SECRET_KEY=$(openssl rand -hex 32)
        
        # Deploy
        git push heroku main
        
        echo -e "${GREEN}✅ Deployed to Heroku!${NC}"
        heroku open
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Set environment variables in your hosting platform"
echo "2. Run database migrations"
echo "3. Test your deployment"
echo "4. Configure custom domain (optional)"
echo ""
echo "Need help? Check CLOUDFLARE_DEPLOYMENT.md"
