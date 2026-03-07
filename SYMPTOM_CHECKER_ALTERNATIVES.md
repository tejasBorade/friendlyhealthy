# Alternative Symptom Checker APIs

## 🚨 Important Update

Infermedica sign-up is currently unavailable. This document provides alternative medical symptom checker APIs you can integrate instead.

## 🎯 Current Status

Your symptom checker is now running in **DEMO MODE** which uses mock data for testing. This allows you to:
- ✅ Test the UI and user flow
- ✅ See how the symptom checker works
- ✅ Demonstrate the feature to stakeholders
- ❌ NOT get real medical diagnoses (demo data only)

## 🔄 Alternative Medical APIs

### 1. **ApiMedic (Priaid)** ⭐ RECOMMENDED

**Website:** https://apimedic.com/

**Overview:** Similar to Infermedica, provides symptom checking and diagnosis suggestions.

**Pricing:**
- **Free Trial:** 300 requests
- **Basic:** $9.99/month - 1,000 requests
- **Professional:** $49/month - 10,000 requests
- **Enterprise:** Custom pricing

**Features:**
- ✅ Symptom search
- ✅ Diagnosis suggestions with probabilities
- ✅ Specialization recommendations
- ✅ Issue information
- ✅ Multiple languages (English, Spanish, German, French, Portuguese, etc.)

**Integration Steps:**

1. Sign up at https://apimedic.com/
2. Get your API credentials (Username & Password)
3. Generate auth token
4. Update the symptom checker component

**Sample Code:**

```javascript
// ApiMedic Authentication
const API_USERNAME = import.meta.env.VITE_APIMEDIC_USERNAME;
const API_PASSWORD = import.meta.env.VITE_APIMEDIC_PASSWORD;
const API_URL = 'https://healthservice.priaid.ch';
const AUTH_URL = 'https://authservice.priaid.ch/login';

// Get auth token
const getAuthToken = async () => {
  const crypto = require('crypto');
  const computedHash = crypto
    .createHmac('md5', API_PASSWORD)
    .update(AUTH_URL)
    .digest('base64');
    
  const response = await axios.post(
    AUTH_URL,
    {},
    {
      headers: {
        'Authorization': `Bearer ${API_USERNAME}:${computedHash}`
      }
    }
  );
  return response.data.Token;
};

// Search symptoms
const searchSymptoms = async (query, token) => {
  const response = await axios.get(
    `${API_URL}/symptoms?token=${token}&format=json&language=en-gb`
  );
  // Filter by query
  return response.data.filter(s => 
    s.Name.toLowerCase().includes(query.toLowerCase())
  );
};

// Get diagnosis
const getDiagnosis = async (symptoms, age, sex, token) => {
  const symptomIds = symptoms.map(s => s.ID).join(',');
  const response = await axios.get(
    `${API_URL}/diagnosis?symptoms=[${symptomIds}]&gender=${sex}&year_of_birth=${new Date().getFullYear() - age}&token=${token}&format=json&language=en-gb`
  );
  return response.data;
};
```

**Environment Variables:**
```env
VITE_APIMEDIC_USERNAME=your-username
VITE_APIMEDIC_PASSWORD=your-password
```

---

### 2. **Symptoma API**

**Website:** https://www.symptoma.com/en/api

**Overview:** Medical symptom checker with differential diagnosis.

**Pricing:** Contact for pricing (typically enterprise-focused)

**Features:**
- ✅ Symptom analysis
- ✅ Differential diagnosis
- ✅ Disease information
- ✅ Medical knowledge base

---

### 3. **Isabel Healthcare API**

**Website:** https://www.isabelhealthcare.com/

**Overview:** Clinical decision support and diagnosis tool.

**Pricing:** Enterprise pricing (contact sales)

**Features:**
- ✅ Symptom checker
- ✅ Diagnosis suggestions
- ✅ Used by medical professionals
- ✅ Evidence-based results

---

### 4. **Ada Health** (Enterprise Only)

**Website:** https://ada.com/

**Overview:** Advanced AI symptom assessment.

**Pricing:** Enterprise licensing only (not publicly available)

**Features:**
- ✅ Conversational symptom collection
- ✅ Advanced AI algorithms
- ✅ Multi-language support
- ✅ High accuracy

**Note:** Ada doesn't offer a public API - requires enterprise partnership.

---

### 5. **Build Your Own with OpenAI**

If commercial APIs are too expensive, you can build a basic symptom analyzer using OpenAI:

**Cost:** OpenAI API pricing (pay-per-use)

**Sample Implementation:**

```javascript
const analyzeSymptoms = async (symptoms, age, sex) => {
  const prompt = `You are a medical symptom analyzer. Based on the following information, provide:
1. Possible conditions (with confidence levels)
2. Triage recommendation (emergency, urgent, routine)
3. General advice

Patient Information:
- Age: ${age}
- Sex: ${sex}
- Symptoms: ${symptoms.join(', ')}

Provide response in JSON format:
{
  "triage": {"level": "...", "description": "..."},
  "conditions": [{"name": "...", "probability": 0.0-1.0}]
}

Important: Include medical disclaimer.`;

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${OPENAI_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: 'You are a medical symptom analyzer assistant.' },
        { role: 'user', content: prompt }
      ],
      temperature: 0.3
    })
  });
  
  return await response.json();
};
```

**⚠️ Disclaimer:** OpenAI solutions are not medically certified and should include strong disclaimers.

---

## 📊 Comparison Table

| Service | Free Tier | Cost | Accuracy | Ease of Integration | Recommendation |
|---------|-----------|------|----------|-------------------|----------------|
| **ApiMedic** | 300 requests | $10+/mo | High | Easy | ⭐⭐⭐⭐⭐ |
| **Symptoma** | No | Enterprise | High | Medium | ⭐⭐⭐⭐ |
| **Isabel** | No | Enterprise | Very High | Medium | ⭐⭐⭐⭐ |
| **Ada Health** | No | Enterprise | Very High | N/A (Not public) | ⭐⭐⭐ |
| **OpenAI Custom** | $5+ credits | Pay-per-use | Medium | Easy | ⭐⭐⭐ |
| **Demo Mode** | ✅ Free | Free | N/A (Mock) | Already done | ⭐⭐ |

---

## 🚀 Recommended Path Forward

### Option A: Quick Start with ApiMedic (Recommended)

**Best for:** Production-ready solution with minimal cost

1. Sign up at https://apimedic.com/ (Get 300 free requests)
2. Get API credentials
3. Update SymptomChecker component (see sample code above)
4. Test with real medical data
5. Upgrade plan as needed

**Timeline:** 1-2 hours
**Cost:** $9.99/month after free trial

---

### Option B: Continue with Demo Mode

**Best for:** Testing, demos, MVP without medical liability

- ✅ Already implemented
- ✅ Free forever
- ✅ No API dependencies
- ❌ Not real medical data
- ❌ Not suitable for production medical use

**Timeline:** 0 hours (already done)
**Cost:** Free

---

### Option C: Custom AI with OpenAI

**Best for:** Flexible solution with full control

1. Get OpenAI API key
2. Implement symptom analysis with GPT-4
3. Add proper medical disclaimers
4. Consider medical liability insurance

**Timeline:** 4-8 hours
**Cost:** ~$0.01-0.03 per diagnosis
**Warning:** Requires strong disclaimers and legal review

---

## 🔧 How to Switch APIs

### Switching to ApiMedic:

1. **Install axios** (already installed)

2. **Update environment variables:**
```env
VITE_APIMEDIC_USERNAME=your-username
VITE_APIMEDIC_PASSWORD=your-password
```

3. **Update SymptomChecker.jsx:**

Replace the API calls in `searchSymptoms` and `getDiagnosis` functions with ApiMedic endpoints (see sample code above).

4. **Restart frontend:**
```bash
cd frontend
npm run dev
```

### Testing with Demo Mode:

Demo mode is already active! Just use the symptom checker as-is. It will:
- Show common symptoms when you search
- Provide mock diagnosis results
- Display triage recommendations
- Work offline

---

## 📝 Medical Disclaimer Requirements

**⚠️ CRITICAL:** Regardless of which API you use, you MUST include:

1. **Prominent Disclaimer** stating:
   - This is not a substitute for professional medical advice
   - Always consult a healthcare provider
   - In emergencies, call emergency services

2. **Terms of Service** covering:
   - No medical advice guarantee
   - Accuracy limitations
   - User responsibility

3. **Privacy Policy** addressing:
   - Health data handling
   - HIPAA compliance (if applicable)
   - Data retention policies

4. **Liability Waiver**
   - Limit platform liability
   - User acknowledgment of terms

---

## 🛡️ Legal Considerations

### Medical Liability:

- ❗ Symptom checkers may create medical liability
- 💼 Consider professional liability insurance
- ⚖️ Consult with legal counsel
- 📋 Include comprehensive disclaimers
- 🔒 Ensure GDPR/HIPAA compliance

### Regulatory Compliance:

**USA:** FDA may regulate medical software
**Europe:** CE marking may be required for medical devices
**Other regions:** Check local medical device regulations

---

## 💡 Next Steps

1. **Choose your path:**
   - [ ] ApiMedic for production (recommended)
   - [ ] Demo mode for testing/MVP
   - [ ] Custom OpenAI solution
   - [ ] Wait for Infermedica to become available

2. **Update documentation:**
   - [ ] Add medical disclaimers
   - [ ] Create terms of service
   - [ ] Update privacy policy

3. **Test thoroughly:**
   - [ ] Try various symptom combinations
   - [ ] Verify triage accuracy
   - [ ] Check edge cases

4. **Get legal review:**
   - [ ] Have lawyer review disclaimers
   - [ ] Verify regulatory compliance
   - [ ] Address liability concerns

---

## 📞 Support Resources

- **ApiMedic Support:** support@priaid.ch
- **OpenAI Support:** https://help.openai.com/
- **Healthcare IT Lawyers:** (Consult local legal services)
- **FDA Medical Device Guidance:** https://www.fda.gov/medical-devices

---

## 🎉 Your Current Setup

Your symptom checker is **LIVE in DEMO MODE** at `http://localhost:3001`

**Features Working:**
- ✅ Symptom search with auto-complete
- ✅ Multi-symptom selection
- ✅ Mock diagnosis results
- ✅ Triage recommendations
- ✅ Beautiful UI
- ✅ Responsive design

**To test:** Visit http://localhost:3001 and scroll to "Check Your Symptoms"

---

**Questions?** See INFERMEDICA_INTEGRATION_GUIDE.md or contact support for your chosen API provider.
