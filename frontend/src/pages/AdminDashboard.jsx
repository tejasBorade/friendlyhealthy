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
  TrendingUp,
  Settings,
  Assessment,
} from '@mui/icons-material';
import api from '../services/api';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalDoctors: 0,
    totalPatients: 0,
    totalAppointments: 0,
    completedAppointments: 0,
    revenue: 0,
  });
  const [recentActivity, setRecentActivity] = useState([]);

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
      const completed = appointments.filter(a => a.status === 'completed');
      const revenue = completed.length * 150; // Assuming avg consultation fee

      setStats({
        totalUsers: appointments.length > 0 ? new Set(appointments.map(a => a.patient_id)).size + doctors.length : doctors.length,
        totalDoctors: doctors.length,
        totalPatients: appointments.length > 0 ? new Set(appointments.map(a => a.patient_id)).size : 0,
        totalAppointments: appointments.length,
        completedAppointments: completed.length,
        revenue: revenue,
      });

      setRecentActivity(appointments.slice(0, 5));
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
          Admin Dashboard
        </Typography>
        <Typography variant="body1" color="textSecondary">
          System overview and management
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Users"
            value={stats.totalUsers}
            icon={People}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Doctors"
            value={stats.totalDoctors}
            icon={LocalHospital}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Patients"
            value={stats.totalPatients}
            icon={People}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Appointments"
            value={stats.totalAppointments}
            icon={CalendarToday}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Completed"
            value={stats.completedAppointments}
            icon={Assessment}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Revenue"
            value={`$${stats.revenue}`}
            icon={TrendingUp}
            color="error"
          />
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Recent Activity</Typography>
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
            {recentActivity.length > 0 ? (
              recentActivity.map((appointment) => (
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
                  No activity found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Paper>

      {/* Admin Actions */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" mb={2}>System Management</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              variant="contained"
              fullWidth
              startIcon={<People />}
              onClick={() => navigate('/appointments')}
            >
              Manage Users
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              variant="contained"
              fullWidth
              startIcon={<LocalHospital />}
              onClick={() => navigate('/doctors')}
            >
              Manage Doctors
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              variant="contained"
              fullWidth
              startIcon={<Assessment />}
              onClick={() => navigate('/reports')}
            >
              View Reports
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              variant="contained"
              fullWidth
              startIcon={<Settings />}
              onClick={() => navigate('/billing')}
            >
              Settings
            </Button>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
}
