import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Grid, 
  Paper, 
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import api from '../services/api';
import { format } from 'date-fns';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import MedicationIcon from '@mui/icons-material/Medication';
import AssignmentIcon from '@mui/icons-material/Assignment';
import SearchIcon from '@mui/icons-material/Search';

const PatientDashboard = () => {
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  const [stats, setStats] = useState({
    upcomingAppointments: 0,
    prescriptions: 0,
    reports: 0,
  });
  const [recentAppointments, setRecentAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.patientId) {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      // Fetch appointments for this patient
      const response = await api.get('/appointments', {
        params: { patientId: user.patientId }
      });
      
      const appointments = response.data.appointments || [];
      
      // Calculate stats
      const upcoming = appointments.filter(apt => {
        const aptDate = new Date(apt.appointment_date);
        return aptDate >= new Date() && apt.status === 'scheduled';
      });
      
      setStats({
        upcomingAppointments: upcoming.length,
        prescriptions: 0, // TODO: Implement prescriptions endpoint
        reports: 0, // TODO: Implement reports endpoint
      });
      
      // Get next 5 appointments
      const recent = appointments
        .sort((a, b) => new Date(b.appointment_date) - new Date(a.appointment_date))
        .slice(0, 5);
      
      setRecentAppointments(recent);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (date) => {
    try {
      return format(new Date(date), 'MMM dd, yyyy');
    } catch {
      return date;
    }
  };

  const statusColors = {
    scheduled: 'primary',
    completed: 'success',
    cancelled: 'error',
    'no-show': 'warning',
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Welcome, {user?.email?.split('@')[0]}
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, display: 'flex', alignItems: 'center' }}>
            <CalendarTodayIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Upcoming Appointments
              </Typography>
              <Typography variant="h4">{stats.upcomingAppointments}</Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, display: 'flex', alignItems: 'center' }}>
            <MedicationIcon sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Active Prescriptions
              </Typography>
              <Typography variant="h4">{stats.prescriptions}</Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, display: 'flex', alignItems: 'center' }}>
            <AssignmentIcon sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Medical Reports
              </Typography>
              <Typography variant="h4">{stats.reports}</Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={() => navigate('/doctors')}
            >
              Find Doctors
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              onClick={() => navigate('/appointments')}
            >
              My Appointments
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              onClick={() => navigate('/prescriptions')}
            >
              Prescriptions
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              onClick={() => navigate('/medical-history')}
            >
              Medical History
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Recent Appointments */}
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Recent Appointments</Typography>
          <Button onClick={() => navigate('/appointments')}>View All</Button>
        </Box>

        {loading ? (
          <Typography>Loading...</Typography>
        ) : recentAppointments.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography color="text.secondary" gutterBottom>
              No appointments found
            </Typography>
            <Button
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={() => navigate('/doctors')}
              sx={{ mt: 2 }}
            >
              Book Your First Appointment
            </Button>
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Time</TableCell>
                  <TableCell>Doctor</TableCell>
                  <TableCell>Specialization</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentAppointments.map((appointment) => (
                  <TableRow key={appointment.id}>
                    <TableCell>{formatDate(appointment.appointment_date)}</TableCell>
                    <TableCell>{appointment.appointment_time}</TableCell>
                    <TableCell>
                      Dr. {appointment.doctor_first_name} {appointment.doctor_last_name}
                    </TableCell>
                    <TableCell>{appointment.specialization}</TableCell>
                    <TableCell>
                      <Chip 
                        label={appointment.status} 
                        color={statusColors[appointment.status] || 'default'} 
                        size="small" 
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Container>
  );
};

export default PatientDashboard;
