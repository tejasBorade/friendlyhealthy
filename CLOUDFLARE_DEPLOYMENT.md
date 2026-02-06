# Cloudflare Pages Deployment Guide

## Option 1: Deploy Frontend to Cloudflare Pages (Recommended)

### Step 1: Build Configuration
Your React frontend can be deployed to Cloudflare Pages.

**Build Settings:**
- Build command: `npm run build`
- Build output directory: `dist`
- Root directory: `frontend`
- Node version: 18

### Step 2: Deploy via Git
1. Go to Cloudflare Dashboard → Pages
2. Click "Create a project"
3. Connect your GitHub repository: `tejasBorade/friendlyhealthy`
4. Configure build settings:
   ```
   Framework preset: Vite
   Build command: npm run build
   Build output directory: dist
   Root directory: frontend
   ```

### Step 3: Environment Variables
Add these to Cloudflare Pages:
```
VITE_API_URL=https://your-backend-api.railway.app/api/v1
```

### Step 4: Deploy
Click "Save and Deploy"

---

## Backend Deployment Options

### Option A: Railway (Recommended - Easy)
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Python and deploys
5. Add PostgreSQL from Railway's plugin marketplace
6. Set environment variables

**Railway Configuration:**
- Automatically detects `requirements.txt`
- Uses `uvicorn` to run FastAPI
- Provides free PostgreSQL database
- Free $5 credit monthly

### Option B: Render (Free Tier Available)
1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repository
4. Configure:
   ```
   Name: friendlyhealthy-api
   Environment: Python 3.11
   Build Command: pip install -r backend/requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Option C: Heroku
```bash
# Install Heroku CLI
heroku login
heroku create friendlyhealthy-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Deploy
git push heroku main
```

---

## Option 2: Cloudflare Workers (Backend Rewrite Required)

⚠️ **Note**: This requires rewriting your backend in TypeScript/JavaScript.

If you want everything on Cloudflare, you'd need to:
1. Rewrite FastAPI backend using Hono.js or similar
2. Use Cloudflare D1 (SQLite) instead of PostgreSQL
3. Use Cloudflare R2 for file storage
4. Use Cloudflare KV for caching

This is a **significant rewrite** (weeks of work).

---

## 🎯 Quick Deploy Solution (15 minutes)

### Step 1: Deploy Backend to Railway
```bash
# 1. Sign up at railway.app
# 2. Install Railway CLI
npm i -g @railway/cli

# 3. Login
railway login

# 4. Create new project
railway init

# 5. Add PostgreSQL
railway add postgresql

# 6. Deploy
railway up
```

### Step 2: Deploy Frontend to Cloudflare Pages
```bash
# 1. Build frontend with backend URL
cd frontend
echo "VITE_API_URL=https://your-railway-app.railway.app/api/v1" > .env.production

# 2. Build
npm run build

# 3. Deploy to Cloudflare Pages (via dashboard or CLI)
npm install -g wrangler
wrangler pages deploy dist --project-name=friendlyhealthy
```

---

## Current Status Analysis

Your Cloudflare Workers service: `friendlyhealthy`
- ❌ Cannot run Python FastAPI directly
- ❌ Cannot run PostgreSQL database
- ✅ Can serve static frontend (React build)
- ✅ Can act as edge functions/API gateway

---

## Recommended Action Plan

**Immediate (30 mins):**
1. ✅ Deploy backend to Railway (free tier)
2. ✅ Deploy frontend to Cloudflare Pages
3. ✅ Use Railway PostgreSQL

**Future (optional):**
1. Migrate file storage to Cloudflare R2
2. Use Cloudflare Workers as API gateway/cache
3. Add Cloudflare CDN for performance

---

Would you like me to:
1. Create Railway/Render deployment configs?
2. Create Cloudflare Pages deployment config?
3. Create a TypeScript/Hono backend (for full Cloudflare stack)?
4. Set up hybrid deployment (backend elsewhere + frontend on CF)?
