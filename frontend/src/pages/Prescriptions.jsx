import React, { useState, useEffect } from 'react';
import {
  Box, Container, Typography, Paper, Card, CardContent, Chip, 
  Grid, Divider, Avatar, CircularProgress, Alert, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, Button, List, ListItem,
  ListItemIcon, ListItemText
} from '@mui/material';
import {
  Description as PrescriptionIcon,
  LocalHospital as HospitalIcon,
  Person as PersonIcon,
  CalendarMonth as CalendarIcon,
  Medication as MedicationIcon,
  AccessTime as TimeIcon,
  Visibility as ViewIcon,
  Download as DownloadIcon,
  LocalPharmacy as PharmacyIcon
} from '@mui/icons-material';
import api from '../services/api';

const Prescriptions = () => {
  const [prescriptions, setPrescriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPrescription, setSelectedPrescription] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [detailsLoading, setDetailsLoading] = useState(false);

  useEffect(() => {
    fetchPrescriptions();
  }, []);

  const fetchPrescriptions = async () => {
    try {
      const response = await api.get('/prescriptions');
      setPrescriptions(response.data.prescriptions || []);
    } catch (err) {
      setError('Failed to load prescriptions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (prescription) => {
    setDetailsOpen(true);
    setDetailsLoading(true);
    try {
      const response = await api.get(`/prescriptions/${prescription.id}`);
      setSelectedPrescription(response.data.prescription);
    } catch (err) {
      console.error(err);
      setSelectedPrescription(prescription);
    } finally {
      setDetailsLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-IN', {
      year: 'numeric', month: 'short', day: 'numeric'
    });
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress sx={{ color: '#10b981' }} />
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 50%, #a7f3d0 100%)', py: 4 }}>
      <Container maxWidth="lg">
        {/* Header */}
        <Paper sx={{ p: 3, mb: 4, borderRadius: '20px', background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
              <PrescriptionIcon sx={{ fontSize: 30, color: 'white' }} />
            </Avatar>
            <Box>
              <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
                My Prescriptions
              </Typography>
              <Typography sx={{ color: 'rgba(255,255,255,0.8)' }}>
                View and manage your medical prescriptions
              </Typography>
            </Box>
          </Box>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>{error}</Alert>
        )}

        {/* Prescriptions List */}
        {prescriptions.length === 0 ? (
          <Paper sx={{ p: 6, textAlign: 'center', borderRadius: '20px' }}>
            <PharmacyIcon sx={{ fontSize: 80, color: '#10b981', opacity: 0.5, mb: 2 }} />
            <Typography variant="h6" color="textSecondary">
              No prescriptions found
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Your prescriptions will appear here after your doctor visits
            </Typography>
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {prescriptions.map((prescription) => (
              <Grid item xs={12} md={6} key={prescription.id}>
                <Card sx={{ 
                  borderRadius: '20px', 
                  boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 30px rgba(16, 185, 129, 0.15)'
                  }
                }}>
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: '#ecfdf5' }}>
                          <PrescriptionIcon sx={{ color: '#10b981' }} />
                        </Avatar>
                        <Box>
                          <Typography variant="h6" sx={{ fontWeight: 600 }}>
                            {prescription.diagnosis || 'Prescription'}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            ID: {prescription.id}
                          </Typography>
                        </Box>
                      </Box>
                      <IconButton 
                        onClick={() => handleViewDetails(prescription)}
                        sx={{ bgcolor: '#ecfdf5', '&:hover': { bgcolor: '#d1fae5' } }}
                      >
                        <ViewIcon sx={{ color: '#10b981' }} />
                      </IconButton>
                    </Box>

                    <Divider sx={{ my: 2 }} />

                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <PersonIcon sx={{ color: '#10b981', fontSize: 20 }} />
                        <Typography variant="body2">
                          Dr. {prescription.doctor_first_name} {prescription.doctor_last_name}
                        </Typography>
                        {prescription.specialization && (
                          <Chip 
                            label={prescription.specialization} 
                            size="small" 
                            sx={{ bgcolor: '#ecfdf5', color: '#059669', fontSize: '0.7rem' }} 
                          />
                        )}
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CalendarIcon sx={{ color: '#10b981', fontSize: 20 }} />
                        <Typography variant="body2">
                          {formatDate(prescription.appointment_date)}
                        </Typography>
                      </Box>
                    </Box>

                    {prescription.notes && (
                      <Box sx={{ mt: 2, p: 2, bgcolor: '#f0fdf4', borderRadius: '12px' }}>
                        <Typography variant="body2" color="textSecondary">
                          {prescription.notes}
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Prescription Details Dialog */}
        <Dialog 
          open={detailsOpen} 
          onClose={() => setDetailsOpen(false)} 
          maxWidth="md" 
          fullWidth
          PaperProps={{ sx: { borderRadius: '20px' } }}
        >
          <DialogTitle sx={{ 
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', 
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            gap: 2
          }}>
            <PrescriptionIcon />
            Prescription Details
          </DialogTitle>
          <DialogContent sx={{ mt: 2 }}>
            {detailsLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress sx={{ color: '#10b981' }} />
              </Box>
            ) : selectedPrescription && (
              <Box>
                <Grid container spacing={3} sx={{ mb: 3 }}>
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, borderRadius: '12px', bgcolor: '#f0fdf4' }}>
                      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                        Doctor
                      </Typography>
                      <Typography variant="body1" fontWeight={600}>
                        Dr. {selectedPrescription.doctor_first_name} {selectedPrescription.doctor_last_name}
                      </Typography>
                      {selectedPrescription.specialization && (
                        <Typography variant="body2" color="textSecondary">
                          {selectedPrescription.specialization}
                        </Typography>
                      )}
                    </Paper>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, borderRadius: '12px', bgcolor: '#f0fdf4' }}>
                      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                        Visit Date
                      </Typography>
                      <Typography variant="body1" fontWeight={600}>
                        {formatDate(selectedPrescription.appointment_date)}
                      </Typography>
                      {selectedPrescription.appointment_reason && (
                        <Typography variant="body2" color="textSecondary">
                          {selectedPrescription.appointment_reason}
                        </Typography>
                      )}
                    </Paper>
                  </Grid>
                </Grid>

                <Paper sx={{ p: 2, borderRadius: '12px', mb: 3 }}>
                  <Typography variant="subtitle1" fontWeight={600} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <HospitalIcon sx={{ color: '#10b981' }} /> Diagnosis
                  </Typography>
                  <Typography variant="body1">
                    {selectedPrescription.diagnosis || 'Not specified'}
                  </Typography>
                </Paper>

                {selectedPrescription.medications && selectedPrescription.medications.length > 0 && (
                  <Paper sx={{ p: 2, borderRadius: '12px', mb: 3 }}>
                    <Typography variant="subtitle1" fontWeight={600} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <MedicationIcon sx={{ color: '#10b981' }} /> Medications
                    </Typography>
                    <List>
                      {selectedPrescription.medications.map((med, index) => (
                        <ListItem key={med.id || index} sx={{ 
                          bgcolor: '#f0fdf4', 
                          borderRadius: '12px', 
                          mb: 1,
                          flexDirection: 'column',
                          alignItems: 'flex-start'
                        }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', mb: 1 }}>
                            <ListItemIcon sx={{ minWidth: 40 }}>
                              <PharmacyIcon sx={{ color: '#10b981' }} />
                            </ListItemIcon>
                            <ListItemText 
                              primary={med.medication_name}
                              secondary={`${med.dosage} - ${med.frequency}`}
                              primaryTypographyProps={{ fontWeight: 600 }}
                            />
                            <Chip label={med.duration} size="small" sx={{ bgcolor: '#10b981', color: 'white' }} />
                          </Box>
                          {med.instructions && (
                            <Typography variant="body2" color="textSecondary" sx={{ pl: 5 }}>
                              ⚠️ {med.instructions}
                            </Typography>
                          )}
                        </ListItem>
                      ))}
                    </List>
                  </Paper>
                )}

                {selectedPrescription.notes && (
                  <Paper sx={{ p: 2, borderRadius: '12px' }}>
                    <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                      Notes
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {selectedPrescription.notes}
                    </Typography>
                  </Paper>
                )}
              </Box>
            )}
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button 
              onClick={() => setDetailsOpen(false)}
              sx={{ borderRadius: '12px' }}
            >
              Close
            </Button>
            <Button 
              variant="contained"
              startIcon={<DownloadIcon />}
              sx={{ 
                borderRadius: '12px',
                bgcolor: '#10b981',
                '&:hover': { bgcolor: '#059669' }
              }}
            >
              Download PDF
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
};

export default Prescriptions;

