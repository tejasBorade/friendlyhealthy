import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Divider,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Snackbar,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SettingsIcon from '@mui/icons-material/Settings';
import PersonIcon from '@mui/icons-material/Person';
import NotificationsIcon from '@mui/icons-material/Notifications';
import SecurityIcon from '@mui/icons-material/Security';
import PaletteIcon from '@mui/icons-material/Palette';
import LogoutIcon from '@mui/icons-material/Logout';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import EventNoteIcon from '@mui/icons-material/EventNote';
import MedicationIcon from '@mui/icons-material/Medication';
import DescriptionIcon from '@mui/icons-material/Description';
import ReceiptIcon from '@mui/icons-material/Receipt';

const Settings = () => {
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  const [settings, setSettings] = useState({
    emailNotifications: true,
    smsNotifications: false,
    appointmentReminders: true,
    prescriptionAlerts: true,
    billingNotifications: true,
    twoFactorAuth: false,
    darkMode: false,
    language: 'en',
    timezone: 'UTC',
  });

  const handleToggle = (setting) => {
    setSettings(prev => ({ ...prev, [setting]: !prev[setting] }));
    setSnackbar({ open: true, message: 'Settings updated successfully', severity: 'success' });
  };

  const handleSelectChange = (setting, value) => {
    setSettings(prev => ({ ...prev, [setting]: value }));
    setSnackbar({ open: true, message: 'Settings updated successfully', severity: 'success' });
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const getRoleBasedPath = (path) => {
    const role = user?.role || 'patient';
    return `/${role}${path}`;
  };

  const menuItems = [
    { icon: DashboardIcon, label: 'Dashboard', path: getRoleBasedPath('/dashboard') },
    { icon: PersonIcon, label: 'Profile', path: '/profile' },
    { icon: SettingsIcon, label: 'Settings', path: '/settings', active: true },
  ];

  const SettingSection = ({ icon: Icon, title, children }) => (
    <Card
      sx={{
        mb: 3,
        borderRadius: 5,
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)',
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Box
            sx={{
              width: 45,
              height: 45,
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              borderRadius: 3,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Icon sx={{ color: 'white', fontSize: 24 }} />
          </Box>
          <Typography sx={{ fontSize: 20, fontWeight: 600, color: '#111827' }}>
            {title}
          </Typography>
        </Box>
        {children}
      </CardContent>
    </Card>
  );

  const SettingToggle = ({ label, description, checked, onChange }) => (
    <Box sx={{ py: 2, borderBottom: '1px solid #f3f4f6' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography sx={{ fontWeight: 500, color: '#111827' }}>{label}</Typography>
          <Typography sx={{ fontSize: 14, color: '#6b7280' }}>{description}</Typography>
        </Box>
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
      </Box>
    </Box>
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
        <Box sx={{ mb: 4 }}>
          <Typography sx={{ fontSize: 32, fontWeight: 700, color: '#111827', mb: 0.5 }}>
            Settings ⚙️
          </Typography>
          <Typography sx={{ color: '#6b7280', fontSize: 16 }}>
            Manage your account preferences and notifications.
          </Typography>
        </Box>

        <Box sx={{ maxWidth: 800 }}>
          {/* Notification Settings */}
          <SettingSection icon={NotificationsIcon} title="Notifications">
            <SettingToggle
              label="Email Notifications"
              description="Receive updates and alerts via email"
              checked={settings.emailNotifications}
              onChange={() => handleToggle('emailNotifications')}
            />
            <SettingToggle
              label="SMS Notifications"
              description="Get text message alerts for important updates"
              checked={settings.smsNotifications}
              onChange={() => handleToggle('smsNotifications')}
            />
            <SettingToggle
              label="Appointment Reminders"
              description="Receive reminders before your appointments"
              checked={settings.appointmentReminders}
              onChange={() => handleToggle('appointmentReminders')}
            />
            <SettingToggle
              label="Prescription Alerts"
              description="Get notified when prescriptions need refills"
              checked={settings.prescriptionAlerts}
              onChange={() => handleToggle('prescriptionAlerts')}
            />
            <SettingToggle
              label="Billing Notifications"
              description="Receive billing and payment updates"
              checked={settings.billingNotifications}
              onChange={() => handleToggle('billingNotifications')}
            />
          </SettingSection>

          {/* Security Settings */}
          <SettingSection icon={SecurityIcon} title="Security">
            <SettingToggle
              label="Two-Factor Authentication"
              description="Add an extra layer of security to your account"
              checked={settings.twoFactorAuth}
              onChange={() => handleToggle('twoFactorAuth')}
            />
            <Box sx={{ py: 2, borderBottom: '1px solid #f3f4f6' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography sx={{ fontWeight: 500, color: '#111827' }}>Change Password</Typography>
                  <Typography sx={{ fontSize: 14, color: '#6b7280' }}>
                    Update your password regularly for security
                  </Typography>
                </Box>
                <Button
                  variant="outlined"
                  sx={{
                    borderColor: '#10b981',
                    color: '#10b981',
                    borderRadius: 2,
                    '&:hover': {
                      borderColor: '#059669',
                      background: '#f0fdf4',
                    },
                  }}
                >
                  Change
                </Button>
              </Box>
            </Box>
          </SettingSection>

          {/* Appearance Settings */}
          <SettingSection icon={PaletteIcon} title="Appearance">
            <SettingToggle
              label="Dark Mode"
              description="Switch to dark theme for reduced eye strain"
              checked={settings.darkMode}
              onChange={() => handleToggle('darkMode')}
            />
            <Box sx={{ py: 2, borderBottom: '1px solid #f3f4f6' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography sx={{ fontWeight: 500, color: '#111827' }}>Language</Typography>
                  <Typography sx={{ fontSize: 14, color: '#6b7280' }}>
                    Choose your preferred language
                  </Typography>
                </Box>
                <FormControl size="small" sx={{ minWidth: 150 }}>
                  <Select
                    value={settings.language}
                    onChange={(e) => handleSelectChange('language', e.target.value)}
                    sx={{ borderRadius: 2 }}
                  >
                    <MenuItem value="en">English</MenuItem>
                    <MenuItem value="es">Spanish</MenuItem>
                    <MenuItem value="fr">French</MenuItem>
                    <MenuItem value="de">German</MenuItem>
                    <MenuItem value="hi">Hindi</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Box>
            <Box sx={{ py: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography sx={{ fontWeight: 500, color: '#111827' }}>Timezone</Typography>
                  <Typography sx={{ fontSize: 14, color: '#6b7280' }}>
                    Set your local timezone
                  </Typography>
                </Box>
                <FormControl size="small" sx={{ minWidth: 200 }}>
                  <Select
                    value={settings.timezone}
                    onChange={(e) => handleSelectChange('timezone', e.target.value)}
                    sx={{ borderRadius: 2 }}
                  >
                    <MenuItem value="UTC">UTC (GMT+0)</MenuItem>
                    <MenuItem value="EST">Eastern Time (GMT-5)</MenuItem>
                    <MenuItem value="CST">Central Time (GMT-6)</MenuItem>
                    <MenuItem value="PST">Pacific Time (GMT-8)</MenuItem>
                    <MenuItem value="IST">India Standard Time (GMT+5:30)</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Box>
          </SettingSection>

          {/* Danger Zone */}
          <Card
            sx={{
              borderRadius: 5,
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)',
              border: '1px solid #fecaca',
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <Box
                  sx={{
                    width: 45,
                    height: 45,
                    background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                    borderRadius: 3,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <SecurityIcon sx={{ color: 'white', fontSize: 24 }} />
                </Box>
                <Typography sx={{ fontSize: 20, fontWeight: 600, color: '#111827' }}>
                  Danger Zone
                </Typography>
              </Box>
              <Box sx={{ py: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box>
                    <Typography sx={{ fontWeight: 500, color: '#111827' }}>Delete Account</Typography>
                    <Typography sx={{ fontSize: 14, color: '#6b7280' }}>
                      Permanently delete your account and all data
                    </Typography>
                  </Box>
                  <Button
                    variant="outlined"
                    color="error"
                    sx={{
                      borderRadius: 2,
                    }}
                  >
                    Delete Account
                  </Button>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ borderRadius: 3 }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Settings;
