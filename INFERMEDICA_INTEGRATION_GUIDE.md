# Infermedica AI Symptom Checker Integration Guide

## ⚠️ IMPORTANT UPDATE - March 2026

**Infermedica sign-up is currently unavailable.** The symptom checker now runs in **DEMO MODE** with mock data, allowing you to test the UI and functionality.

### Current Options:

1. **Use Demo Mode** (Already Active) - Free, for testing only
2. **Switch to ApiMedic** (Recommended) - Similar service, $10/month
3. **Build Custom with OpenAI** - Flexible, pay-per-use
4. **Wait for Infermedica** - Check status periodically

👉 **See [SYMPTOM_CHECKER_ALTERNATIVES.md](SYMPTOM_CHECKER_ALTERNATIVES.md) for detailed alternative options and integration guides.**

---

## Overview

We've integrated an AI-powered symptom checker on your healthcare platform. This feature is available on the home page for all users, including non-registered visitors.

## Features

✅ **AI-Powered Symptom Analysis** - Advanced medical intelligence (or demo mock data)
✅ **Step-by-Step Assessment** - User-friendly guided symptom collection
✅ **Triage Recommendations** - Emergency detection and care recommendations  
✅ **Possible Conditions** - Ranked list of potential diagnoses with probabilities
✅ **Professional UI** - Beautiful Material-UI design with smooth animations
✅ **Publicly Accessible** - Available on homepage without login required
✅ **Demo Mode** - Works immediately with mock data for testing

## Current Status: Demo Mode Active

The symptom checker is **currently running in demo mode** and uses simulated medical data. This means:

- ✅ Fully functional UI and user flow
- ✅ Can search and select symptoms
- ✅ Shows mock diagnosis results
- ✅ Demonstrates triage recommendations
- ❌ Does NOT provide real medical analysis
- ❌ Not suitable for actual patient use

**To switch to a real medical API, see:** [SYMPTOM_CHECKER_ALTERNATIVES.md](SYMPTOM_CHECKER_ALTERNATIVES.md)

---

## Getting Started (Demo Mode)

### The symptom checker is already working!

1. Visit your home page: `http://localhost:3001`
2. Scroll to "Check Your Symptoms" section
3. Try it with demo data

**No API credentials needed for demo mode.**

---

## Getting Started (Real Medical API)

### Option 1: ApiMedic (Recommended Alternative)

See detailed integration guide in [SYMPTOM_CHECKER_ALTERNATIVES.md](SYMPTOM_CHECKER_ALTERNATIVES.md#1-apimedic-priaid--recommended)

### Option 2: Wait for Infermedica

If you want to wait for Infermedica to become available:

### Step 1: Get Infermedica API Credentials (When Available)

1. Visit [Infermedica Developer Portal](https://developer.infermedica.com/)
2. Click "Sign Up" to create a free account
3. After registration, go to your dashboard
4. Navigate to "Applications" section
5. Create a new application or use the default one
6. Copy your **App ID** and **App Key**

**Free Tier Limits:**
- 500 requests per month
- Academic/research use: Contact for increased limits
- Commercial use: See pricing page

### Step 2: Configure Environment Variables

1. Open `frontend/.env.local` file
2. Replace the placeholder values:

```env
VITE_INFERMEDICA_APP_ID=your-actual-app-id
VITE_INFERMEDICA_APP_KEY=your-actual-app-key
```

**Example:**
```env
VITE_INFERMEDICA_APP_ID=a1b2c3d4
VITE_INFERMEDICA_APP_KEY=e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

### Step 3: Restart Frontend

After updating the environment variables, restart your frontend development server:

```powershell
# Stop the current frontend (Ctrl+C in the terminal)
cd frontend
npm run dev
```

The symptom checker will now use your Infermedica credentials.

## How to Use

### For Website Visitors:

1. Navigate to the home page: `http://localhost:3001` (or root URL)
2. Scroll down to "Check Your Symptoms" section
3. Follow the guided 3-step process:
   - **Step 1:** Enter age and sex
   - **Step 2:** Search and select symptoms
   - **Step 3:** Review and get diagnosis

### User Flow:

```
Home Page → Symptom Checker Section → Enter Info → Search Symptoms → Get Diagnosis → Book Appointment
```

## Components Created

### 1. SymptomChecker Component
**Location:** `frontend/src/components/SymptomChecker.jsx`

**Features:**
- Debounced symptom search
- Multi-step wizard interface
- Symptom selection with chips
- AI diagnosis with triage levels
- Condition probability rankings
- Responsive design

### 2. Home/Landing Page
**Location:** `frontend/src/pages/Home.jsx`

**Sections:**
- Hero section with CTA buttons
- Feature highlights grid
- Integrated symptom checker
- Call-to-action section
- Footer with links

## API Endpoints Used

The integration uses the following Infermedica API endpoints:

### 1. Search Symptoms
```
GET https://api.infermedica.com/v3/search
```
**Parameters:**
- `phrase` - Search query
- `max_results` - Number of results (default: 8)

### 2. Get Diagnosis
```
POST https://api.infermedica.com/v3/diagnosis
```
**Body:**
```json
{
  "sex": "male" | "female",
  "age": { "value": 30 },
  "evidence": [
    {
      "id": "symptom_id",
      "choice_id": "present",
      "source": "initial"
    }
  ],
  "extras": {
    "enable_triage_5": true
  }
}
```

## Triage Levels

The symptom checker provides the following triage recommendations:

| Level | Meaning | Color |
|-------|---------|-------|
| `emergency_ambulance` | Call ambulance immediately | Red |
| `emergency` | Seek immediate care | Red |
| `consultation_24` | Consult doctor within 24 hours | Orange |
| `consultation` | Schedule a consultation | Yellow |
| `self_care` | Self-care recommended | Green |

## Customization

### Modify Number of Results

In `SymptomChecker.jsx`, line 43:
```javascript
params: { phrase: query, max_results: 8 },  // Change 8 to your preferred number
```

### Change Triage Colors

In `SymptomChecker.jsx`, lines 138-145:
```javascript
const getTriageColor = (level) => {
  const colors = {
    emergency: '#ef4444',           // Customize these colors
    emergency_ambulance: '#dc2626',
    consultation_24: '#f97316',
    consultation: '#f59e0b',
    self_care: '#10b981',
  };
  return colors[level] || '#6b7280';
};
```

### Modify Step Labels

In `SymptomChecker.jsx`, line 26:
```javascript
const steps = ['Basic Info', 'Search Symptoms', 'Review & Diagnose'];  // Customize labels
```

## Security Considerations

⚠️ **Important Security Notes:**

1. **API Keys in Frontend**: API keys are exposed in the frontend bundle. For production:
   - Consider proxying requests through your backend
   - Use rate limiting on your backend
   - Monitor Infermedica usage in their dashboard

2. **Recommended Production Setup**:
   ```
   Frontend → Your Backend API → Infermedica API
   ```
   This way, API keys remain secure on the server.

3. **Rate Limiting**: Implement rate limiting to prevent abuse:
   - Limit requests per IP address
   - Add CAPTCHA for suspicious activity
   - Monitor usage patterns

## Backend Proxy (Recommended for Production)

### Create Backend Endpoint

Add to `backend/app/api/routes/symptom_checker.py`:

```python
from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter(prefix="/symptom-checker", tags=["Symptom Checker"])

INFERMEDICA_APP_ID = os.getenv("INFERMEDICA_APP_ID")
INFERMEDICA_APP_KEY = os.getenv("INFERMEDICA_APP_KEY")

@router.get("/search")
async def search_symptoms(phrase: str, max_results: int = 8):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.infermedica.com/v3/search",
            params={"phrase": phrase, "max_results": max_results},
            headers={
                "App-Id": INFERMEDICA_APP_ID,
                "App-Key": INFERMEDICA_APP_KEY,
            }
        )
        return response.json()

@router.post("/diagnosis")
async def get_diagnosis(data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.infermedica.com/v3/diagnosis",
            json=data,
            headers={
                "App-Id": INFERMEDICA_APP_ID,
                "App-Key": INFERMEDICA_APP_KEY,
                "Content-Type": "application/json",
            }
        )
        return response.json()
```

### Update Frontend to Use Backend Proxy

In `SymptomChecker.jsx`, replace API calls:

```javascript
// Instead of calling Infermedica directly:
const response = await axios.get('https://api.infermedica.com/v3/search', ...);

// Call your backend:
const response = await api.get('/symptom-checker/search', {
  params: { phrase: query, max_results: 8 }
});
```

## Troubleshooting

### Issue: "Disallowed CORS origin"

**Solution:** This happens when API keys are invalid or domain isn't registered.
1. Verify your API credentials
2. Check Infermedica dashboard for allowed domains
3. Add your domain to allowed origins in Infermedica settings

### Issue: Symptom search returns no results

**Possible causes:**
1. Search query too short (minimum 3 characters)
2. Invalid API credentials  
3. Network connectivity issues

**Debug steps:**
```javascript
// Add console.log in searchSymptoms function
console.log('Search query:', query);
console.log('API response:', response.data);
```

### Issue: Diagnosis returns error

**Check:**
1. Age is valid (0-120)
2. At least one symptom is selected
3. API rate limits not exceeded
4. API credentials are correct

### Issue: Environment variables not loading

**Solution:**
1. Ensure `.env.local` file exists in `frontend/` directory
2. Variables must start with `VITE_` prefix
3. Restart dev server after changing env vars
4. Check for typos in variable names

## Testing

### Manual Testing Checklist:

- [ ] Home page loads successfully
- [ ] Symptom checker is visible
- [ ] Can enter age and select sex
- [ ] Can search for symptoms (e.g., "headache")
- [ ] Search results appear
- [ ] Can select multiple symptoms
- [ ] Selected symptoms appear as chips
- [ ] Can remove symptoms by clicking X
- [ ] Can navigate between steps
- [ ] Diagnosis loads with triage recommendation
- [ ] Possible conditions are displayed
- [ ] Can start over and repeat process
- [ ] "Book Appointment" button works

### Test Scenarios:

**Scenario 1: Emergency Detection**
```
Age: 35, Sex: Male
Symptoms: chest pain, shortness of breath
Expected: Emergency triage level
```

**Scenario 2: Common Cold**
```
Age: 28, Sex: Female
Symptoms: runny nose, sore throat, cough
Expected: Self-care or consultation triage level
```

**Scenario 3: Multiple Symptoms**
```
Age: 45, Sex: Male
Symptoms: fever, headache, body aches, fatigue
Expected: Multiple possible conditions like flu, COVID-19
```

## Production Deployment

### Frontend (.env.production)

```env
VITE_API_URL=https://your-api-domain.com/api/v1
VITE_INFERMEDICA_APP_ID=your-production-app-id
VITE_INFERMEDICA_APP_KEY=your-production-app-key
```

### Cloudflare Workers

If deploying to Cloudflare:

1. Add secrets to Cloudflare:
```bash
wrangler secret put INFERMEDICA_APP_ID
wrangler secret put INFERMEDICA_APP_KEY
```

2. Update `cloudflare-backend` to proxy Infermedica requests

### Best Practices

1. ✅ Use backend proxy for API calls
2. ✅ Implement rate limiting (e.g., 10 requests/hour per IP)
3. ✅ Add logging for API usage monitoring
4. ✅ Cache common symptom searches
5. ✅ Display clear disclaimers about medical advice
6. ✅ GDPR compliance: Don't store symptom data without consent
7. ✅ Add analytics to track usage patterns
8. ✅ Implement error boundaries for graceful failures

## Medical Disclaimer

⚠️ **Important:** The symptom checker provides preliminary assessments only and should not replace professional medical advice. Always include appropriate disclaimers:

```
"This AI-powered symptom checker provides preliminary health assessments
and should not replace professional medical advice, diagnosis, or treatment.
Always consult with a qualified healthcare provider for medical concerns."
```

## Support & Resources

- **Infermedica Documentation:** https://developer.infermedica.com/docs/introduction
- **API Reference:** https://developer.infermedica.com/docs/api
- **Status Page:** https://status.infermedica.com/
- **Support:** support@infermedica.com

## License & Attribution

When using Infermedica API, you must:
1. Display "Powered by Infermedica" attribution
2. Follow their terms of service
3. Respect rate limits
4. Use responsibly for healthcare purposes

## Next Steps

1. ✅ Get your Infermedica API credentials
2. ✅ Update `.env.local` with real credentials  
3. ✅ Test the symptom checker on home page
4. 🔄 Consider implementing backend proxy for production
5. 🔄 Add analytics tracking
6. 🔄 Customize UI to match your brand
7. 🔄 Add multilingual support (Infermedica supports 15+ languages)

---

**Questions or Issues?** Check the troubleshooting section or contact the Infermedica support team.
