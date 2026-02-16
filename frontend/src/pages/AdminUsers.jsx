import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Alert,
  Avatar,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  InputAdornment,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import {
  AttachMoney,
  Dashboard,
  Description,
  EventNote,
  LocalHospital,
  Logout,
  People,
  Search,
  Settings,
} from '@mui/icons-material';
import api from '../services/api';

const AdminUsers = () => {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const menuItems = [
    { icon: Dashboard, label: 'Dashboard', path: '/admin/dashboard' },
    { icon: People, label: 'Users', path: '/admin/users', active: true },
    { icon: LocalHospital, label: 'Doctors', path: '/admin/doctors' },
    { icon: EventNote, label: 'Appointments', path: '/admin/appointments' },
    { icon: AttachMoney, label: 'Billing', path: '/billing' },
    { icon: Description, label: 'Reports', path: '/reports' },
    { icon: Settings, label: 'Settings', path: '/admin/settings' },
  ];

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setLoading(true);
        setError('');

        const [doctorsRes, appointmentsRes] = await Promise.all([
          api.get('/doctors'),
          api.get('/appointments'),
        ]);

        const doctors = doctorsRes.data?.doctors || [];
        const appointments = appointmentsRes.data?.appointments || [];

        const doctorUsers = doctors.map((doctor) => ({
          id: `doctor-${doctor.id}`,
          name: `Dr. ${doctor.first_name || ''} ${doctor.last_name || ''}`.trim(),
          role: 'doctor',
          email: doctor.email || 'Not available',
          contact: doctor.phone || 'Not available',
          status: doctor.is_available === 0 ? 'inactive' : 'active',
          source: 'Doctor Directory',
        }));

        const patientMap = new Map();
        appointments.forEach((appointment) => {
          if (!appointment.patient_id || patientMap.has(appointment.patient_id)) {
            return;
          }

          patientMap.set(appointment.patient_id, {
            id: `patient-${appointment.patient_id}`,
            name: `${appointment.patient_first_name || ''} ${appointment.patient_last_name || ''}`.trim() || `Patient ${appointment.patient_id}`,
            role: 'patient',
            email: appointment.patient_email || 'Not available',
            contact: appointment.patient_phone || 'Not available',
            status: 'active',
            source: 'Appointments',
          });
        });

        const patientUsers = Array.from(patientMap.values());
        const combinedUsers = [...doctorUsers, ...patientUsers].sort((a, b) =>
          a.name.localeCompare(b.name)
        );

        setUsers(combinedUsers);
      } catch (err) {
        setError('Unable to load users right now.');
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const filteredUsers = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) {
      return users;
    }

    return users.filter((user) =>
      `${user.name} ${user.email} ${user.role}`.toLowerCase().includes(query)
    );
  }, [search, users]);

  const summary = useMemo(() => {
    const doctors = users.filter((user) => user.role === 'doctor').length;
    const patients = users.filter((user) => user.role === 'patient').length;
    return {
      total: users.length,
      doctors,
      patients,
    };
  }, [users]);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', background: '#f9fafb' }}>
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
              color: 'white',
              fontWeight: 700,
            }}
          >
            H
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
            <Logout sx={{ fontSize: 22 }} />
            <Typography sx={{ fontSize: 15 }}>Logout</Typography>
          </Box>
        </Box>
      </Box>

      <Box sx={{ ml: { xs: 0, md: '280px' }, flex: 1, p: { xs: 2, md: 4 } }}>
        <Box sx={{ mb: 4 }}>
          <Typography sx={{ fontSize: 32, fontWeight: 700, color: '#111827', mb: 0.5 }}>
            User Management
          </Typography>
          <Typography sx={{ color: '#6b7280', fontSize: 16 }}>
            Review all users currently visible to the admin panel.
          </Typography>
        </Box>

        {error ? (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        ) : null}

        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)' }}>
              <CardContent>
                <Typography sx={{ fontSize: 14, color: '#6b7280' }}>Total Users</Typography>
                <Typography sx={{ fontSize: 30, fontWeight: 700, color: '#111827' }}>
                  {summary.total}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)' }}>
              <CardContent>
                <Typography sx={{ fontSize: 14, color: '#6b7280' }}>Doctors</Typography>
                <Typography sx={{ fontSize: 30, fontWeight: 700, color: '#2563eb' }}>
                  {summary.doctors}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)' }}>
              <CardContent>
                <Typography sx={{ fontSize: 14, color: '#6b7280' }}>Patients</Typography>
                <Typography sx={{ fontSize: 30, fontWeight: 700, color: '#059669' }}>
                  {summary.patients}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Card sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)' }}>
          <CardContent>
            <TextField
              fullWidth
              placeholder="Search users by name, email, or role"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              sx={{ mb: 3 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />

            {loading ? (
              <Box sx={{ py: 6, display: 'flex', justifyContent: 'center' }}>
                <CircularProgress />
              </Box>
            ) : (
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700 }}>User</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Role</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Contact</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Source</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredUsers.length > 0 ? (
                    filteredUsers.map((user) => (
                      <TableRow key={user.id} sx={{ '&:hover': { background: '#f9fafb' } }}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <Avatar sx={{ width: 34, height: 34, background: '#d1fae5', color: '#059669' }}>
                              {user.name?.charAt(0)?.toUpperCase() || 'U'}
                            </Avatar>
                            <Box>
                              <Typography sx={{ fontWeight: 600, color: '#111827' }}>
                                {user.name}
                              </Typography>
                              <Typography sx={{ fontSize: 12, color: '#6b7280' }}>
                                {user.email}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            label={user.role}
                            sx={{
                              textTransform: 'capitalize',
                              background: user.role === 'doctor' ? '#dbeafe' : '#dcfce7',
                              color: user.role === 'doctor' ? '#1d4ed8' : '#166534',
                              fontWeight: 600,
                            }}
                          />
                        </TableCell>
                        <TableCell>{user.contact}</TableCell>
                        <TableCell>{user.source}</TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            label={user.status}
                            sx={{
                              textTransform: 'capitalize',
                              background: user.status === 'active' ? '#d1fae5' : '#fee2e2',
                              color: user.status === 'active' ? '#059669' : '#b91c1c',
                              fontWeight: 600,
                            }}
                          />
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={5} align="center" sx={{ py: 5, color: '#9ca3af' }}>
                        No users found for this search.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default AdminUsers;
