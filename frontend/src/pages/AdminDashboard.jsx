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
  IconButton,
  Avatar,
} from '@mui/material';
import {
  People,
  LocalHospital,
  CalendarToday,
  TrendingUp,
  Settings,
  Assessment,
  Logout,
  Dashboard,
  EventNote,
  AttachMoney,
  Description,
  MedicalServices,
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

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const StatCard = ({ title, value, icon: Icon, gradient, trend }) => (
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
        '&::before': {
          content: '""',
          position: 'absolute',
          top: -50,
          right: -50,
          width: 100,
          height: 100,
          borderRadius: '50%',
          background: gradient,
          opacity: 0.1,
        }
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
            {trend && (
              <Box 
                sx={{ 
                  mt: 1,
                  display: 'inline-block',
                  px: 1.5,
                  py: 0.5,
                  borderRadius: 2,
                  background: '#d1fae5',
                  color: '#059669',
                  fontSize: 13,
                  fontWeight: 600,
                }}
              >
                {trend}
              </Box>
            )}
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

  const menuItems = [
    { icon: Dashboard, label: 'Dashboard', path: '/admin/dashboard', active: true },
    { icon: People, label: 'Users', path: '/admin/users' },
    { icon: LocalHospital, label: 'Doctors', path: '/admin/doctors' },
    { icon: EventNote, label: 'Appointments', path: '/admin/appointments' },
    { icon: AttachMoney, label: 'Billing', path: '/billing' },
    { icon: Description, label: 'Reports', path: '/reports' },
    { icon: Settings, label: 'Settings', path: '/admin/settings' },
  ];

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
        {/* Logo */}
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

        {/* Menu */}
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

        {/* Logout */}
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
            <Logout sx={{ fontSize: 22 }} />
            <Typography sx={{ fontSize: 15 }}>Logout</Typography>
          </Box>
        </Box>
      </Box>

      {/* Main Content */}
      <Box sx={{ ml: { xs: 0, md: '280px' }, flex: 1, p: { xs: 2, md: 4 } }}>
        {/* Header */}
        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography sx={{ fontSize: 32, fontWeight: 700, color: '#111827', mb: 0.5 }}>
              Welcome back, Admin! 👋
            </Typography>
            <Typography sx={{ color: '#6b7280', fontSize: 16 }}>
              Here's what's happening with your platform today.
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<MedicalServices />}
            sx={{
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              borderRadius: 3,
              px: 3,
              py: 1.5,
              boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)',
              display: { xs: 'none', sm: 'flex' },
            }}
          >
            Add Doctor
          </Button>
        </Box>

        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard
              title="Total Users"
              value={stats.totalUsers}
              icon={People}
              gradient="linear-gradient(135deg, #10b981 0%, #059669 100%)"
              trend="+12%"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard
              title="Total Doctors"
              value={stats.totalDoctors}
              icon={LocalHospital}
              gradient="linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)"
              trend="+5%"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard
              title="Total Patients"
              value={stats.totalPatients}
              icon={People}
              gradient="linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)"
              trend="+18%"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard
              title="Appointments"
              value={stats.totalAppointments}
              icon={CalendarToday}
              gradient="linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
              trend="+23%"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard
              title="Completed"
              value={stats.completedAppointments}
              icon={Assessment}
              gradient="linear-gradient(135deg, #10b981 0%, #059669 100%)"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard
              title="Revenue"
              value={`$${stats.revenue}`}
              icon={TrendingUp}
              gradient="linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"
              trend="+15%"
            />
          </Grid>
        </Grid>

        {/* Recent Activity */}
        <Paper 
          sx={{ 
            p: 3, 
            mb: 3, 
            borderRadius: 5,
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
          }}
        >
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography sx={{ fontSize: 20, fontWeight: 700, color: '#111827' }}>
              Recent Activity
            </Typography>
            <Button
              variant="outlined"
              onClick={() => navigate('/appointments')}
              sx={{
                borderColor: '#10b981',
                color: '#10b981',
                borderRadius: 3,
                '&:hover': {
                  borderColor: '#059669',
                  background: '#f0fdf4',
                },
              }}
            >
              View All
            </Button>
          </Box>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 600, color: '#374151' }}>Patient</TableCell>
                <TableCell sx={{ fontWeight: 600, color: '#374151' }}>Doctor</TableCell>
                <TableCell sx={{ fontWeight: 600, color: '#374151' }}>Date</TableCell>
                <TableCell sx={{ fontWeight: 600, color: '#374151' }}>Time</TableCell>
                <TableCell sx={{ fontWeight: 600, color: '#374151' }}>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {recentActivity.length > 0 ? (
                recentActivity.map((appointment) => (
                  <TableRow 
                    key={appointment.id}
                    sx={{ '&:hover': { background: '#f9fafb' } }}
                  >
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Avatar sx={{ width: 36, height: 36, background: '#d1fae5', color: '#059669', fontSize: 14 }}>
                          {appointment.patient_first_name?.[0] || 'P'}
                        </Avatar>
                        {appointment.patient_first_name} {appointment.patient_last_name}
                      </Box>
                    </TableCell>
                    <TableCell>
                      Dr. {appointment.doctor_first_name} {appointment.doctor_last_name}
                    </TableCell>
                    <TableCell>{appointment.appointment_date}</TableCell>
                    <TableCell>{appointment.appointment_time}</TableCell>
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
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 4, color: '#9ca3af' }}>
                    No recent activity
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </Paper>

        {/* Quick Actions */}
        <Paper 
          sx={{ 
            p: 3, 
            borderRadius: 5,
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
          }}
        >
          <Typography sx={{ fontSize: 20, fontWeight: 700, color: '#111827', mb: 3 }}>
            Quick Actions
          </Typography>
          <Grid container spacing={2}>
            {[
              { icon: People, label: 'Manage Users', color: '#10b981' },
              { icon: LocalHospital, label: 'Manage Doctors', color: '#3b82f6' },
              { icon: Assessment, label: 'View Reports', color: '#8b5cf6' },
              { icon: Settings, label: 'Settings', color: '#f59e0b' },
            ].map((action) => (
              <Grid item xs={12} sm={6} md={3} key={action.label}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<action.icon />}
                  sx={{
                    py: 2,
                    borderRadius: 3,
                    borderColor: action.color,
                    color: action.color,
                    fontWeight: 600,
                    '&:hover': {
                      background: `${action.color}10`,
                      borderColor: action.color,
                    },
                  }}
                >
                  {action.label}
                </Button>
              </Grid>
            ))}
          </Grid>
        </Paper>
      </Box>
    </Box>
  );
}
