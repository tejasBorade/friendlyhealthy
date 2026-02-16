import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  MenuItem,
  Button,
  Box,
  Avatar,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
} from '@mui/material';
import { LocalizationProvider, DatePicker, TimePicker } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import SearchIcon from '@mui/icons-material/Search';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import { useSelector } from 'react-redux';
import api from '../services/api';
import { toast } from 'react-toastify';
import AdminSidebar from '../components/AdminSidebar';

const specializations = [
  'All Specializations',
  'Cardiology',
  'Neurology',
  'Pediatrics',
  'Orthopedics',
  'Dermatology',
  'Psychiatry',
  'Obstetrics & Gynecology',
  'Oncology',
  'Endocrinology',
  'Gastroenterology',
  'Pulmonology',
  'Urology',
  'Ophthalmology',
  'ENT (Otolaryngology)',
  'Rheumatology',
  'Nephrology',
  'Hematology',
  'Infectious Disease',
  'Allergy & Immunology',
  'Emergency Medicine',
];

const DoctorSearch = () => {
  const [doctors, setDoctors] = useState([]);
  const [filteredDoctors, setFilteredDoctors] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSpecialization, setSelectedSpecialization] = useState('All Specializations');
  const [loading, setLoading] = useState(true);
  const [bookingDialog, setBookingDialog] = useState(false);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [appointmentDate, setAppointmentDate] = useState(null);
  const [appointmentTime, setAppointmentTime] = useState(null);
  const [reason, setReason] = useState('');
  const [patientId, setPatientId] = useState(null);
  const [manualPatientId, setManualPatientId] = useState('');
  
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.role === 'admin';

  useEffect(() => {
    fetchDoctors();
    if (user?.role === 'patient') {
      fetchPatientId();
    }
  }, []);

  useEffect(() => {
    filterDoctors();
  }, [searchTerm, selectedSpecialization, doctors]);

  const fetchDoctors = async () => {
    try {
      const response = await api.get('/doctors');
      setDoctors(response.data.doctors || []);
      setFilteredDoctors(response.data.doctors || []);
    } catch (error) {
      console.error('Error fetching doctors:', error);
      toast.error('Failed to load doctors');
    } finally {
      setLoading(false);
    }
  };

  const fetchPatientId = async () => {
    try {
      const response = await api.get('/auth/me');
      if (response.data.user?.patientId) {
        setPatientId(response.data.user.patientId);
      }
    } catch (error) {
      console.error('Error fetching patient info:', error);
    }
  };

  const filterDoctors = () => {
    let filtered = doctors;

    if (selectedSpecialization !== 'All Specializations') {
      filtered = filtered.filter(doc => doc.specialization === selectedSpecialization);
    }

    if (searchTerm) {
      filtered = filtered.filter(doc =>
        `${doc.first_name} ${doc.last_name}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.specialization.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredDoctors(filtered);
  };

  const handleBookAppointment = (doctor) => {
    setSelectedDoctor(doctor);
    setBookingDialog(true);
    setAppointmentDate(null);
    setAppointmentTime(null);
    setReason('');
    setManualPatientId('');
  };

  const handleConfirmBooking = async () => {
    if (!appointmentDate || !appointmentTime || !reason) {
      toast.error('Please fill in all fields');
      return;
    }

    const bookingPatientId = user?.role === 'patient' ? patientId : Number(manualPatientId);

    if (!bookingPatientId) {
      toast.error(
        user?.role === 'patient'
          ? 'Patient profile not found. Please contact support.'
          : 'Please enter a valid patient ID.'
      );
      return;
    }

    try {
      const formattedDate = appointmentDate.toISOString().split('T')[0];
      const formattedTime = appointmentTime.toTimeString().split(' ')[0].substring(0, 5);

      await api.post('/appointments', {
        patientId: bookingPatientId,
        doctorId: selectedDoctor.id,
        appointmentDate: formattedDate,
        appointmentTime: formattedTime,
        reason,
      });

      toast.success('Appointment booked successfully!');
      setBookingDialog(false);
      setSelectedDoctor(null);
    } catch (error) {
      console.error('Booking error:', error);
      toast.error(error.response?.data?.message || 'Failed to book appointment');
    }
  };

  if (loading) {
    const loadingContent = (
      <Box sx={{ 
        minHeight: '100vh', 
        background: '#f9fafb',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Typography sx={{ color: '#6b7280' }}>Loading doctors...</Typography>
      </Box>
    );

    if (isAdmin) {
      return (
        <Box sx={{ display: 'flex', minHeight: '100vh', background: '#f9fafb' }}>
          <AdminSidebar activeItem="Doctors" />
          <Box sx={{ ml: { xs: 0, md: '280px' }, flex: 1 }}>
            {loadingContent}
          </Box>
        </Box>
      );
    }

    return loadingContent;
  }

  const pageContent = (
    <Box sx={{ minHeight: '100vh', background: '#f9fafb' }}>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #10b981 0%, #5eead4 100%)',
          py: { xs: 6, md: 10 },
          px: 3,
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.1) 2px, transparent 2px)',
            backgroundSize: '40px 40px',
          },
        }}
      >
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
          <Typography
            sx={{
              fontSize: { xs: 32, md: 48 },
              fontWeight: 800,
              color: 'white',
              textAlign: 'center',
              mb: 2,
            }}
          >
            Find the Best <span style={{ opacity: 0.9 }}>Doctors</span> Near You
          </Typography>
          <Typography
            sx={{
              fontSize: { xs: 16, md: 20 },
              color: 'rgba(255,255,255,0.9)',
              textAlign: 'center',
              mb: 5,
            }}
          >
            Search by specialization, book appointments instantly
          </Typography>

          {/* Search Box */}
          <Box
            sx={{
              maxWidth: 800,
              mx: 'auto',
              background: 'white',
              borderRadius: '60px',
              p: 1.5,
              display: 'flex',
              flexDirection: { xs: 'column', sm: 'row' },
              gap: 1.5,
              boxShadow: '0 25px 70px rgba(0, 0, 0, 0.2)',
            }}
          >
            <TextField
              fullWidth
              placeholder="Search by name or specialization..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: '#9ca3af' }} />,
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  border: 'none',
                  borderRadius: '50px',
                  '& fieldset': { border: 'none' },
                },
              }}
            />
            <TextField
              select
              value={selectedSpecialization}
              onChange={(e) => setSelectedSpecialization(e.target.value)}
              sx={{
                minWidth: { xs: '100%', sm: 220 },
                '& .MuiOutlinedInput-root': {
                  borderRadius: '50px',
                  background: '#f3f4f6',
                  '& fieldset': { border: 'none' },
                },
              }}
            >
              {specializations.map((spec) => (
                <MenuItem key={spec} value={spec}>
                  {spec}
                </MenuItem>
              ))}
            </TextField>
          </Box>
        </Container>
      </Box>

      {/* Results Section */}
      <Container maxWidth="lg" sx={{ py: 5 }}>
        <Typography 
          sx={{ 
            fontSize: 24, 
            fontWeight: 700, 
            color: '#111827', 
            mb: 4,
            display: 'flex',
            alignItems: 'center',
            gap: 1,
          }}
        >
          <LocalHospitalIcon sx={{ color: '#10b981' }} />
          {filteredDoctors.length} Doctors Available
        </Typography>

        {filteredDoctors.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Box sx={{ fontSize: 60, mb: 2 }}>🔍</Box>
            <Typography sx={{ color: '#6b7280', fontSize: 18 }}>
              No doctors found matching your criteria
            </Typography>
          </Box>
        ) : (
          <Grid container spacing={3}>
            {filteredDoctors.map((doctor) => (
              <Grid item xs={12} md={6} lg={4} key={doctor.id}>
                <Card 
                  sx={{ 
                    height: '100%', 
                    display: 'flex', 
                    flexDirection: 'column',
                    borderRadius: 5,
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                    transition: 'all 0.4s ease',
                    overflow: 'hidden',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: '0 15px 40px rgba(16, 185, 129, 0.2)',
                    },
                  }}
                >
                  {/* Card Header */}
                  <Box
                    sx={{
                      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                      p: 3,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 2,
                    }}
                  >
                    <Avatar 
                      sx={{ 
                        width: 70, 
                        height: 70, 
                        bgcolor: 'white',
                        color: '#10b981',
                        fontSize: 24,
                        fontWeight: 700,
                      }}
                    >
                      {doctor.first_name?.[0]}{doctor.last_name?.[0]}
                    </Avatar>
                    <Box>
                      <Typography sx={{ color: 'white', fontWeight: 700, fontSize: 20 }}>
                        Dr. {doctor.first_name} {doctor.last_name}
                      </Typography>
                      <Chip 
                        label={doctor.specialization || 'General'} 
                        size="small"
                        sx={{
                          mt: 1,
                          bgcolor: 'rgba(255,255,255,0.2)',
                          color: 'white',
                          fontWeight: 600,
                          backdropFilter: 'blur(10px)',
                        }}
                      />
                    </Box>
                  </Box>

                  {/* Card Body */}
                  <CardContent sx={{ flexGrow: 1, p: 3 }}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography sx={{ color: '#9ca3af', fontSize: 13, minWidth: 100 }}>Qualification</Typography>
                        <Typography sx={{ color: '#374151', fontWeight: 500 }}>{doctor.qualification || 'MBBS'}</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography sx={{ color: '#9ca3af', fontSize: 13, minWidth: 100 }}>Experience</Typography>
                        <Typography sx={{ color: '#374151', fontWeight: 500 }}>{doctor.experience_years || 0} years</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography sx={{ color: '#9ca3af', fontSize: 13, minWidth: 100 }}>Fee</Typography>
                        <Typography sx={{ color: '#10b981', fontWeight: 700, fontSize: 18 }}>
                          ${doctor.consultation_fee || 0}
                        </Typography>
                      </Box>
                      {doctor.city && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography sx={{ color: '#9ca3af', fontSize: 13, minWidth: 100 }}>Location</Typography>
                          <Typography sx={{ color: '#374151', fontWeight: 500 }}>{doctor.city}</Typography>
                        </Box>
                      )}
                    </Box>
                    
                    <Chip 
                      label={doctor.is_available !== 0 ? "Available" : "Unavailable"}
                      size="small"
                      sx={{
                        mt: 2,
                        fontWeight: 600,
                        bgcolor: doctor.is_available !== 0 ? '#d1fae5' : '#fee2e2',
                        color: doctor.is_available !== 0 ? '#059669' : '#dc2626',
                      }}
                    />
                  </CardContent>

                  {/* Card Footer */}
                  <Box sx={{ p: 3, pt: 0 }}>
                    <Button
                      fullWidth
                      variant="contained"
                      onClick={() => handleBookAppointment(doctor)}
                      disabled={doctor.is_available === 0}
                      sx={{
                        py: 1.5,
                        borderRadius: 3,
                        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                        fontWeight: 600,
                        boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)',
                        '&:hover': {
                          boxShadow: '0 8px 25px rgba(16, 185, 129, 0.4)',
                        },
                        '&.Mui-disabled': {
                          background: '#e5e7eb',
                        },
                      }}
                    >
                      Book Appointment
                    </Button>
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Container>

      {/* Booking Dialog */}
      <Dialog 
        open={bookingDialog} 
        onClose={() => setBookingDialog(false)} 
        maxWidth="sm" 
        fullWidth
        PaperProps={{
          sx: { borderRadius: 5 }
        }}
      >
        <DialogTitle sx={{ 
          fontSize: 24, 
          fontWeight: 700, 
          color: '#111827',
          pb: 1,
        }}>
          Book Appointment
        </DialogTitle>
        <Box sx={{ px: 3, pb: 1 }}>
          <Typography sx={{ color: '#6b7280' }}>
            with Dr. {selectedDoctor?.first_name} {selectedDoctor?.last_name}
          </Typography>
        </Box>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Appointment Date"
                value={appointmentDate}
                onChange={setAppointmentDate}
                minDate={new Date()}
                slotProps={{ 
                  textField: { 
                    fullWidth: true, 
                    sx: { 
                      mb: 3,
                      '& .MuiOutlinedInput-root': { borderRadius: 3 }
                    } 
                  } 
                }}
              />
              
              <TimePicker
                label="Appointment Time"
                value={appointmentTime}
                onChange={setAppointmentTime}
                slotProps={{ 
                  textField: { 
                    fullWidth: true, 
                    sx: { 
                      mb: 3,
                      '& .MuiOutlinedInput-root': { borderRadius: 3 }
                    } 
                  } 
                }}
              />
            </LocalizationProvider>

            {user?.role !== 'patient' && (
              <TextField
                fullWidth
                type="number"
                label="Patient ID"
                value={manualPatientId}
                onChange={(e) => setManualPatientId(e.target.value)}
                placeholder="Enter patient ID"
                sx={{
                  mb: 3,
                  '& .MuiOutlinedInput-root': { borderRadius: 3 },
                }}
              />
            )}

            <TextField
              fullWidth
              multiline
              rows={4}
              label="Reason for Visit"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Please describe your symptoms or reason for consultation..."
              sx={{
                '& .MuiOutlinedInput-root': { borderRadius: 3 }
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 0 }}>
          <Button 
            onClick={() => setBookingDialog(false)}
            sx={{ 
              color: '#6b7280',
              borderRadius: 3,
              px: 3,
            }}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleConfirmBooking} 
            variant="contained"
            sx={{
              borderRadius: 3,
              px: 4,
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)',
            }}
          >
            Confirm Booking
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );

  if (isAdmin) {
    return (
      <Box sx={{ display: 'flex', minHeight: '100vh', background: '#f9fafb' }}>
        <AdminSidebar activeItem="Doctors" />
        <Box sx={{ ml: { xs: 0, md: '280px' }, flex: 1 }}>
          {pageContent}
        </Box>
      </Box>
    );
  }

  return pageContent;
};

export default DoctorSearch;
