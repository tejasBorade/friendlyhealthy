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
  Card,
  CardContent,
  Avatar,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import api from '../services/api';
import { format } from 'date-fns';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import MedicationIcon from '@mui/icons-material/Medication';
import AssignmentIcon from '@mui/icons-material/Assignment';
import SearchIcon from '@mui/icons-material/Search';
import LogoutIcon from '@mui/icons-material/Logout';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PersonIcon from '@mui/icons-material/Person';
import EventNoteIcon from '@mui/icons-material/EventNote';
import DescriptionIcon from '@mui/icons-material/Description';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import ReceiptIcon from '@mui/icons-material/Receipt';

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
    fetchDashboardData();
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/appointments');
      const appointments = response.data.appointments || [];
      
      const upcoming = appointments.filter(apt => {
        const aptDate = new Date(apt.appointment_date);
        return aptDate >= new Date() && apt.status !== 'cancelled';
      });
      
      setStats({
        upcomingAppointments: upcoming.length,
        prescriptions: 0,
        reports: 0,
      });
      
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

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const menuItems = [
    { icon: DashboardIcon, label: 'Dashboard', path: '/patient/dashboard', active: true },
    { icon: LocalHospitalIcon, label: 'Find Doctors', path: '/patient/doctors' },
    { icon: EventNoteIcon, label: 'Appointments', path: '/patient/appointments' },
    { icon: MedicationIcon, label: 'Prescriptions', path: '/patient/prescriptions' },
    { icon: DescriptionIcon, label: 'Reports', path: '/patient/reports' },
    { icon: ReceiptIcon, label: 'Billing', path: '/patient/billing' },
  ];

  const StatCard = ({ title, value, icon: Icon, gradient }) => (
    <Card 
      sx={{ 
        height: '100%',
        borderRadius: 5,
        boxShadow: '0 6px 25px rgba(0, 0, 0, 0.08)',
        transition: 'all 0.4s ease',
        position: 'relative',
        overflow: 'hidden',
        '&:hover': {
          transform: 'translateY(-6px)',
          boxShadow: '0 15px 45px rgba(0, 0, 0, 0.12)',
        },
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography sx={{ color: '#6b7280', fontSize: 14, fontWeight: 500, mb: 1 }}>
              {title}
            </Typography>
            <Typography sx={{ fontSize: 32, fontWeight: 700, color: '#111827' }}>
              {value}
            </Typography>
          </Box>
          <Box
            sx={{
              background: gradient,
              borderRadius: 4,
              p: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Icon sx={{ color: 'white', fontSize: 28 }} />
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', background: '#f9fafb' }}>
      {/* Sidebar */}
      <Box
        sx={{
          width: 280,
          background: 'white',
          borderRight: '1px solid #f3f4f6',
          position: 'fixed',
          height: '100vh',
          display: { xs: 'none', md: 'block' },
        }}
      >
        <Box sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              width: 45,
              height: 45,
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              borderRadius: 3.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 24,
            }}
          >
            🏥
          </Box>
          <Typography
            sx={{
              fontSize: 22,
              fontWeight: 700,
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            HealthCare
          </Typography>
        </Box>

        <Box sx={{ px: 1.5, mt: 2 }}>
          {menuItems.map((item) => (
            <Box
              key={item.label}
              onClick={() => navigate(item.path)}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1.75,
                px: 2,
                py: 1.5,
                borderRadius: 3,
                mb: 0.5,
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                background: item.active ? '#d1fae5' : 'transparent',
                color: item.active ? '#059669' : '#6b7280',
                fontWeight: item.active ? 600 : 400,
                '&:hover': {
                  background: item.active ? '#d1fae5' : '#f9fafb',
                  color: '#10b981',
                },
              }}
            >
              <item.icon sx={{ fontSize: 22 }} />
              <Typography sx={{ fontSize: 15 }}>{item.label}</Typography>
            </Box>
          ))}
        </Box>

        <Box sx={{ position: 'absolute', bottom: 20, left: 0, right: 0, px: 1.5 }}>
          <Box
            onClick={handleLogout}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.75,
              px: 2,
              py: 1.5,
              borderRadius: 3,
              cursor: 'pointer',
              color: '#ef4444',
              '&:hover': { background: '#fef2f2' },
            }}
          >
            <LogoutIcon sx={{ fontSize: 22 }} />
            <Typography sx={{ fontSize: 15 }}>Logout</Typography>
          </Box>
        </Box>
      </Box>

      {/* Main Content */}
      <Box sx={{ ml: { xs: 0, md: '280px' }, flex: 1, p: { xs: 2, md: 4 } }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography sx={{ fontSize: 32, fontWeight: 700, color: '#111827', mb: 0.5 }}>
            Welcome back! 👋
          </Typography>
          <Typography sx={{ color: '#6b7280', fontSize: 16 }}>
            Here's your health overview for today.
          </Typography>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <StatCard
              title="Upcoming Appointments"
              value={stats.upcomingAppointments}
              icon={CalendarTodayIcon}
              gradient="linear-gradient(135deg, #10b981 0%, #059669 100%)"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <StatCard
              title="Active Prescriptions"
              value={stats.prescriptions}
              icon={MedicationIcon}
              gradient="linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <StatCard
              title="Medical Reports"
              value={stats.reports}
              icon={AssignmentIcon}
              gradient="linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)"
            />
          </Grid>
        </Grid>

        {/* Quick Actions */}
        <Paper sx={{ p: 3, mb: 4, borderRadius: 5, boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)' }}>
          <Typography sx={{ fontSize: 20, fontWeight: 700, color: '#111827', mb: 3 }}>
            Quick Actions
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<SearchIcon />}
                onClick={() => navigate('/patient/doctors')}
                sx={{
                  py: 1.5,
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  borderRadius: 3,
                  boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)',
                }}
              >
                Find Doctors
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => navigate('/patient/appointments')}
                sx={{ py: 1.5, borderRadius: 3, borderColor: '#10b981', color: '#10b981' }}
              >
                My Appointments
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => navigate('/patient/prescriptions')}
                sx={{ py: 1.5, borderRadius: 3, borderColor: '#10b981', color: '#10b981' }}
              >
                Prescriptions
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => navigate('/patient/reports')}
                sx={{ py: 1.5, borderRadius: 3, borderColor: '#10b981', color: '#10b981' }}
              >
                Medical History
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Recent Appointments */}
        <Paper sx={{ p: 3, borderRadius: 5, boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography sx={{ fontSize: 20, fontWeight: 700, color: '#111827' }}>
              Recent Appointments
            </Typography>
            <Button 
              onClick={() => navigate('/patient/appointments')}
              sx={{ color: '#10b981', fontWeight: 600 }}
            >
              View All
            </Button>
          </Box>

          {loading ? (
            <Typography sx={{ textAlign: 'center', py: 4, color: '#9ca3af' }}>Loading...</Typography>
          ) : recentAppointments.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 6 }}>
              <Box sx={{ fontSize: 60, mb: 2 }}>📅</Box>
              <Typography sx={{ color: '#6b7280', mb: 3 }}>
                No appointments found
              </Typography>
              <Button
                variant="contained"
                startIcon={<SearchIcon />}
                onClick={() => navigate('/patient/doctors')}
                sx={{
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  borderRadius: 3,
                  px: 4,
                }}
              >
                Book Your First Appointment
              </Button>
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600, color: '#374151' }}>Date</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: '#374151' }}>Time</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: '#374151' }}>Doctor</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: '#374151' }}>Specialization</TableCell>
                    <TableCell sx={{ fontWeight: 600, color: '#374151' }}>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentAppointments.map((appointment) => (
                    <TableRow key={appointment.id} sx={{ '&:hover': { background: '#f9fafb' } }}>
                      <TableCell>{formatDate(appointment.appointment_date)}</TableCell>
                      <TableCell>{appointment.appointment_time}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                          <Avatar sx={{ width: 32, height: 32, background: '#d1fae5', color: '#059669', fontSize: 12 }}>
                            {appointment.doctor_first_name?.[0] || 'D'}
                          </Avatar>
                          Dr. {appointment.doctor_first_name} {appointment.doctor_last_name}
                        </Box>
                      </TableCell>
                      <TableCell>{appointment.specialization || 'General'}</TableCell>
                      <TableCell>
                        <Chip 
                          label={appointment.status} 
                          size="small"
                          sx={{
                            borderRadius: 2,
                            fontWeight: 600,
                            background: 
                              appointment.status === 'completed' ? '#d1fae5' :
                              appointment.status === 'pending' ? '#fef3c7' :
                              appointment.status === 'confirmed' ? '#dbeafe' :
                              appointment.status === 'cancelled' ? '#fee2e2' : '#f3f4f6',
                            color:
                              appointment.status === 'completed' ? '#059669' :
                              appointment.status === 'pending' ? '#d97706' :
                              appointment.status === 'confirmed' ? '#2563eb' :
                              appointment.status === 'cancelled' ? '#dc2626' : '#6b7280',
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

export default PatientDashboard;
