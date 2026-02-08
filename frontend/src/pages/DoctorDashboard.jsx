import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Grid, 
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box,
  Button,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import api from '../services/api';
import { format } from 'date-fns';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import PeopleIcon from '@mui/icons-material/People';
import PendingActionsIcon from '@mui/icons-material/PendingActions';

const DoctorDashboard = () => {
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  const [stats, setStats] = useState({
    todayAppointments: 0,
    totalAppointments: 0,
    totalPatients: 0,
    pendingAppointments: 0,
  });
  const [upcomingAppointments, setUpcomingAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    if (user?.doctorId) {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      // Fetch appointments for this doctor
      const response = await api.get('/appointments', {
        params: { doctorId: user.doctorId }
      });
      
      const appointments = response.data.appointments || [];
      const today = new Date().toISOString().split('T')[0];
      
      // Calculate stats
      const todayApps = appointments.filter(apt => apt.appointment_date.includes(today));
      const pending = appointments.filter(apt => apt.status === 'scheduled');
      const uniquePatients = new Set(appointments.map(apt => apt.patient_id));
      
      setStats({
        todayAppointments: todayApps.length,
        totalAppointments: appointments.length,
        totalPatients: uniquePatients.size,
        pendingAppointments: pending.length,
      });
      
      // Get upcoming appointments (next 7 days, scheduled only)
      const upcoming = appointments
        .filter(apt => {
          const aptDate = new Date(apt.appointment_date);
          const daysAhead = (aptDate - new Date()) / (1000 * 60 * 60 * 24);
          return apt.status === 'scheduled' && daysAhead >= 0 && daysAhead <= 7;
        })
        .sort((a, b) => new Date(a.appointment_date) - new Date(b.appointment_date))
        .slice(0, 5);
      
      setUpcomingAppointments(upcoming);
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

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Doctor Dashboard
      </Typography>
      
      {/* Stats Cards */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 3, display: 'flex', alignItems: 'center' }}>
            <CalendarTodayIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Today's Appointments
              </Typography>
              <Typography variant="h4">{stats.todayAppointments}</Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 3, display: 'flex', alignItems: 'center' }}>
            <CalendarTodayIcon sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Total Appointments
              </Typography>
              <Typography variant="h4">{stats.totalAppointments}</Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 3, display: 'flex', alignItems: 'center' }}>
            <PeopleIcon sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Total Patients
              </Typography>
              <Typography variant="h4">{stats.totalPatients}</Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 3, display: 'flex', alignItems: 'center' }}>
            <PendingActionsIcon sx={{ fontSize: 40, color: 'warning.main', mr: 2 }} />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Pending Consultations
              </Typography>
              <Typography variant="h4">{stats.pendingAppointments}</Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Upcoming Appointments */}
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Upcoming Appointments</Typography>
          <Button onClick={() => navigate('/appointments')}>View All</Button>
        </Box>

        {loading ? (
          <Typography>Loading...</Typography>
        ) : upcomingAppointments.length === 0 ? (
          <Typography color="text.secondary">No upcoming appointments</Typography>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Time</TableCell>
                  <TableCell>Patient</TableCell>
                  <TableCell>Reason</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {upcomingAppointments.map((appointment) => (
                  <TableRow key={appointment.id}>
                    <TableCell>{formatDate(appointment.appointment_date)}</TableCell>
                    <TableCell>{appointment.appointment_time}</TableCell>
                    <TableCell>
                      <Button 
                        variant="text" 
                        onClick={() => navigate(`/doctor/patient/${appointment.patient_id}`)}
                        sx={{ textTransform: 'none' }}
                      >
                        {appointment.patient_first_name} {appointment.patient_last_name}
                      </Button>
                    </TableCell>
                    <TableCell>{appointment.reason}</TableCell>
                    <TableCell>
                      <Chip label={appointment.status} color="primary" size="small" />
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

export default DoctorDashboard;
