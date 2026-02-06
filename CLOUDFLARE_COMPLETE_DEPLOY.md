# Deploy to Cloudflare - Complete Guide

## 🚀 Deploy Both Frontend and Backend to Cloudflare

### Prerequisites
```bash
npm install -g wrangler
wrangler login
```

---

## Step 1: Setup Cloudflare D1 Database

```bash
cd cloudflare-backend

# Create D1 database
wrangler d1 create friendlyhealthy-db

# Copy the database_id from output and update wrangler.toml

# Execute schema
wrangler d1 execute friendlyhealthy-db --file=schema.sql

# Verify tables
wrangler d1 execute friendlyhealthy-db --command="SELECT name FROM sqlite_master WHERE type='table'"
```

---

## Step 2: Setup Cloudflare R2 Storage

```bash
# Create R2 bucket for file uploads
wrangler r2 bucket create friendlyhealthy-files
```

---

## Step 3: Setup Cloudflare KV

```bash
# Create KV namespace
wrangler kv:namespace create "CACHE"

# Copy the id and update wrangler.toml
```

---

## Step 4: Deploy Backend (Cloudflare Workers)

```bash
cd cloudflare-backend

# Install dependencies
npm install

# Test locally
npm run dev
# Visit http://localhost:8787

# Deploy to production
npm run deploy
```

Your backend will be at: `https://friendlyhealthy.your-subdomain.workers.dev`

---

## Step 5: Deploy Frontend (Cloudflare Pages)

### Option A: Via Dashboard
1. Go to https://dash.cloudflare.com → Pages
2. Create a project
3. Connect GitHub: tejasBorade/friendlyhealthy
4. Configure:
   - Framework: Vite
   - Build command: `npm run build`
   - Build directory: `dist`
   - Root directory: `frontend`
5. Environment variables:
   ```
   VITE_API_URL=https://friendlyhealthy.your-subdomain.workers.dev/api/v1
   ```
6. Deploy

### Option B: Via CLI
```bash
cd frontend

# Update API URL
echo "VITE_API_URL=https://friendlyhealthy.your-subdomain.workers.dev/api/v1" > .env.production

# Build
npm install
npm run build

# Deploy
wrangler pages deploy dist --project-name=friendlyhealthy
```

---

## Step 6: Configure Custom Domain (Optional)

### For Backend:
```bash
wrangler route add "api.friendlyhealthy.com/*" friendlyhealthy
```

### For Frontend:
1. Go to Pages → friendlyhealthy → Custom domains
2. Add: `friendlyhealthy.com`

---

## 🔧 Environment Variables

Update `cloudflare-backend/wrangler.toml`:

```toml
[vars]
JWT_SECRET = "your-secret-key-32-chars-minimum"
ENVIRONMENT = "production"
```

---

## 🧪 Test Your Deployment

```bash
# Test health endpoint
curl https://friendlyhealthy.your-subdomain.workers.dev/health

# Test registration
curl -X POST https://friendlyhealthy.your-subdomain.workers.dev/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@1234","role":"patient"}'
```

---

## 📊 Monitor Your App

- **Workers**: https://dash.cloudflare.com → Workers & Pages → friendlyhealthy
- **Analytics**: View requests, errors, and performance
- **Logs**: Real-time logs in dashboard

---

## 💰 Pricing

**Free Tier Includes:**
- 100,000 Workers requests/day
- Unlimited Pages bandwidth
- 5 GB D1 database storage
- 10 GB R2 storage

**Paid Plans:**
- Workers: $5/month (10M requests)
- D1: $5/month (25 GB)
- R2: $0.015/GB/month

---

## 🔄 Update Your Deployment

```bash
# Backend updates
cd cloudflare-backend
npm run deploy

# Frontend updates
cd frontend
npm run build
wrangler pages deploy dist --project-name=friendlyhealthy
```

---

## ⚠️ Important Notes

1. **Database Differences**: D1 uses SQLite, not PostgreSQL
   - No stored procedures
   - Limited triggers
   - Simpler queries

2. **File Storage**: Use R2 instead of local filesystem
   - All files go to R2 bucket
   - Access via bucket.get() / bucket.put()

3. **Background Tasks**: Use Durable Objects or Queues instead of Celery

4. **Limitations**:
   - Max request time: 50ms (free) / unlimited (paid)
   - Max request size: 100MB
   - No long-running processes

---

## 🎯 Quick Deploy Commands

```bash
# Deploy everything
cd cloudflare-backend && npm run deploy && cd ../frontend && npm run build && wrangler pages deploy dist

# Or use the one-liner:
npm run deploy:all
```

---

## 📝 What's Different from Python Backend?

**Changed:**
- ✅ Python → TypeScript
- ✅ FastAPI → Hono.js
- ✅ PostgreSQL → Cloudflare D1 (SQLite)
- ✅ Local files → Cloudflare R2
- ✅ Redis → Cloudflare KV
- ✅ Celery → Cloudflare Queues

**Same:**
- ✅ JWT authentication
- ✅ RBAC (roles)
- ✅ All API endpoints
- ✅ Same request/response format
- ✅ Frontend unchanged

---

## 🚀 Your Cloudflare URLs

After deployment:

**Backend API**: `https://friendlyhealthy.[your-subdomain].workers.dev`  
**Frontend**: `https://friendlyhealthy.pages.dev`  
**API Docs**: Check backend /health endpoint

---

**Need help?** Check [Cloudflare Docs](https://developers.cloudflare.com)
