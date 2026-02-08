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
  
  const { user } = useSelector((state) => state.auth);

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
  };

  const handleConfirmBooking = async () => {
    if (!appointmentDate || !appointmentTime || !reason) {
      toast.error('Please fill in all fields');
      return;
    }

    if (!patientId) {
      toast.error('Patient profile not found. Please contact support.');
      return;
    }

    try {
      const formattedDate = appointmentDate.toISOString().split('T')[0];
      const formattedTime = appointmentTime.toTimeString().split(' ')[0].substring(0, 5);

      await api.post('/appointments', {
        patientId,
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
    return (
      <Container sx={{ mt: 4, textAlign: 'center' }}>
        <Typography>Loading doctors...</Typography>
      </Container>
    );
  }

  return (
    <Container sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <LocalHospitalIcon sx={{ mr: 2, fontSize: 40, color: 'primary.main' }} />
        Find & Book Doctors
      </Typography>

      {/* Search and Filter */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search by name or specialization..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />,
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              select
              label="Specialization"
              value={selectedSpecialization}
              onChange={(e) => setSelectedSpecialization(e.target.value)}
            >
              {specializations.map((spec) => (
                <MenuItem key={spec} value={spec}>
                  {spec}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        </Grid>
      </Box>

      {/* Results */}
      <Typography variant="h6" gutterBottom>
        {filteredDoctors.length} Doctors Available
      </Typography>

      {filteredDoctors.length === 0 ? (
        <Alert severity="info">No doctors found matching your criteria</Alert>
      ) : (
        <Grid container spacing={3}>
          {filteredDoctors.map((doctor) => (
            <Grid item xs={12} md={6} lg={4} key={doctor.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56, mr: 2 }}>
                      {doctor.first_name[0]}{doctor.last_name[0]}
                    </Avatar>
                    <Box>
                      <Typography variant="h6">
                        Dr. {doctor.first_name} {doctor.last_name}
                      </Typography>
                      <Chip 
                        label={doctor.specialization} 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                      />
                    </Box>
                  </Box>

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Qualification:</strong> {doctor.qualification}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Experience:</strong> {doctor.experience_years} years
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Consultation Fee:</strong> ${doctor.consultation_fee}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Contact:</strong> {doctor.phone}
                  </Typography>
                  
                  {doctor.is_available ? (
                    <Chip label="Available" color="success" size="small" sx={{ mt: 1 }} />
                  ) : (
                    <Chip label="Unavailable" color="error" size="small" sx={{ mt: 1 }} />
                  )}
                </CardContent>

                <Box sx={{ p: 2, pt: 0 }}>
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={() => handleBookAppointment(doctor)}
                    disabled={!doctor.is_available || user?.role !== 'patient'}
                  >
                    Book Appointment
                  </Button>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Booking Dialog */}
      <Dialog open={bookingDialog} onClose={() => setBookingDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Book Appointment with Dr. {selectedDoctor?.first_name} {selectedDoctor?.last_name}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Appointment Date"
                value={appointmentDate}
                onChange={setAppointmentDate}
                minDate={new Date()}
                renderInput={(params) => <TextField {...params} fullWidth sx={{ mb: 2 }} />}
                slotProps={{ textField: { fullWidth: true, sx: { mb: 2 } } }}
              />
              
              <TimePicker
                label="Appointment Time"
                value={appointmentTime}
                onChange={setAppointmentTime}
                renderInput={(params) => <TextField {...params} fullWidth sx={{ mb: 2 }} />}
                slotProps={{ textField: { fullWidth: true, sx: { mb: 2 } } }}
              />
            </LocalizationProvider>

            <TextField
              fullWidth
              multiline
              rows={4}
              label="Reason for Visit"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Please describe your symptoms or reason for consultation..."
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBookingDialog(false)}>Cancel</Button>
          <Button onClick={handleConfirmBooking} variant="contained">
            Confirm Booking
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default DoctorSearch;
