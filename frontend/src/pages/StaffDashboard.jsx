import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import {
  People,
  LocalHospital,
  CalendarToday,
  Assignment,
} from '@mui/icons-material';
import api from '../services/api';

export default function StaffDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalPatients: 0,
    totalDoctors: 0,
    todayAppointments: 0,
    pendingAppointments: 0,
  });
  const [recentAppointments, setRecentAppointments] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch appointments
      const appointmentsRes = await api.get('/appointments');
      const appointments = appointmentsRes.data.appointments || [];
      
      // Fetch doctors
      const doctorsRes = await api.get('/doctors');
      const doctors = doctorsRes.data.doctors || [];

      // Calculate stats
      const today = new Date().toISOString().split('T')[0];
      const todayAppts = appointments.filter(a => a.appointment_date === today);
      const pending = appointments.filter(a => a.status === 'scheduled');

      setStats({
        totalPatients: appointments.length > 0 ? new Set(appointments.map(a => a.patient_id)).size : 0,
        totalDoctors: doctors.length,
        todayAppointments: todayAppts.length,
        pendingAppointments: pending.length,
      });

      setRecentAppointments(appointments.slice(0, 5));
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const StatCard = ({ title, value, icon: Icon, color }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" variant="body2" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
          </Box>
          <Box
            sx={{
              backgroundColor: `${color}.light`,
              borderRadius: '50%',
              p: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Icon sx={{ color: `${color}.main`, fontSize: 40 }} />
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box mb={4}>
        <Typography variant="h4" gutterBottom>
          Staff Dashboard
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Manage appointments, patients, and administrative tasks
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Patients"
            value={stats.totalPatients}
            icon={People}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Doctors"
            value={stats.totalDoctors}
            icon={LocalHospital}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Today's Appointments"
            value={stats.todayAppointments}
            icon={CalendarToday}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Appointments"
            value={stats.pendingAppointments}
            icon={Assignment}
            color="error"
          />
        </Grid>
      </Grid>

      {/* Recent Appointments */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Recent Appointments</Typography>
          <Button
            variant="outlined"
            onClick={() => navigate('/appointments')}
          >
            View All
          </Button>
        </Box>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Patient</TableCell>
              <TableCell>Doctor</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Time</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {recentAppointments.length > 0 ? (
              recentAppointments.map((appointment) => (
                <TableRow key={appointment.id}>
                  <TableCell>
                    {appointment.patient_first_name} {appointment.patient_last_name}
                  </TableCell>
                  <TableCell>
                    {appointment.doctor_first_name} {appointment.doctor_last_name}
                  </TableCell>
                  <TableCell>{appointment.appointment_date}</TableCell>
                  <TableCell>{appointment.appointment_time}</TableCell>
                  <TableCell>
                    <Chip
                      label={appointment.status}
                      color={
                        appointment.status === 'completed' ? 'success' :
                        appointment.status === 'scheduled' ? 'primary' :
                        appointment.status === 'cancelled' ? 'error' : 'default'
                      }
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No appointments found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Paper>

      {/* Quick Actions */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" mb={2}>Quick Actions</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              variant="contained"
              fullWidth
              startIcon={<CalendarToday />}
              onClick={() => navigate('/appointments')}
            >
              Manage Appointments
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              variant="contained"
              fullWidth
              startIcon={<LocalHospital />}
              onClick={() => navigate('/doctors')}
            >
              View Doctors
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              variant="contained"
              fullWidth
              startIcon={<People />}
              onClick={() => navigate('/patients')}
            >
              View Patients
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              variant="contained"
              fullWidth
              startIcon={<Assignment />}
              onClick={() => navigate('/reports')}
            >
              Reports
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
}
