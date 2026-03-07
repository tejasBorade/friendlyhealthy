# Quick Deployment Reference

## 🌐 Live URLs

**Frontend**: https://5d585636.friendlyhealthy.pages.dev
**Backend**: https://friendlyhealthy.tejasborade9594.workers.dev
**API Docs**: https://friendlyhealthy.tejasborade9594.workers.dev/docs

## 🚀 Quick Redeploy

### Frontend:
```powershell
cd frontend
npm run build
npx wrangler pages deploy dist --project-name=friendlyhealthy
```

### Backend:
```powershell
cd cloudflare-backend
npx wrangler deploy
```

## 🔑 Add API Keys

Go to https://dash.cloudflare.com/
→ Pages → friendlyhealthy → Settings → Environment Variables

Add:
- `VITE_APIMEDIC_USERNAME` = your-username
- `VITE_APIMEDIC_PASSWORD` = your-password  
- `VITE_GOOGLE_MAPS_API_KEY` = your-key

Then **redeploy** the project.

## 📊 Current Status

| Feature | Status |
|---------|--------|
| Frontend | ✅ LIVE |
| Backend | ✅ LIVE |
| OpenFDA (Medicine Search) | ✅ Working (real data) |
| ApiMedic (Diagnosis) | 🟡 Demo mode |
| Google Maps (Doctors) | 🟡 Demo mode |

## 📚 Full Guide

See [CLOUDFLARE_DEPLOYMENT_SUCCESS.md](CLOUDFLARE_DEPLOYMENT_SUCCESS.md) for complete instructions.

## 💡 Pro Tips

1. **Enable auto-deploy**: Connect GitHub to Cloudflare Pages for automatic deployments on push
2. **Custom domain**: Set up in Cloudflare Pages dashboard → Custom domains
3. **Monitor logs**: Run `npx wrangler tail` in cloudflare-backend folder
4. **Analytics**: Enable in Cloudflare dashboard for traffic insights

---

**Last Deployed**: March 7, 2026
