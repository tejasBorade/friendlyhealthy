import React, { useState, useEffect } from 'react';
import {
  Box, Container, Typography, Paper, Card, CardContent, Chip, 
  Grid, Divider, Avatar, CircularProgress, Alert, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, Button,
  Tabs, Tab, TextField, InputAdornment
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
  FolderShared as RecordsIcon,
  Science as LabIcon,
  MonitorHeart as DiagnosticIcon,
  Description as ReportIcon,
  CalendarMonth as CalendarIcon,
  Person as PersonIcon,
  Search as SearchIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
  LocalHospital as HospitalIcon,
  Bloodtype as BloodIcon
} from '@mui/icons-material';
import api from '../services/api';
import DoctorSidebar from '../components/DoctorSidebar';

const MedicalHistory = () => {
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  const [records, setRecords] = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  useEffect(() => {
    fetchRecords();
  }, [user]);

  const fetchRecords = async () => {
    try {
      const response = await api.get('/medical-records');
      setRecords(response.data.records || []);

      if (user?.role === 'doctor') {
        const appointmentRes = await api.get('/appointments', {
          params: user?.doctorId ? { doctorId: user.doctorId } : {},
        });
        const appointments = appointmentRes.data.appointments || [];
        const patientMap = new Map();
        appointments.forEach((appointment) => {
          if (!appointment.patient_id || patientMap.has(appointment.patient_id)) {
            return;
          }
          patientMap.set(appointment.patient_id, {
            id: appointment.patient_id,
            firstName: appointment.patient_first_name || 'Patient',
            lastName: appointment.patient_last_name || appointment.patient_id,
          });
        });
        setPatients(Array.from(patientMap.values()));
      }
    } catch (err) {
      setError('Failed to load medical records');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-IN', {
      year: 'numeric', month: 'short', day: 'numeric'
    });
  };

  const getRecordIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'lab test': return <LabIcon sx={{ color: '#10b981' }} />;
      case 'diagnostic': return <DiagnosticIcon sx={{ color: '#7c3aed' }} />;
      default: return <ReportIcon sx={{ color: '#f59e0b' }} />;
    }
  };

  const getRecordTypeColor = (type) => {
    switch (type?.toLowerCase()) {
      case 'lab test': return { bg: '#dcfce7', color: '#16a34a' };
      case 'diagnostic': return { bg: '#ede9fe', color: '#7c3aed' };
      default: return { bg: '#fef3c7', color: '#d97706' };
    }
  };

  const filteredRecords = records.filter(record => {
    const matchesSearch = record.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          record.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTab = tabValue === 0 || 
                       (tabValue === 1 && record.record_type === 'Lab Test') ||
                       (tabValue === 2 && record.record_type === 'Diagnostic');
    return matchesSearch && matchesTab;
  });

  if (loading) {
    const loadingContent = (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress sx={{ color: '#10b981' }} />
      </Box>
    );

    if (user?.role === 'doctor') {
      return (
        <Box sx={{ display: 'flex', minHeight: '100vh', background: '#f9fafb' }}>
          <DoctorSidebar activeItem="My Patients" />
          <Box sx={{ ml: { xs: 0, md: '280px' }, flex: 1 }}>
            {loadingContent}
          </Box>
        </Box>
      );
    }

    return loadingContent;
  }

  const pageContent = (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 50%, #a7f3d0 100%)', py: 4 }}>
      <Container maxWidth="lg">
        {/* Header */}
        <Paper sx={{ p: 3, mb: 4, borderRadius: '20px', background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
              <RecordsIcon sx={{ fontSize: 30, color: 'white' }} />
            </Avatar>
            <Box>
              <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
                {user?.role === 'doctor' ? 'My Patients' : 'Medical Records'}
              </Typography>
              <Typography sx={{ color: 'rgba(255,255,255,0.8)' }}>
                {user?.role === 'doctor'
                  ? 'Open patient files to update history, reports, and prescriptions'
                  : 'View your test results and medical reports'}
              </Typography>
            </Box>
          </Box>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>{error}</Alert>
        )}

        {user?.role === 'doctor' && (
          <Paper sx={{ p: 3, mb: 3, borderRadius: '20px' }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 700 }}>
              Patient Directory
            </Typography>
            {patients.length === 0 ? (
              <Alert severity="info">
                No patients found yet. Once appointments are assigned, patients will appear here.
              </Alert>
            ) : (
              <Grid container spacing={2}>
                {patients.map((patient) => (
                  <Grid key={patient.id} item xs={12} sm={6} md={4}>
                    <Card sx={{ borderRadius: '14px' }}>
                      <CardContent>
                        <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                          {patient.firstName} {patient.lastName}
                        </Typography>
                        <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                          ID: {patient.id}
                        </Typography>
                        <Button
                          size="small"
                          variant="contained"
                          onClick={() => navigate(`/doctor/patient/${patient.id}`)}
                        >
                          Open File
                        </Button>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Paper>
        )}

        {/* Search and Filter */}
        <Paper sx={{ p: 2, mb: 4, borderRadius: '20px' }}>
          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 2, alignItems: 'center' }}>
            <TextField
              placeholder="Search records..."
              size="small"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              sx={{ 
                flex: 1, 
                '& .MuiOutlinedInput-root': { borderRadius: '12px' }
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon sx={{ color: '#10b981' }} />
                  </InputAdornment>
                )
              }}
            />
            <Tabs 
              value={tabValue} 
              onChange={(e, v) => setTabValue(v)}
              sx={{
                '& .MuiTab-root': { 
                  borderRadius: '12px',
                  minHeight: '40px',
                  textTransform: 'none'
                },
                '& .Mui-selected': { 
                  bgcolor: '#ecfdf5',
                  color: '#10b981 !important'
                }
              }}
            >
              <Tab label="All Records" />
              <Tab label="Lab Tests" icon={<LabIcon sx={{ fontSize: 18 }} />} iconPosition="start" />
              <Tab label="Diagnostics" icon={<DiagnosticIcon sx={{ fontSize: 18 }} />} iconPosition="start" />
            </Tabs>
          </Box>
        </Paper>

        {/* Records Grid */}
        {filteredRecords.length === 0 ? (
          <Paper sx={{ p: 6, textAlign: 'center', borderRadius: '20px' }}>
            <RecordsIcon sx={{ fontSize: 80, color: '#10b981', opacity: 0.5, mb: 2 }} />
            <Typography variant="h6" color="textSecondary">
              No medical records found
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Your test results and medical reports will appear here
            </Typography>
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {filteredRecords.map((record) => {
              const typeStyle = getRecordTypeColor(record.record_type);
              return (
                <Grid item xs={12} md={6} lg={4} key={record.id}>
                  <Card sx={{ 
                    borderRadius: '20px', 
                    boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    height: '100%',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 30px rgba(16, 185, 129, 0.15)'
                    }
                  }}>
                    <CardContent sx={{ p: 3 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Avatar sx={{ bgcolor: typeStyle.bg }}>
                            {getRecordIcon(record.record_type)}
                          </Avatar>
                          <Box>
                            <Chip 
                              label={record.record_type} 
                              size="small"
                              sx={{ 
                                bgcolor: typeStyle.bg, 
                                color: typeStyle.color,
                                fontWeight: 600,
                                fontSize: '0.7rem'
                              }} 
                            />
                          </Box>
                        </Box>
                        <IconButton 
                          onClick={() => { setSelectedRecord(record); setDetailsOpen(true); }}
                          sx={{ bgcolor: '#ecfdf5', '&:hover': { bgcolor: '#d1fae5' } }}
                        >
                          <ViewIcon sx={{ color: '#10b981' }} />
                        </IconButton>
                      </Box>

                      <Typography variant="h6" fontWeight={600} gutterBottom>
                        {record.title}
                      </Typography>

                      <Divider sx={{ my: 2 }} />

                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CalendarIcon sx={{ color: '#10b981', fontSize: 20 }} />
                          <Typography variant="body2">
                            {formatDate(record.test_date)}
                          </Typography>
                        </Box>
                        {record.doctor_first_name && (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <PersonIcon sx={{ color: '#10b981', fontSize: 20 }} />
                            <Typography variant="body2">
                              Dr. {record.doctor_first_name} {record.doctor_last_name}
                            </Typography>
                          </Box>
                        )}
                      </Box>

                      {record.result_summary && (
                        <Box sx={{ mt: 2, p: 2, bgcolor: '#f0fdf4', borderRadius: '12px' }}>
                          <Typography variant="body2" color="textSecondary" sx={{
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden'
                          }}>
                            {record.result_summary}
                          </Typography>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        )}

        {/* Record Details Dialog */}
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
            <ReportIcon />
            Medical Record Details
          </DialogTitle>
          <DialogContent sx={{ mt: 2 }}>
            {selectedRecord && (
              <Box>
                <Grid container spacing={3} sx={{ mb: 3 }}>
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, borderRadius: '12px', bgcolor: '#f0fdf4' }}>
                      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                        Test Type
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getRecordIcon(selectedRecord.record_type)}
                        <Typography variant="body1" fontWeight={600}>
                          {selectedRecord.record_type}
                        </Typography>
                      </Box>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, borderRadius: '12px', bgcolor: '#f0fdf4' }}>
                      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                        Test Date
                      </Typography>
                      <Typography variant="body1" fontWeight={600}>
                        {formatDate(selectedRecord.test_date)}
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>

                <Paper sx={{ p: 3, borderRadius: '12px', mb: 3 }}>
                  <Typography variant="h5" fontWeight={600} gutterBottom>
                    {selectedRecord.title}
                  </Typography>
                  {selectedRecord.description && (
                    <Typography variant="body2" color="textSecondary" paragraph>
                      {selectedRecord.description}
                    </Typography>
                  )}
                </Paper>

                {selectedRecord.doctor_first_name && (
                  <Paper sx={{ p: 2, borderRadius: '12px', mb: 3 }}>
                    <Typography variant="subtitle1" fontWeight={600} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <HospitalIcon sx={{ color: '#10b981' }} /> Ordered By
                    </Typography>
                    <Typography variant="body1">
                      Dr. {selectedRecord.doctor_first_name} {selectedRecord.doctor_last_name}
                      {selectedRecord.specialization && ` (${selectedRecord.specialization})`}
                    </Typography>
                  </Paper>
                )}

                {selectedRecord.result_summary && (
                  <Paper sx={{ p: 3, borderRadius: '12px', bgcolor: '#f0fdf4' }}>
                    <Typography variant="subtitle1" fontWeight={600} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <BloodIcon sx={{ color: '#10b981' }} /> Results Summary
                    </Typography>
                    <Typography variant="body1">
                      {selectedRecord.result_summary}
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
              Download Report
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );

  if (user?.role === 'doctor') {
    return (
      <Box sx={{ display: 'flex', minHeight: '100vh', background: '#f9fafb' }}>
        <DoctorSidebar activeItem="My Patients" />
        <Box sx={{ ml: { xs: 0, md: '280px' }, flex: 1 }}>
          {pageContent}
        </Box>
      </Box>
    );
  }

  return pageContent;
};

export default MedicalHistory;

