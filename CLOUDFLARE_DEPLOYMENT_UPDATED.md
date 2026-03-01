# 🚀 Deploy Healthcare Platform to Cloudflare - Updated Guide

## Changes Included in This Deployment

### Backend API Changes:
✅ Medical Records - POST endpoint added with field mapping  
✅ Prescriptions - POST endpoint updated  with medication fields
✅ Response schemas updated to match frontend expectations  
✅ Medication fields added directly to prescriptions table

---

## Prerequisites

```powershell
# Install Wrangler CLI globally
npm install -g wrangler

# Login to Cloudflare
wrangler login
```

---

## Step 1: Update D1 Database Schema

```powershell
cd cloudflare-backend

# Run migration to add medication fields to prescriptions table
wrangler d1 execute friendlyhealthy-db --file=migration-add-prescription-fields.sql

# Verify migration
wrangler d1 execute friendlyhealthy-db --command="PRAGMA table_info(prescriptions)"
```

**Expected Output:** You should see new columns: `medication_name`, `dosage`, `frequency`, `duration`, `instructions`, `prescribed_date`

---

## Step 2: Test Backend Locally

```powershell
cd cloudflare-backend

# Install dependencies (if not already done)
npm install

# Start local dev server
npm run dev
```

Visit http://localhost:8787 to test the API locally.

### Test Endpoints:
```powershell
# Test medical records GET (replace token)
curl http://localhost:8787/api/v1/medical-records?patientId=1 `
  -H "Authorization: Bearer YOUR_TOKEN"

# Test prescriptions GET
curl http://localhost:8787/api/v1/prescriptions?patientId=1 `
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Step 3: Deploy Backend to Cloudflare Workers

```powershell
cd cloudflare-backend

# Deploy to production
npm run deploy
```

**Your backend will be available at:**
`https://friendlyhealthy.<your-subdomain>.workers.dev`

Copy this URL - you'll need it for the frontend deployment.

---

## Step 4: Update Frontend Environment Variables

```powershell
cd ..
cd frontend

# Create production environment file
$workerUrl = "https://friendlyhealthy.<your-subdomain>.workers.dev"
"VITE_API_URL=$workerUrl/api/v1" | Out-File .env.production -Encoding UTF8

# Verify the file
Get-Content .env.production
```

---

## Step 5: Deploy Frontend to Cloudflare Pages

### Option A: Via Cloudflare Dashboard (Recommended)

1. **Go to Cloudflare Dashboard** → Pages → Create a project

2. **Connect GitHub Repository:**
   - Repository: `tejasBorade/friendlyhealthy`
   - Branch: `main`

3. **Build Configuration:**
   ```
   Framework preset: Vite
   Build command: npm run build
   Build output directory: dist
   Root directory: frontend
   ```

4. **Environment Variables:**
   ```
   VITE_API_URL = https://friendlyhealthy.<your-subdomain>.workers.dev/api/v1
   NODE_VERSION = 18
   ```

5. **Click "Save and Deploy"**

### Option B: Via Command Line

```powershell
cd frontend

# Build the frontend
npm install
npm run build

# Deploy to Cloudflare Pages (first time)
npx wrangler pages deploy dist --project-name=friendlyhealthy-app

# For subsequent deployments
npx wrangler pages deploy dist
```

---

## Step 6: Verify Deployment

### Backend Verification:
```powershell
# Test medical records endpoint
$token = "YOUR_DOCTOR_TOKEN"
Invoke-RestMethod -Uri "https://friendlyhealthy.<your-subdomain>.workers.dev/api/v1/medical-records?patientId=1" `
  -Headers @{Authorization="Bearer $token"}

# Test prescriptions endpoint  
Invoke-RestMethod -Uri "https://friendlyhealthy.<your-subdomain>.workers.dev/api/v1/prescriptions?patientId=1" `
  -Headers @{Authorization="Bearer $token"}
```

### Frontend Verification:
1. Visit your Cloudflare Pages URL
2. Login as a doctor
3. Navigate to Patient Journey page
4. Test adding:
   - Medical History
   - Prescriptions
   - Reports & Documents
5. Verify they display correctly

---

## Step 7: Configure Custom Domain (Optional)

### In Cloudflare Dashboard:

**For Backend (Workers):**
1. Go to Workers & Pages → friendlyhealthy → Settings → Triggers
2. Add Custom Domain: `api.yourapp.com`

**For Frontend (Pages):**
1. Go to Pages → friendlyhealthy-app → Custom domains
2. Add Custom Domain: `yourapp.com`

**Then update frontend .env:**
```
VITE_API_URL=https://api.yourapp.com/api/v1
```

---

## Rollback Instructions

### If something goes wrong:

**Backend Rollback:**
```powershell
cd cloudflare-backend
wrangler rollback
```

**Frontend Rollback:**
```powershell
cd frontend
# Go to Cloudflare Dashboard → Pages → Deployments
# Click "..." on previous deployment → "Rollback to this deployment"
```

**Database Rollback:**
```powershell
# Remove added columns (if needed)
wrangler d1 execute friendlyhealthy-db --command="
  ALTER TABLE prescriptions DROP COLUMN medication_name;
  ALTER TABLE prescriptions DROP COLUMN dosage;
  ALTER TABLE prescriptions DROP COLUMN frequency;
  ALTER TABLE prescriptions DROP COLUMN duration;
  ALTER TABLE prescriptions DROP COLUMN instructions;
  ALTER TABLE prescriptions DROP COLUMN prescribed_date;
"
```

---

## Monitoring & Logs

### View Worker Logs:
```powershell
wrangler tail
```

### View Pages Build Logs:
- Cloudflare Dashboard → Pages → Deployments → Click deployment → View logs

### Check Database:
```powershell
# Query prescriptions table
wrangler d1 execute friendlyhealthy-db --command="SELECT * FROM prescriptions LIMIT 5"

# Query medical records table  
wrangler d1 execute friendlyhealthy-db --command="SELECT * FROM medical_records LIMIT 5"
```

---

## Common Issues & Solutions

### Issue: "Database not found"
**Solution:** Check `wrangler.toml` has correct `database_id`

### Issue: "Column not found" in prescriptions
**Solution:** Run the migration script again:
```powershell
wrangler d1 execute friendlyhealthy-db --file=migration-add-prescription-fields.sql
```

### Issue: Frontend shows 404 errors
**Solution:** 
1. Check `VITE_API_URL` in frontend environment variables
2. Ensure backend is deployed and accessible
3. Check browser console for CORS errors

### Issue: CORS errors
**Solution:** Backend should already have CORS middleware. Verify `src/index.ts` has CORS headers.

---

## Post-Deployment Checklist

- [ ] Backend deployed successfully to Workers
- [ ] Migration script executed on D1 database
- [ ] Frontend built and deployed to Pages
- [ ] Environment variables configured correctly
- [ ] Medical Records endpoints tested (GET, POST)
- [ ] Prescriptions endpoints tested (GET, POST)
- [ ] Frontend displays data correctly
- [ ] Doctor can add medical history
- [ ] Doctor can add prescriptions
- [ ] Doctor can upload reports
- [ ] All data persists in D1 database

---

## Support

If you encounter issues:
1. Check Wrangler logs: `wrangler tail`
2. Check D1 database: `wrangler d1 execute friendlyhealthy-db --command="SELECT * FROM prescriptions LIMIT 1"`
3. Verify API URL in frontend matches Worker URL
4. Check browser console for frontend errors

---

## Next Steps After Deployment

1. **Setup Analytics:** Enable Web Analytics in Cloudflare Pages
2. **Configure Caching:** Adjust cache rules in Worker settings
3. **Enable Rate Limiting:** Add rate limiting to protect APIs
4. **Setup Monitoring:** Use Cloudflare Analytics to monitor usage
5. **Backup Database:** Regularly export D1 database

```powershell
# Export database backup
wrangler d1 export friendlyhealthy-db --output=backup-$(Get-Date -Format "yyyy-MM-dd").sql
```

---

## Cost Estimate (Cloudflare Free Tier)

- **Workers:** 100,000 requests/day (Free)
- **Pages:** Unlimited requests (Free)
- **D1 Database:** 5GB storage, 5M reads/day, 100K writes/day (Free)
- **R2 Storage:** 10 GB storage (Free)

Your application should run comfortably within the free tier! 🎉
