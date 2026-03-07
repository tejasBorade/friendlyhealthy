import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Stepper,
  Step,
  StepLabel,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  Chip,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
} from '@mui/material';
import {
  Search,
  ExpandMore,
  CheckCircle,
  Warning,
  LocalHospital,
  Psychology,
} from '@mui/icons-material';
import axios from 'axios';

const INFERMEDICA_APP_ID = import.meta.env.VITE_INFERMEDICA_APP_ID || 'demo';
const INFERMEDICA_APP_KEY = import.meta.env.VITE_INFERMEDICA_APP_KEY || 'demo';
const USE_DEMO_MODE = INFERMEDICA_APP_ID === 'demo' || !INFERMEDICA_APP_ID || INFERMEDICA_APP_ID === 'your-app-id-here';

// Demo data for testing
const DEMO_SYMPTOMS = [
  { id: 's_1', label: 'Headache', common_name: 'Headache' },
  { id: 's_2', label: 'Fever', common_name: 'High temperature' },
  { id: 's_3', label: 'Cough', common_name: 'Coughing' },
  { id: 's_4', label: 'Sore throat', common_name: 'Throat pain' },
  { id: 's_5', label: 'Runny nose', common_name: 'Nasal discharge' },
  { id: 's_6', label: 'Fatigue', common_name: 'Tiredness' },
  { id: 's_7', label: 'Nausea', common_name: 'Feeling sick' },
  { id: 's_8', label: 'Chest pain', common_name: 'Pain in chest' },
  { id: 's_9', label: 'Shortness of breath', common_name: 'Difficulty breathing' },
  { id: 's_10', label: 'Body aches', common_name: 'Muscle pain' },
  { id: 's_11', label: 'Dizziness', common_name: 'Feeling dizzy' },
  { id: 's_12', label: 'Abdominal pain', common_name: 'Stomach pain' },
];

const SymptomChecker = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [symptoms, setSymptoms] = useState([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [age, setAge] = useState('');
  const [sex, setSex] = useState('male');
  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [diagnosis, setDiagnosis] = useState(null);
  const [error, setError] = useState('');
  const [demoMode] = useState(USE_DEMO_MODE);

  const steps = ['Basic Info', 'Search Symptoms', 'Review & Diagnose'];

  // Search for symptoms
  const searchSymptoms = async (query) => {
    if (!query || query.length < 3) {
      setSymptoms([]);
      return;
    }

    setSearchLoading(true);
    setError('');

    try {
      if (demoMode) {
        // Demo mode: Filter local symptoms
        await new Promise(resolve => setTimeout(resolve, 300)); // Simulate API delay
        const filtered = DEMO_SYMPTOMS.filter(s => 
          s.label.toLowerCase().includes(query.toLowerCase()) ||
          s.common_name.toLowerCase().includes(query.toLowerCase())
        );
        setSymptoms(filtered);
      } else {
        // Real API mode
        const response = await axios.get('https://api.infermedica.com/v3/search', {
          params: { phrase: query, max_results: 8 },
          headers: {
            'App-Id': INFERMEDICA_APP_ID,
            'App-Key': INFERMEDICA_APP_KEY,
            'Content-Type': 'application/json',
          },
        });
        setSymptoms(response.data || []);
      }
    } catch (err) {
      console.error('Error searching symptoms:', err);
      setError('Failed to search symptoms. Please check your API credentials.');
    } finally {
      setSearchLoading(false);
    }
  };

  // Debounced search
  React.useEffect(() => {
    const timer = setTimeout(() => {
      if (activeStep === 1) {
        searchSymptoms(searchTerm);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm, activeStep]);

  // Add symptom to selected list
  const addSymptom = (symptom) => {
    if (!selectedSymptoms.find((s) => s.id === symptom.id)) {
      setSelectedSymptoms([...selectedSymptoms, { ...symptom, choice_id: 'present' }]);
      setSearchTerm('');
      setSymptoms([]);
    }
  };

  // Remove symptom from selected list
  const removeSymptom = (symptomId) => {
    setSelectedSymptoms(selectedSymptoms.filter((s) => s.id !== symptomId));
  };

  // Get diagnosis from Infermedica
  const getDiagnosis = async () => {
    if (selectedSymptoms.length === 0) {
      setError('Please select at least one symptom');
      return;
    }

    setLoading(true);
    setError('');

    try {
      if (demoMode) {
        // Demo mode: Generate mock diagnosis
        await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API delay
        
        // Determine triage based on symptoms
        const emergencySymptoms = ['chest pain', 'shortness of breath'];
        const hasEmergency = selectedSymptoms.some(s => 
          emergencySymptoms.some(es => s.label.toLowerCase().includes(es))
        );
        
        const mockDiagnosis = {
          triage: {
            triage_level: hasEmergency ? 'emergency' : 
                         selectedSymptoms.length > 3 ? 'consultation_24' : 'consultation',
            description: hasEmergency 
              ? 'Your symptoms require immediate medical attention. Please visit the emergency room or call emergency services.'
              : selectedSymptoms.length > 3
              ? 'Based on your symptoms, we recommend consulting a doctor within 24 hours.'
              : 'Schedule a consultation with a healthcare provider to discuss your symptoms.'
          },
          conditions: [
            {
              id: 'c_1',
              name: 'Common Cold',
              common_name: 'Common Cold',
              probability: 0.75
            },
            {
              id: 'c_2',
              name: 'Influenza',
              common_name: 'Flu',
              probability: 0.65
            },
            {
              id: 'c_3',
              name: 'Viral Infection',
              common_name: 'Viral Infection',
              probability: 0.45
            },
            {
              id: 'c_4',
              name: 'Sinusitis',
              common_name: 'Sinus Infection',
              probability: 0.30
            },
            {
              id: 'c_5',
              name: 'Allergic Rhinitis',
              common_name: 'Allergies',
              probability: 0.25
            }
          ].sort((a, b) => b.probability - a.probability)
        };
        
        setDiagnosis(mockDiagnosis);
      } else {
        // Real API mode
        const evidence = selectedSymptoms.map((symptom) => ({
          id: symptom.id,
          choice_id: symptom.choice_id,
          source: 'initial',
        }));

        const response = await axios.post(
          'https://api.infermedica.com/v3/diagnosis',
          {
            sex: sex,
            age: { value: parseInt(age) },
            evidence: evidence,
            extras: {
              enable_triage_5: true,
            },
          },
          {
            headers: {
              'App-Id': INFERMEDICA_APP_ID,
              'App-Key': INFERMEDICA_APP_KEY,
              'Content-Type': 'application/json',
            },
          }
        );

        setDiagnosis(response.data);
      }
      setActiveStep(3);
    } catch (err) {
      console.error('Error getting diagnosis:', err);
      setError('Failed to get diagnosis. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Reset the checker
  const reset = () => {
    setActiveStep(0);
    setSearchTerm('');
    setSymptoms([]);
    setSelectedSymptoms([]);
    setAge('');
    setSex('male');
    setDiagnosis(null);
    setError('');
  };

  const handleNext = () => {
    if (activeStep === 0) {
      if (!age || parseInt(age) < 0 || parseInt(age) > 120) {
        setError('Please enter a valid age (0-120)');
        return;
      }
      setError('');
    }
    if (activeStep === 1 && selectedSymptoms.length === 0) {
      setError('Please select at least one symptom');
      return;
    }
    setError('');
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
    setError('');
  };

  const getTriageColor = (level) => {
    const colors = {
      emergency: '#ef4444',
      emergency_ambulance: '#dc2626',
      consultation_24: '#f97316',
      consultation: '#f59e0b',
      self_care: '#10b981',
    };
    return colors[level] || '#6b7280';
  };

  const getTriageLabel = (level) => {
    const labels = {
      emergency: 'Emergency - Seek immediate care',
      emergency_ambulance: 'Call ambulance immediately',
      consultation_24: 'Consult doctor within 24 hours',
      consultation: 'Schedule a consultation',
      self_care: 'Self-care recommended',
    };
    return labels[level] || level;
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 4,
        maxWidth: 900,
        mx: 'auto',
        borderRadius: 4,
        background: 'linear-gradient(135deg, #ffffff 0%, #f9fafb 100%)',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Psychology sx={{ fontSize: 40, color: '#10b981' }} />
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, color: '#111827' }}>
            AI Symptom Checker
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {demoMode ? 'Demo Mode - For Testing Purposes' : 'Powered by Infermedica Medical Intelligence'}
          </Typography>
        </Box>
      </Box>

      {demoMode && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>Demo Mode Active:</strong> Currently using simulated data for testing. 
            To use real medical AI, obtain API credentials from an alternative service (see documentation).
          </Typography>
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Step 0: Basic Info */}
      {activeStep === 0 && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <TextField
            fullWidth
            label="Age"
            type="number"
            value={age}
            onChange={(e) => setAge(e.target.value)}
            InputProps={{ inputProps: { min: 0, max: 120 } }}
            helperText="Enter your age (0-120 years)"
          />

          <FormControl component="fieldset">
            <FormLabel component="legend">Sex</FormLabel>
            <RadioGroup row value={sex} onChange={(e) => setSex(e.target.value)}>
              <FormControlLabel value="male" control={<Radio />} label="Male" />
              <FormControlLabel value="female" control={<Radio />} label="Female" />
            </RadioGroup>
          </FormControl>

          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
            <Button
              variant="contained"
              onClick={handleNext}
              sx={{
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                px: 4,
              }}
            >
              Next
            </Button>
          </Box>
        </Box>
      )}

      {/* Step 1: Search Symptoms */}
      {activeStep === 1 && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <TextField
            fullWidth
            label="Search Symptoms"
            placeholder="E.g., headache, fever, cough..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <Search sx={{ color: '#9ca3af', mr: 1 }} />,
              endAdornment: searchLoading && <CircularProgress size={20} />,
            }}
            helperText="Type at least 3 characters to search"
          />

          {/* Search Results */}
          {symptoms.length > 0 && (
            <Paper sx={{ maxHeight: 200, overflow: 'auto', p: 1 }}>
              {symptoms.map((symptom) => (
                <Box
                  key={symptom.id}
                  onClick={() => addSymptom(symptom)}
                  sx={{
                    p: 1.5,
                    cursor: 'pointer',
                    borderRadius: 2,
                    '&:hover': { backgroundColor: '#f3f4f6' },
                  }}
                >
                  <Typography variant="body1">{symptom.label}</Typography>
                  {symptom.common_name && (
                    <Typography variant="caption" color="text.secondary">
                      {symptom.common_name}
                    </Typography>
                  )}
                </Box>
              ))}
            </Paper>
          )}

          {/* Selected Symptoms */}
          <Box>
            <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
              Selected Symptoms ({selectedSymptoms.length})
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {selectedSymptoms.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No symptoms selected yet
                </Typography>
              ) : (
                selectedSymptoms.map((symptom) => (
                  <Chip
                    key={symptom.id}
                    label={symptom.label || symptom.common_name}
                    onDelete={() => removeSymptom(symptom.id)}
                    color="primary"
                    sx={{ fontWeight: 500 }}
                  />
                ))
              )}
            </Box>
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
            <Button onClick={handleBack}>Back</Button>
            <Button
              variant="contained"
              onClick={handleNext}
              disabled={selectedSymptoms.length === 0}
              sx={{
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                px: 4,
              }}
            >
              Next
            </Button>
          </Box>
        </Box>
      )}

      {/* Step 2: Review & Diagnose */}
      {activeStep === 2 && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <Alert severity="info" icon={<LocalHospital />}>
            <Typography variant="subtitle2" fontWeight={600}>
              Review Your Information
            </Typography>
            <Typography variant="body2">
              Age: {age} years | Sex: {sex === 'male' ? 'Male' : 'Female'}
            </Typography>
          </Alert>

          <Box>
            <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
              Your Symptoms:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {selectedSymptoms.map((symptom) => (
                <Chip
                  key={symptom.id}
                  icon={<CheckCircle />}
                  label={symptom.label || symptom.common_name}
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
            <Button onClick={handleBack}>Back</Button>
            <Button
              variant="contained"
              onClick={getDiagnosis}
              disabled={loading}
              sx={{
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                px: 4,
              }}
            >
              {loading ? <CircularProgress size={24} /> : 'Get Diagnosis'}
            </Button>
          </Box>
        </Box>
      )}

      {/* Step 3: Results */}
      {activeStep === 3 && diagnosis && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Triage Level */}
          {diagnosis.triage && (
            <Alert
              severity={
                diagnosis.triage.triage_level.includes('emergency')
                  ? 'error'
                  : diagnosis.triage.triage_level === 'consultation_24'
                  ? 'warning'
                  : 'info'
              }
              icon={<Warning />}
              sx={{
                borderLeft: `4px solid ${getTriageColor(diagnosis.triage.triage_level)}`,
              }}
            >
              <Typography variant="h6" fontWeight={700}>
                {getTriageLabel(diagnosis.triage.triage_level)}
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                {diagnosis.triage.description}
              </Typography>
            </Alert>
          )}

          {/* Possible Conditions */}
          {diagnosis.conditions && diagnosis.conditions.length > 0 && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 700 }}>
                Possible Conditions
              </Typography>
              {diagnosis.conditions.slice(0, 5).map((condition, index) => (
                <Accordion key={condition.id} sx={{ mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                      <Chip
                        label={`${(condition.probability * 100).toFixed(0)}%`}
                        size="small"
                        color={index === 0 ? 'primary' : 'default'}
                      />
                      <Typography fontWeight={index === 0 ? 700 : 500}>
                        {condition.common_name || condition.name}
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box>
                      <LinearProgress
                        variant="determinate"
                        value={condition.probability * 100}
                        sx={{ mb: 2, height: 8, borderRadius: 4 }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        Probability: {(condition.probability * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}

          {/* Disclaimer */}
          <Alert severity="warning" sx={{ mt: 2 }}>
            <Typography variant="caption">
              <strong>Important:</strong> This is an AI-powered preliminary assessment and should not
              replace professional medical advice. Please consult with a healthcare provider for an
              accurate diagnosis and treatment plan.
            </Typography>
          </Alert>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
            <Button onClick={reset} variant="outlined">
              Start Over
            </Button>
            <Button
              variant="contained"
              onClick={() => (window.location.href = '/login')}
              sx={{
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                px: 4,
              }}
            >
              Book Appointment
            </Button>
          </Box>
        </Box>
      )}
    </Paper>
  );
};

export default SymptomChecker;
