import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Alert,
  IconButton,
} from '@mui/material';
import { LocalizationProvider, DatePicker, TimePicker } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { useSelector } from 'react-redux';
import api from '../services/api';
import { toast } from 'react-toastify';
import { format } from 'date-fns';

const statusColors = {
  scheduled: 'primary',
  completed: 'success',
  cancelled: 'error',
  'no-show': 'warning',
};

const Appointments = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [bookingDialog, setBookingDialog] = useState(false);
  const [doctors, setDoctors] = useState([]);
  const [patients, setPatients] = useState([]);
  const [selectedDoctor, setSelectedDoctor] = useState('');
  const [selectedPatient, setSelectedPatient] = useState('');
  const [appointmentDate, setAppointmentDate] = useState(null);
  const [appointmentTime, setAppointmentTime] = useState(null);
  const [reason, setReason] = useState('');
  const [statusDialogOpen, setStatusDialogOpen] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [newStatus, setNewStatus] = useState('');
  
  const { user } = useSelector((state) => state.auth);

  useEffect(() => {
    fetchAppointments();
    if (user?.role === 'staff' || user?.role === 'admin') {
      fetchDoctors();
      fetchPatients();
    }
  }, [user]);

  const fetchAppointments = async () => {
    try {
      const params = {};
      
      // Filter based on role
      if (user?.role === 'patient' && user?.patientId) {
        params.patientId = user.patientId;
      } else if (user?.role === 'doctor' && user?.doctorId) {
        params.doctorId = user.doctorId;
      }
      // Staff and admin see all appointments

      const response = await api.get('/appointments', { params });
      setAppointments(response.data.appointments || []);
    } catch (error) {
      console.error('Error fetching appointments:', error);
      toast.error('Failed to load appointments');
    } finally {
      setLoading(false);
    }
  };

  const fetchDoctors = async () => {
    try {
      const response = await api.get('/doctors');
      setDoctors(response.data.doctors || []);
    } catch (error) {
      console.error('Error fetching doctors:', error);
    }
  };

  const fetchPatients = async () => {
    try {
      // You'll need to implement this endpoint
      // const response = await api.get('/patients');
      // setPatients(response.data.patients || []);
    } catch (error) {
      console.error('Error fetching patients:', error);
    }
  };

  const handleCreateAppointment = () => {
    setBookingDialog(true);
    setSelectedDoctor('');
    setSelectedPatient('');
    setAppointmentDate(null);
    setAppointmentTime(null);
    setReason('');
  };

  const handleConfirmBooking = async () => {
    if (!appointmentDate || !appointmentTime || !reason || !selectedDoctor || !selectedPatient) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      const formattedDate = appointmentDate.toISOString().split('T')[0];
      const formattedTime = appointmentTime.toTimeString().split(' ')[0].substring(0, 5);

      await api.post('/appointments', {
        patientId: selectedPatient,
        doctorId: selectedDoctor,
        appointmentDate: formattedDate,
        appointmentTime: formattedTime,
        reason,
      });

      toast.success('Appointment created successfully!');
      setBookingDialog(false);
      fetchAppointments();
    } catch (error) {
      console.error('Booking error:', error);
      toast.error(error.response?.data?.message || 'Failed to create appointment');
    }
  };

  const handleUpdateStatus = (appointment) => {
    setSelectedAppointment(appointment);
    setNewStatus(appointment.status);
    setStatusDialogOpen(true);
  };

  const handleConfirmStatusUpdate = async () => {
    try {
      await api.patch(`/appointments/${selectedAppointment.id}`, {
        status: newStatus,
      });

      toast.success('Appointment status updated');
      setStatusDialogOpen(false);
      fetchAppointments();
    } catch (error) {
      console.error('Update error:', error);
      toast.error('Failed to update appointment');
    }
  };

  const handleCancelAppointment = async (id) => {
    if (!window.confirm('Are you sure you want to cancel this appointment?')) {
      return;
    }

    try {
      await api.delete(`/appointments/${id}`);
      toast.success('Appointment cancelled');
      fetchAppointments();
    } catch (error) {
      console.error('Cancel error:', error);
      toast.error('Failed to cancel appointment');
    }
  };

  const formatDate = (date) => {
    try {
      return format(new Date(date), 'MMM dd, yyyy');
    } catch {
      return date;
    }
  };

  const canModifyAppointment = () => {
    return ['staff', 'admin', 'doctor'].includes(user?.role);
  };

  const canCreateAppointment = () => {
    return ['staff', 'admin'].includes(user?.role);
  };

  if (loading) {
    return (
      <Container sx={{ mt: 4, textAlign: 'center' }}>
        <Typography>Loading appointments...</Typography>
      </Container>
    );
  }

  return (
    <Container sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          {user?.role === 'patient' ? 'My Appointments' : 
           user?.role === 'doctor' ? 'Patient Appointments' : 
           'All Appointments'}
        </Typography>
        {canCreateAppointment() && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateAppointment}
          >
            New Appointment
          </Button>
        )}
      </Box>

      {appointments.length === 0 ? (
        <Alert severity="info">No appointments found</Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Time</TableCell>
                {user?.role !== 'patient' && <TableCell>Patient</TableCell>}
                {user?.role !== 'doctor' && <TableCell>Doctor</TableCell>}
                <TableCell>Specialization</TableCell>
                <TableCell>Reason</TableCell>
                <TableCell>Status</TableCell>
                {canModifyAppointment() && <TableCell>Actions</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {appointments.map((appointment) => (
                <TableRow key={appointment.id}>
                  <TableCell>{formatDate(appointment.appointment_date)}</TableCell>
                  <TableCell>{appointment.appointment_time}</TableCell>
                  {user?.role !== 'patient' && (
                    <TableCell>
                      {appointment.patient_first_name} {appointment.patient_last_name}
                    </TableCell>
                  )}
                  {user?.role !== 'doctor' && (
                    <TableCell>
                      Dr. {appointment.doctor_first_name} {appointment.doctor_last_name}
                    </TableCell>
                  )}
                  <TableCell>{appointment.specialization}</TableCell>
                  <TableCell>{appointment.reason}</TableCell>
                  <TableCell>
                    <Chip
                      label={appointment.status}
                      color={statusColors[appointment.status] || 'default'}
                      size="small"
                    />
                  </TableCell>
                  {canModifyAppointment() && (
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleUpdateStatus(appointment)}
                        disabled={appointment.status === 'cancelled'}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleCancelAppointment(appointment.id)}
                        disabled={appointment.status === 'cancelled'}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create Appointment Dialog (Staff/Admin) */}
      <Dialog open={bookingDialog} onClose={() => setBookingDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Appointment</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              select
              fullWidth
              label="Select Doctor"
              value={selectedDoctor}
              onChange={(e) => setSelectedDoctor(e.target.value)}
            >
              {doctors.map((doctor) => (
                <MenuItem key={doctor.id} value={doctor.id}>
                  Dr. {doctor.first_name} {doctor.last_name} - {doctor.specialization}
                </MenuItem>
              ))}
            </TextField>

            <TextField
              fullWidth
              label="Patient ID"
              type="number"
              value={selectedPatient}
              onChange={(e) => setSelectedPatient(e.target.value)}
              helperText="Enter the patient ID"
            />

            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Appointment Date"
                value={appointmentDate}
                onChange={setAppointmentDate}
                minDate={new Date()}
                slotProps={{ textField: { fullWidth: true } }}
              />
              
              <TimePicker
                label="Appointment Time"
                value={appointmentTime}
                onChange={setAppointmentTime}
                slotProps={{ textField: { fullWidth: true } }}
              />
            </LocalizationProvider>

            <TextField
              fullWidth
              multiline
              rows={4}
              label="Reason for Visit"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBookingDialog(false)}>Cancel</Button>
          <Button onClick={handleConfirmBooking} variant="contained">
            Create Appointment
          </Button>
        </DialogActions>
      </Dialog>

      {/* Update Status Dialog */}
      <Dialog open={statusDialogOpen} onClose={() => setStatusDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Update Appointment Status</DialogTitle>
        <DialogContent>
          <TextField
            select
            fullWidth
            label="Status"
            value={newStatus}
            onChange={(e) => setNewStatus(e.target.value)}
            sx={{ mt: 2 }}
          >
            <MenuItem value="scheduled">Scheduled</MenuItem>
            <MenuItem value="completed">Completed</MenuItem>
            <MenuItem value="cancelled">Cancelled</MenuItem>
            <MenuItem value="no-show">No Show</MenuItem>
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStatusDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleConfirmStatusUpdate} variant="contained">
            Update
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Appointments;
