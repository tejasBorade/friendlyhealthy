import React, { useEffect, useState } from 'react';
import {
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
  Avatar,
  Card,
  CardContent,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import api from '../services/api';
import { format } from 'date-fns';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import PeopleIcon from '@mui/icons-material/People';
import PendingActionsIcon from '@mui/icons-material/PendingActions';
import EventNoteIcon from '@mui/icons-material/EventNote';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import DoctorSidebar from '../components/DoctorSidebar';

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
    fetchDashboardData();
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      const doctorId = user?.doctorId;
      const response = await api.get('/appointments', {
        params: doctorId ? { doctorId } : {},
      });
      const appointments = response.data.appointments || [];
      const today = new Date().toISOString().split('T')[0];

      const todayApps = appointments.filter((apt) => apt.appointment_date?.includes(today));
      const pending = appointments.filter(
        (apt) => apt.status === 'pending' || apt.status === 'confirmed'
      );
      const uniquePatients = new Set(appointments.map((apt) => apt.patient_id));

      setStats({
        todayAppointments: todayApps.length,
        totalAppointments: appointments.length,
        totalPatients: uniquePatients.size,
        pendingAppointments: pending.length,
      });

      const upcoming = appointments
        .filter((apt) => apt.status === 'pending' || apt.status === 'confirmed')
        .sort(
          (a, b) =>
            new Date(`${a.appointment_date}T${a.appointment_time || '00:00'}`) -
            new Date(`${b.appointment_date}T${b.appointment_time || '00:00'}`)
        )
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
    <Box sx={{ display: 'flex', minHeight: '100vh', background: '#f9fafb' }}>
      <DoctorSidebar activeItem="Dashboard" />

      <Box sx={{ ml: { xs: 0, md: '280px' }, flex: 1, p: 4, overflow: 'auto' }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 700, color: '#111827' }}>
            Welcome Back, Dr. {user?.first_name || 'Doctor'}
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Here is a snapshot of your current appointments and patients.
          </Typography>
        </Box>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card
              sx={{
                borderRadius: '20px',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: 'white',
                boxShadow: '0 10px 30px rgba(16, 185, 129, 0.3)',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.8 }}>
                      Today's Appointments
                    </Typography>
                    <Typography variant="h3" fontWeight={700}>
                      {stats.todayAppointments}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
                    <CalendarTodayIcon sx={{ fontSize: 28 }} />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card
              sx={{
                borderRadius: '20px',
                background: 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)',
                color: 'white',
                boxShadow: '0 10px 30px rgba(124, 58, 237, 0.3)',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.8 }}>
                      Total Appointments
                    </Typography>
                    <Typography variant="h3" fontWeight={700}>
                      {stats.totalAppointments}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
                    <EventNoteIcon sx={{ fontSize: 28 }} />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card
              sx={{
                borderRadius: '20px',
                background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                color: 'white',
                boxShadow: '0 10px 30px rgba(245, 158, 11, 0.3)',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.8 }}>
                      Total Patients
                    </Typography>
                    <Typography variant="h3" fontWeight={700}>
                      {stats.totalPatients}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
                    <PeopleIcon sx={{ fontSize: 28 }} />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card
              sx={{
                borderRadius: '20px',
                background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                color: 'white',
                boxShadow: '0 10px 30px rgba(239, 68, 68, 0.3)',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.8 }}>
                      Pending
                    </Typography>
                    <Typography variant="h3" fontWeight={700}>
                      {stats.pendingAppointments}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
                    <PendingActionsIcon sx={{ fontSize: 28 }} />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Paper sx={{ borderRadius: '20px', overflow: 'hidden' }}>
          <Box
            sx={{
              p: 3,
              borderBottom: '1px solid #e5e7eb',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <Typography variant="h6" fontWeight={600}>
              Upcoming Appointments
            </Typography>
            <Button
              onClick={() => navigate('/doctor/appointments')}
              sx={{
                borderRadius: '12px',
                color: '#10b981',
                '&:hover': { bgcolor: '#ecfdf5' },
              }}
            >
              View All
            </Button>
          </Box>

          {loading ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Typography color="textSecondary">Loading...</Typography>
            </Box>
          ) : upcomingAppointments.length === 0 ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <CheckCircleIcon sx={{ fontSize: 48, color: '#10b981', mb: 1 }} />
              <Typography color="textSecondary">No upcoming appointments</Typography>
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: '#f0fdf4' }}>
                    <TableCell sx={{ fontWeight: 600 }}>Patient</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Time</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Reason</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {upcomingAppointments.map((appointment) => (
                    <TableRow key={appointment.id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Avatar sx={{ bgcolor: '#ecfdf5', color: '#10b981' }}>
                            {(appointment.patient_first_name || 'P')[0]}
                          </Avatar>
                          <Typography fontWeight={500}>
                            {appointment.patient_first_name || 'Patient'}{' '}
                            {appointment.patient_last_name || appointment.patient_id}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{formatDate(appointment.appointment_date)}</TableCell>
                      <TableCell>{appointment.appointment_time}</TableCell>
                      <TableCell>{appointment.reason || '-'}</TableCell>
                      <TableCell>
                        <Chip
                          label={appointment.status}
                          size="small"
                          sx={{
                            bgcolor:
                              appointment.status === 'confirmed' ? '#dcfce7' : '#fef9c3',
                            color:
                              appointment.status === 'confirmed' ? '#16a34a' : '#ca8a04',
                            fontWeight: 600,
                            textTransform: 'capitalize',
                          }}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>
      </Box>
    </Box>
  );
};

export default DoctorDashboard;
