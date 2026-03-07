import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
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
  Card,
  CardContent,
  Grid,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  InputAdornment,
} from '@mui/material';
import {
  Search,
  CheckCircle,
  Warning,
  LocalHospital,
  Psychology,
  Medication,
  LocalPharmacy,
  Place,
  Phone,
  Star,
  NavigationOutlined,
  Close,
} from '@mui/icons-material';
import axios from 'axios';
import CryptoJS from 'crypto-js';

// API Configuration
const APIMEDIC_USERNAME = import.meta.env.VITE_APIMEDIC_USERNAME || 'demo';
const APIMEDIC_PASSWORD = import.meta.env.VITE_APIMEDIC_PASSWORD || 'demo';
const APIMEDIC_URL = 'https://healthservice.priaid.ch';
const AUTH_URL = 'https://authservice.priaid.ch/login';
const FDA_API_BASE = 'https://api.fda.gov';
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

// Demo mode detection
const USE_DEMO_MODE = APIMEDIC_USERNAME === 'demo' || !APIMEDIC_USERNAME || APIMEDIC_USERNAME === 'your-username';

// Demo data
const DEMO_SYMPTOMS = [
  { ID: 1, Name: 'Headache' },
  { ID: 2, Name: 'Fever' },
  { ID: 3, Name: 'Cough' },
  { ID: 4, Name: 'Sore throat' },
  { ID: 5, Name: 'Runny nose' },
  { ID: 6, Name: 'Fatigue' },
  { ID: 7, Name: 'Nausea' },
  { ID: 8, Name: 'Chest pain' },
  { ID: 9, Name: 'Shortness of breath' },
  { ID: 10, Name: 'Body aches' },
];

const IntegratedHealthFlow = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [authToken, setAuthToken] = useState('');
  
  // User info
  const [age, setAge] = useState('');
  const [sex, setSex] = useState('male');
  const [location, setLocation] = useState(null);
  
  // Symptoms
  const [searchTerm, setSearchTerm] = useState('');
  const [symptoms, setSymptoms] = useState([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  
  // Results
  const [diagnosis, setDiagnosis] = useState(null);
  const [medicines, setMedicines] = useState([]);
  const [nearbyDoctors, setNearbyDoctors] = useState([]);
  
  // UI states
  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [error, setError] = useState('');
  const [demoMode] = useState(USE_DEMO_MODE);

  const steps = ['Your Info', 'Symptoms', 'Diagnosis', 'Medicines', 'Find Doctors'];

  // Get user's location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          console.log('Location access denied:', error);
          // Default to a general location if denied
          setLocation({ lat: 40.7128, lng: -74.0060 }); // NYC as default
        }
      );
    }
  }, []);

  // ApiMedic Authentication
  const getAuthToken = async () => {
    if (demoMode) {
      return 'demo-token';
    }

    try {
      const uri = AUTH_URL;
      const computedHash = CryptoJS.HmacMD5(uri, APIMEDIC_PASSWORD).toString(CryptoJS.enc.Base64);
      
      const response = await axios.post(
        uri,
        {},
        {
          headers: {
            'Authorization': `Bearer ${APIMEDIC_USERNAME}:${computedHash}`,
          },
        }
      );
      
      return response.data.Token;
    } catch (err) {
      console.error('Auth error:', err);
      throw err;
    }
  };

  // Initialize auth token
  useEffect(() => {
    if (!demoMode && !authToken) {
      getAuthToken()
        .then(token => setAuthToken(token))
        .catch(err => {
          console.error('Failed to get auth token:', err);
          setError('Failed to authenticate with ApiMedic. Using demo mode.');
        });
    }
  }, []);

  // Search symptoms (Step 2)
  const searchSymptoms = async (query) => {
    if (!query || query.length < 2) {
      setSymptoms([]);
      return;
    }

    setSearchLoading(true);
    setError('');

    try {
      if (demoMode) {
        await new Promise(resolve => setTimeout(resolve, 300));
        const filtered = DEMO_SYMPTOMS.filter(s => 
          s.Name.toLowerCase().includes(query.toLowerCase())
        );
        setSymptoms(filtered);
      } else {
        const token = authToken || await getAuthToken();
        const response = await axios.get(
          `${APIMEDIC_URL}/symptoms?token=${token}&format=json&language=en-gb`
        );
        const filtered = response.data.filter(s => 
          s.Name.toLowerCase().includes(query.toLowerCase())
        );
        setSymptoms(filtered.slice(0, 8));
      }
    } catch (err) {
      console.error('Error searching symptoms:', err);
      setError('Failed to search symptoms');
    } finally {
      setSearchLoading(false);
    }
  };

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (activeStep === 1 && searchTerm) {
        searchSymptoms(searchTerm);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm, activeStep]);

  // Add symptom
  const addSymptom = (symptom) => {
    if (!selectedSymptoms.find(s => s.ID === symptom.ID)) {
      setSelectedSymptoms([...selectedSymptoms, symptom]);
      setSearchTerm('');
      setSymptoms([]);
    }
  };

  // Remove symptom
  const removeSymptom = (symptomId) => {
    setSelectedSymptoms(selectedSymptoms.filter(s => s.ID !== symptomId));
  };

  // Get diagnosis (Step 3)
  const getDiagnosis = async () => {
    if (selectedSymptoms.length === 0) {
      setError('Please select at least one symptom');
      return;
    }

    setLoading(true);
    setError('');

    try {
      if (demoMode) {
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Demo diagnosis
        const diagnosisData = [
          {
            Issue: { ID: 1, Name: 'Common Cold', Accuracy: 75, ProfName: 'Viral Respiratory Infection' },
            Specialisation: [{ Name: 'General Practice', ID: 15, SpecialistID: 3 }],
          },
          {
            Issue: { ID: 2, Name: 'Influenza', Accuracy: 65, ProfName: 'Flu' },
            Specialisation: [{ Name: 'General Practice', ID: 15, SpecialistID: 3 }],
          },
          {
            Issue: { ID: 3, Name: 'Allergic Rhinitis', Accuracy: 45, ProfName: 'Hay Fever' },
            Specialisation: [{ Name: 'Allergy & Immunology', ID: 23, SpecialistID: 1 }],
          },
        ];
        
        setDiagnosis(diagnosisData);
        setActiveStep(2);
      } else {
        const token = authToken || await getAuthToken();
        const symptomIds = selectedSymptoms.map(s => s.ID);
        const birthYear = new Date().getFullYear() - parseInt(age);
        
        const response = await axios.get(
          `${APIMEDIC_URL}/diagnosis`,
          {
            params: {
              symptoms: JSON.stringify(symptomIds),
              gender: sex,
              year_of_birth: birthYear,
              token: token,
              format: 'json',
              language: 'en-gb',
            },
          }
        );
        
        setDiagnosis(response.data);
        setActiveStep(2);
      }
    } catch (err) {
      console.error('Error getting diagnosis:', err);
      setError('Failed to get diagnosis');
    } finally {
      setLoading(false);
    }
  };

  // Get medicines from OpenFDA (Step 4)
  const getMedicines = async (diseaseName) => {
    setLoading(true);
    setError('');

    try {
      // Search for medicines related to the disease
      const searchTerms = [
        diseaseName,
        diseaseName.split(' ')[0], // First word
      ];

      const medicineResults = [];

      for (const term of searchTerms) {
        try {
          const response = await axios.get(
            `${FDA_API_BASE}/drug/label.json`,
            {
              params: {
                search: `indications_and_usage:"${term}"`,
                limit: 5,
              },
            }
          );

          if (response.data?.results) {
            medicineResults.push(...response.data.results);
          }
        } catch (err) {
          console.log(`No medicines found for: ${term}`);
        }
      }

      // Remove duplicates and format
      const uniqueMedicines = [];
      const seen = new Set();
      
      for (const drug of medicineResults) {
        const brandName = drug.openfda?.brand_name?.[0];
        if (brandName && !seen.has(brandName)) {
          seen.add(brandName);
          uniqueMedicines.push({
            brandName: brandName,
            genericName: drug.openfda?.generic_name?.[0] || 'N/A',
            manufacturer: drug.openfda?.manufacturer_name?.[0] || 'N/A',
            purpose: drug.purpose?.[0] || drug.indications_and_usage?.[0] || 'N/A',
            warnings: drug.warnings?.[0] || 'N/A',
          });
        }
      }

      setMedicines(uniqueMedicines.slice(0, 5));
      setActiveStep(3);
    } catch (err) {
      console.error('Error fetching medicines:', err);
      setError('Could not fetch medicine information');
      setMedicines([]);
      setActiveStep(3);
    } finally {
      setLoading(false);
    }
  };

  // Find nearby doctors using Google Maps (Step 5)
  const findNearbyDoctors = async (specialization) => {
    if (!location) {
      setError('Location not available. Please enable location services.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      if (!GOOGLE_MAPS_API_KEY || GOOGLE_MAPS_API_KEY === 'your-api-key-here') {
        // Demo doctors
        setNearbyDoctors([
          {
            name: 'Dr. Sarah Johnson - General Practice',
            address: '123 Main St, New York, NY 10001',
            rating: 4.8,
            phone: '+1 (555) 123-4567',
            distance: '0.5 miles',
          },
          {
            name: 'Dr. Michael Chen - Family Medicine',
            address: '456 Broadway, New York, NY 10013',
            rating: 4.6,
            phone: '+1 (555) 234-5678',
            distance: '1.2 miles',
          },
          {
            name: 'Dr. Emily Rodriguez - Internal Medicine',
            address: '789 Park Ave, New York, NY 10021',
            rating: 4.9,
            phone: '+1 (555) 345-6789',
            distance: '1.8 miles',
          },
        ]);
        setActiveStep(4);
        setLoading(false);
        return;
      }

      // Use Google Places API
      const query = specialization || 'doctor';
      const response = await axios.get(
        `https://maps.googleapis.com/maps/api/place/nearbysearch/json`,
        {
          params: {
            location: `${location.lat},${location.lng}`,
            radius: 5000, // 5km
            type: 'doctor',
            keyword: query,
            key: GOOGLE_MAPS_API_KEY,
          },
        }
      );

      const doctors = response.data.results.slice(0, 5).map(place => ({
        name: place.name,
        address: place.vicinity,
        rating: place.rating || 'N/A',
        phone: place.formatted_phone_number || 'Call for info',
        placeId: place.place_id,
      }));

      setNearbyDoctors(doctors);
      setActiveStep(4);
    } catch (err) {
      console.error('Error finding doctors:', err);
      setError('Failed to find nearby doctors');
    } finally {
      setLoading(false);
    }
  };

  // Handle next step
  const handleNext = () => {
    if (activeStep === 0) {
      if (!age || parseInt(age) < 1 || parseInt(age) > 120) {
        setError('Please enter a valid age');
        return;
      }
      setError('');
      setActiveStep(1);
    } else if (activeStep === 1) {
      getDiagnosis();
    }
  };

  const handleBack = () => {
    setActiveStep(Math.max(0, activeStep - 1));
    setError('');
  };

  const handleReset = () => {
    setActiveStep(0);
    setSelectedSymptoms([]);
    setDiagnosis(null);
    setMedicines([]);
    setNearbyDoctors([]);
    setError('');
  };

  // Render steps
  const renderStep = () => {
    switch (activeStep) {
      case 0:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Tell us about yourself
            </Typography>
            
            <TextField
              fullWidth
              label="Age"
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              margin="normal"
              required
              inputProps={{ min: 1, max: 120 }}
            />

            <FormControl component="fieldset" margin="normal">
              <FormLabel>Sex</FormLabel>
              <RadioGroup row value={sex} onChange={(e) => setSex(e.target.value)}>
                <FormControlLabel value="male" control={<Radio />} label="Male" />
                <FormControlLabel value="female" control={<Radio />} label="Female" />
              </RadioGroup>
            </FormControl>

            <Box sx={{ mt: 3 }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleNext}
                fullWidth
                sx={{
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  py: 1.5,
                }}
              >
                Next: Select Symptoms
              </Button>
            </Box>
          </Box>
        );

      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Search and select your symptoms
            </Typography>

            {demoMode && (
              <Alert severity="info" sx={{ mb: 2 }}>
                Demo Mode: Using mock ApiMedic data. Sign up at apimedic.com for real diagnoses.
              </Alert>
            )}

            <TextField
              fullWidth
              placeholder="Search symptoms... (e.g., headache, fever)"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
                endAdornment: searchLoading && (
                  <InputAdornment position="end">
                    <CircularProgress size={20} />
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 2 }}
            />

            {/* Search results */}
            {symptoms.length > 0 && (
              <Paper sx={{ mb: 2, maxHeight: 200, overflow: 'auto' }}>
                <List>
                  {symptoms.map((symptom) => (
                    <ListItem
                      key={symptom.ID}
                      button
                      onClick={() => addSymptom(symptom)}
                    >
                      <ListItemIcon>
                        <Psychology color="primary" />
                      </ListItemIcon>
                      <ListItemText primary={symptom.Name} />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            )}

            {/* Selected symptoms */}
            <Typography variant="subtitle2" gutterBottom>
              Selected Symptoms ({selectedSymptoms.length})
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
              {selectedSymptoms.map((symptom) => (
                <Chip
                  key={symptom.ID}
                  label={symptom.Name}
                  onDelete={() => removeSymptom(symptom.ID)}
                  color="primary"
                  icon={<CheckCircle />}
                />
              ))}
            </Box>

            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button onClick={handleBack}>Back</Button>
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={selectedSymptoms.length === 0 || loading}
                fullWidth
                sx={{
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                }}
              >
                {loading ? <CircularProgress size={24} /> : 'Get Diagnosis'}
              </Button>
            </Box>
          </Box>
        );

      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Possible Diagnoses
            </Typography>

            {diagnosis && diagnosis.length > 0 ? (
              <>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Based on your symptoms, here are the most likely conditions:
                </Alert>

                {diagnosis.map((item, idx) => (
                  <Card key={idx} sx={{ mb: 2 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                        <Typography variant="h6">
                          {item.Issue.Name}
                        </Typography>
                        <Chip 
                          label={`${item.Issue.Accuracy}% match`}
                          color={item.Issue.Accuracy > 60 ? 'error' : 'warning'}
                          size="small"
                        />
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Medical Name: {item.Issue.ProfName}
                      </Typography>

                      {item.Specialisation && item.Specialisation.length > 0 && (
                        <Typography variant="body2" color="text.secondary">
                          Specialist: {item.Specialisation[0].Name}
                        </Typography>
                      )}

                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<Medication />}
                        onClick={() => getMedicines(item.Issue.Name)}
                        sx={{ mt: 2 }}
                      >
                        Find Medicines
                      </Button>
                    </CardContent>
                  </Card>
                ))}

                <Alert severity="warning" sx={{ mt: 2 }}>
                  This is not a medical diagnosis. Always consult with healthcare professionals.
                </Alert>
              </>
            ) : (
              <Alert severity="info">
                No diagnosis data available
              </Alert>
            )}
          </Box>
        );

      case 3:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Recommended Medicines
            </Typography>

            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : medicines.length > 0 ? (
              <>
                <Alert severity="info" sx={{ mb: 2 }}>
                  These medicines are commonly used for your condition (from FDA database):
                </Alert>

                {medicines.map((medicine, idx) => (
                  <Card key={idx} sx={{ mb: 2 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                        <LocalPharmacy color="primary" />
                        <Typography variant="h6">
                          {medicine.brandName}
                        </Typography>
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Generic: {medicine.genericName}
                      </Typography>
                      
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Manufacturer: {medicine.manufacturer}
                      </Typography>

                      <Divider sx={{ my: 1 }} />

                      <Typography variant="body2" sx={{ mt: 1 }}>
                        <strong>Purpose:</strong> {medicine.purpose.substring(0, 200)}...
                      </Typography>
                    </CardContent>
                  </Card>
                ))}

                <Alert severity="warning" sx={{ mb: 2 }}>
                  Always consult a doctor before taking any medication.
                </Alert>

                <Button
                  variant="contained"
                  fullWidth
                  size="large"
                  startIcon={<LocalHospital />}
                  onClick={() => findNearbyDoctors(diagnosis?.[0]?.Specialisation?.[0]?.Name)}
                  sx={{
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    py: 1.5,
                  }}
                >
                  Find Nearby Doctors
                </Button>
              </>
            ) : (
              <Alert severity="info">
                No medicine information available for this condition
              </Alert>
            )}
          </Box>
        );

      case 4:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Nearby Doctors
            </Typography>

            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : nearbyDoctors.length > 0 ? (
              <>
                <Alert severity="success" sx={{ mb: 2 }}>
                  Found {nearbyDoctors.length} doctors near you:
                </Alert>

                {nearbyDoctors.map((doctor, idx) => (
                  <Card key={idx} sx={{ mb: 2 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="h6" gutterBottom>
                            {doctor.name}
                          </Typography>
                          
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <Place fontSize="small" color="action" />
                            <Typography variant="body2" color="text.secondary">
                              {doctor.address}
                            </Typography>
                          </Box>

                          {doctor.phone && (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                              <Phone fontSize="small" color="action" />
                              <Typography variant="body2" color="text.secondary">
                                {doctor.phone}
                              </Typography>
                            </Box>
                          )}

                          {doctor.rating && (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Star fontSize="small" sx={{ color: '#f59e0b' }} />
                              <Typography variant="body2">
                                {doctor.rating} {doctor.distance && `• ${doctor.distance}`}
                              </Typography>
                            </Box>
                          )}
                        </Box>

                        <IconButton
                          color="primary"
                          onClick={() => {
                            const address = encodeURIComponent(doctor.address);
                            window.open(`https://www.google.com/maps/search/?api=1&query=${address}`, '_blank');
                          }}
                        >
                          <NavigationOutlined />
                        </IconButton>
                      </Box>
                    </CardContent>
                  </Card>
                ))}

                <Button
                  variant="outlined"
                  fullWidth
                  onClick={handleReset}
                  sx={{ mt: 2 }}
                >
                  Start New Diagnosis
                </Button>
              </>
            ) : (
              <Alert severity="info">
                No doctors found nearby
              </Alert>
            )}
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Box
      id="integrated-health-flow"
      sx={{
        py: 8,
        background: 'white',
      }}
    >
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
            <Box
              sx={{
                width: 70,
                height: 70,
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Psychology sx={{ fontSize: 40, color: 'white' }} />
            </Box>
          </Box>
          <Typography
            variant="h3"
            sx={{
              fontWeight: 700,
              color: '#111827',
              mb: 2,
              fontSize: { xs: '2rem', md: '3rem' },
            }}
          >
            Complete Health Analysis
          </Typography>
          <Typography
            variant="h6"
            sx={{
              color: '#6b7280',
              maxWidth: 700,
              mx: 'auto',
            }}
          >
            Symptoms → Diagnosis → Medicines → Nearby Doctors
          </Typography>
        </Box>

        <Paper
          elevation={3}
          sx={{
            p: 4,
            borderRadius: 4,
            maxWidth: 800,
            mx: 'auto',
          }}
        >
          {/* Stepper */}
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Error Message */}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          {/* Step Content */}
          {renderStep()}

          {/* Medical Disclaimer */}
          <Alert severity="warning" sx={{ mt: 3 }}>
            <Typography variant="body2">
              <strong>Medical Disclaimer:</strong> This tool provides preliminary information only
              and does not constitute professional medical advice, diagnosis, or treatment. Always
              seek the advice of your physician or qualified healthcare provider.
            </Typography>
          </Alert>
        </Paper>
      </Container>
    </Box>
  );
};

export default IntegratedHealthFlow;
