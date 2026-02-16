import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  FormControl,
  FormControlLabel,
  MenuItem,
  Select,
  Snackbar,
  Switch,
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
  Security,
  Settings,
} from '@mui/icons-material';

const defaultSettings = {
  maintenanceMode: false,
  publicRegistration: true,
  emailVerification: true,
  auditLogging: true,
  notifyOnNewUser: true,
  notifyOnFailedLogin: true,
  sessionTimeout: '30',
  timezone: 'UTC',
};

const AdminSettings = () => {
  const navigate = useNavigate();
  const [settings, setSettings] = useState(defaultSettings);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const menuItems = [
    { icon: Dashboard, label: 'Dashboard', path: '/admin/dashboard' },
    { icon: People, label: 'Users', path: '/admin/users' },
    { icon: LocalHospital, label: 'Doctors', path: '/admin/doctors' },
    { icon: EventNote, label: 'Appointments', path: '/admin/appointments' },
    { icon: AttachMoney, label: 'Billing', path: '/billing' },
    { icon: Description, label: 'Reports', path: '/reports' },
    { icon: Settings, label: 'Settings', path: '/admin/settings', active: true },
  ];

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const handleToggle = (key) => {
    setSettings((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSelect = (key, value) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    setSnackbar({ open: true, message: 'Admin settings saved', severity: 'success' });
  };

  const handleReset = () => {
    setSettings(defaultSettings);
    setSnackbar({ open: true, message: 'Settings reset to defaults', severity: 'info' });
  };

  const SwitchRow = ({ title, description, checked, onChange }) => (
    <Box sx={{ py: 2, display: 'flex', justifyContent: 'space-between', gap: 2 }}>
      <Box>
        <Typography sx={{ fontWeight: 600, color: '#111827' }}>{title}</Typography>
        <Typography sx={{ fontSize: 14, color: '#6b7280' }}>{description}</Typography>
      </Box>
      <FormControlLabel
        control={
          <Switch
            checked={checked}
            onChange={onChange}
            sx={{
              '& .MuiSwitch-switchBase.Mui-checked': {
                color: '#10b981',
              },
              '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                backgroundColor: '#10b981',
              },
            }}
          />
        }
        label=""
      />
    </Box>
  );

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
            Admin Settings
          </Typography>
          <Typography sx={{ color: '#6b7280', fontSize: 16 }}>
            Configure platform behavior, security defaults, and notifications.
          </Typography>
        </Box>

        <Card sx={{ mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
              <Settings sx={{ color: '#059669' }} />
              <Typography sx={{ fontSize: 20, fontWeight: 700, color: '#111827' }}>
                Platform Controls
              </Typography>
            </Box>
            <Divider />
            <SwitchRow
              title="Maintenance Mode"
              description="Temporarily disable non-admin access while updates are in progress."
              checked={settings.maintenanceMode}
              onChange={() => handleToggle('maintenanceMode')}
            />
            <Divider />
            <SwitchRow
              title="Public Registration"
              description="Allow new users to register accounts from the public app."
              checked={settings.publicRegistration}
              onChange={() => handleToggle('publicRegistration')}
            />
            <Divider />
            <Box sx={{ py: 2 }}>
              <Typography sx={{ fontWeight: 600, color: '#111827', mb: 0.5 }}>Default Timezone</Typography>
              <Typography sx={{ fontSize: 14, color: '#6b7280', mb: 1.5 }}>
                Applied to new users and system reports.
              </Typography>
              <FormControl size="small" sx={{ minWidth: 220 }}>
                <Select
                  value={settings.timezone}
                  onChange={(event) => handleSelect('timezone', event.target.value)}
                >
                  <MenuItem value="UTC">UTC</MenuItem>
                  <MenuItem value="EST">US Eastern (EST)</MenuItem>
                  <MenuItem value="CST">US Central (CST)</MenuItem>
                  <MenuItem value="PST">US Pacific (PST)</MenuItem>
                  <MenuItem value="IST">India Standard (IST)</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ mb: 3, borderRadius: 4, boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
              <Security sx={{ color: '#2563eb' }} />
              <Typography sx={{ fontSize: 20, fontWeight: 700, color: '#111827' }}>
                Security Defaults
              </Typography>
            </Box>
            <Divider />
            <SwitchRow
              title="Email Verification Required"
              description="Require verification before first login."
              checked={settings.emailVerification}
              onChange={() => handleToggle('emailVerification')}
            />
            <Divider />
            <SwitchRow
              title="Audit Logging"
              description="Record user and admin actions for compliance."
              checked={settings.auditLogging}
              onChange={() => handleToggle('auditLogging')}
            />
            <Divider />
            <Box sx={{ py: 2 }}>
              <Typography sx={{ fontWeight: 600, color: '#111827', mb: 0.5 }}>Session Timeout</Typography>
              <Typography sx={{ fontSize: 14, color: '#6b7280', mb: 1.5 }}>
                Automatically sign users out after inactivity.
              </Typography>
              <FormControl size="small" sx={{ minWidth: 220 }}>
                <Select
                  value={settings.sessionTimeout}
                  onChange={(event) => handleSelect('sessionTimeout', event.target.value)}
                >
                  <MenuItem value="15">15 minutes</MenuItem>
                  <MenuItem value="30">30 minutes</MenuItem>
                  <MenuItem value="60">60 minutes</MenuItem>
                  <MenuItem value="120">120 minutes</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ borderRadius: 4, boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)' }}>
          <CardContent>
            <Typography sx={{ fontSize: 20, fontWeight: 700, color: '#111827', mb: 1.5 }}>
              Admin Notifications
            </Typography>
            <Divider />
            <SwitchRow
              title="Notify on New User"
              description="Send admin alerts when a new account is created."
              checked={settings.notifyOnNewUser}
              onChange={() => handleToggle('notifyOnNewUser')}
            />
            <Divider />
            <SwitchRow
              title="Notify on Failed Login"
              description="Alert admins when repeated failed login attempts are detected."
              checked={settings.notifyOnFailedLogin}
              onChange={() => handleToggle('notifyOnFailedLogin')}
            />
          </CardContent>
        </Card>

        <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            onClick={handleSave}
            sx={{
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              borderRadius: 2.5,
              px: 3,
              '&:hover': {
                background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
              },
            }}
          >
            Save Changes
          </Button>
          <Button
            variant="outlined"
            onClick={handleReset}
            sx={{
              borderRadius: 2.5,
              borderColor: '#9ca3af',
              color: '#374151',
              '&:hover': {
                borderColor: '#6b7280',
                background: '#f3f4f6',
              },
            }}
          >
            Reset Defaults
          </Button>
        </Box>

        <Alert severity="info" sx={{ mt: 3 }}>
          These settings are currently local to the frontend session and can be connected to backend APIs later.
        </Alert>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
          severity={snackbar.severity}
          sx={{ borderRadius: 2 }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default AdminSettings;
