import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Avatar,
  Grid,
  Divider,
  Alert,
  Snackbar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SettingsIcon from '@mui/icons-material/Settings';
import PersonIcon from '@mui/icons-material/Person';
import EditIcon from '@mui/icons-material/Edit';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import EmailIcon from '@mui/icons-material/Email';
import PhoneIcon from '@mui/icons-material/Phone';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import BadgeIcon from '@mui/icons-material/Badge';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import LogoutIcon from '@mui/icons-material/Logout';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';

const Profile = () => {
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  const [isEditing, setIsEditing] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [passwordDialog, setPasswordDialog] = useState(false);
  
  const [profile, setProfile] = useState({
    firstName: user?.first_name || user?.name?.split(' ')[0] || 'John',
    lastName: user?.last_name || user?.name?.split(' ')[1] || 'Doe',
    email: user?.email || 'user@healthcare.com',
    phone: user?.phone || '+1 234 567 8900',
    address: user?.address || '123 Healthcare Avenue, Medical City, MC 12345',
    dateOfBirth: user?.date_of_birth || '1990-01-15',
    bloodType: user?.blood_type || 'O+',
    emergencyContact: user?.emergency_contact || '+1 234 567 8901',
  });

  const [passwords, setPasswords] = useState({
    current: '',
    new: '',
    confirm: '',
  });

  const handleChange = (field, value) => {
    setProfile(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    setIsEditing(false);
    setSnackbar({ open: true, message: 'Profile updated successfully!', severity: 'success' });
  };

  const handleCancel = () => {
    setIsEditing(false);
    // Reset to original values
    setProfile({
      firstName: user?.first_name || user?.name?.split(' ')[0] || 'John',
      lastName: user?.last_name || user?.name?.split(' ')[1] || 'Doe',
      email: user?.email || 'user@healthcare.com',
      phone: user?.phone || '+1 234 567 8900',
      address: user?.address || '123 Healthcare Avenue, Medical City, MC 12345',
      dateOfBirth: user?.date_of_birth || '1990-01-15',
      bloodType: user?.blood_type || 'O+',
      emergencyContact: user?.emergency_contact || '+1 234 567 8901',
    });
  };

  const handlePasswordChange = () => {
    if (passwords.new !== passwords.confirm) {
      setSnackbar({ open: true, message: 'Passwords do not match!', severity: 'error' });
      return;
    }
    if (passwords.new.length < 6) {
      setSnackbar({ open: true, message: 'Password must be at least 6 characters!', severity: 'error' });
      return;
    }
    setPasswordDialog(false);
    setPasswords({ current: '', new: '', confirm: '' });
    setSnackbar({ open: true, message: 'Password changed successfully!', severity: 'success' });
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
    { icon: PersonIcon, label: 'Profile', path: '/profile', active: true },
    { icon: SettingsIcon, label: 'Settings', path: '/settings' },
  ];

  const InfoField = ({ icon: Icon, label, value, field, editable = true }) => (
    <Box sx={{ py: 2, borderBottom: '1px solid #f3f4f6' }}>
      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
        <Box
          sx={{
            width: 40,
            height: 40,
            background: '#f0fdf4',
            borderRadius: 2.5,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Icon sx={{ color: '#10b981', fontSize: 20 }} />
        </Box>
        <Box sx={{ flex: 1 }}>
          <Typography sx={{ fontSize: 13, color: '#6b7280', mb: 0.5 }}>{label}</Typography>
          {isEditing && editable ? (
            <TextField
              fullWidth
              size="small"
              value={value}
              onChange={(e) => handleChange(field, e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                  '&.Mui-focused fieldset': {
                    borderColor: '#10b981',
                  },
                },
              }}
            />
          ) : (
            <Typography sx={{ fontWeight: 500, color: '#111827' }}>{value}</Typography>
          )}
        </Box>
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
        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography sx={{ fontSize: 32, fontWeight: 700, color: '#111827', mb: 0.5 }}>
              My Profile 👤
            </Typography>
            <Typography sx={{ color: '#6b7280', fontSize: 16 }}>
              Manage your personal information and preferences.
            </Typography>
          </Box>
          {!isEditing ? (
            <Button
              variant="contained"
              startIcon={<EditIcon />}
              onClick={() => setIsEditing(true)}
              sx={{
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                borderRadius: 3,
                px: 3,
                py: 1.2,
                textTransform: 'none',
                fontWeight: 600,
                boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                },
              }}
            >
              Edit Profile
            </Button>
          ) : (
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="outlined"
                startIcon={<CancelIcon />}
                onClick={handleCancel}
                sx={{
                  borderColor: '#d1d5db',
                  color: '#6b7280',
                  borderRadius: 3,
                  px: 3,
                  py: 1.2,
                  textTransform: 'none',
                  fontWeight: 600,
                  '&:hover': {
                    borderColor: '#9ca3af',
                    background: '#f9fafb',
                  },
                }}
              >
                Cancel
              </Button>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                sx={{
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  borderRadius: 3,
                  px: 3,
                  py: 1.2,
                  textTransform: 'none',
                  fontWeight: 600,
                  boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                  },
                }}
              >
                Save Changes
              </Button>
            </Box>
          )}
        </Box>

        <Grid container spacing={3}>
          {/* Profile Card */}
          <Grid item xs={12} md={4}>
            <Card
              sx={{
                borderRadius: 5,
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)',
                overflow: 'visible',
              }}
            >
              <Box
                sx={{
                  height: 120,
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  borderRadius: '20px 20px 0 0',
                }}
              />
              <CardContent sx={{ textAlign: 'center', pt: 0, mt: -8 }}>
                <Box sx={{ position: 'relative', display: 'inline-block' }}>
                  <Avatar
                    sx={{
                      width: 120,
                      height: 120,
                      border: '4px solid white',
                      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
                      fontSize: 48,
                      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    }}
                  >
                    {profile.firstName[0]}{profile.lastName[0]}
                  </Avatar>
                  {isEditing && (
                    <IconButton
                      sx={{
                        position: 'absolute',
                        bottom: 0,
                        right: 0,
                        background: '#10b981',
                        color: 'white',
                        '&:hover': { background: '#059669' },
                      }}
                    >
                      <CameraAltIcon />
                    </IconButton>
                  )}
                </Box>
                <Typography sx={{ mt: 2, fontSize: 24, fontWeight: 700, color: '#111827' }}>
                  {profile.firstName} {profile.lastName}
                </Typography>
                <Typography sx={{ color: '#6b7280', textTransform: 'capitalize' }}>
                  {user?.role || 'Patient'}
                </Typography>
                <Box
                  sx={{
                    mt: 3,
                    p: 2,
                    background: '#f0fdf4',
                    borderRadius: 3,
                  }}
                >
                  <Typography sx={{ fontSize: 32, fontWeight: 700, color: '#10b981' }}>
                    {profile.bloodType}
                  </Typography>
                  <Typography sx={{ fontSize: 14, color: '#6b7280' }}>Blood Type</Typography>
                </Box>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card
              sx={{
                mt: 3,
                borderRadius: 5,
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)',
              }}
            >
              <CardContent>
                <Typography sx={{ fontWeight: 600, color: '#111827', mb: 2 }}>
                  Quick Actions
                </Typography>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => setPasswordDialog(true)}
                  sx={{
                    mb: 1.5,
                    borderColor: '#e5e7eb',
                    color: '#374151',
                    borderRadius: 2.5,
                    py: 1.2,
                    textTransform: 'none',
                    justifyContent: 'flex-start',
                    '&:hover': {
                      borderColor: '#10b981',
                      background: '#f0fdf4',
                    },
                  }}
                >
                  🔐 Change Password
                </Button>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => navigate('/settings')}
                  sx={{
                    mb: 1.5,
                    borderColor: '#e5e7eb',
                    color: '#374151',
                    borderRadius: 2.5,
                    py: 1.2,
                    textTransform: 'none',
                    justifyContent: 'flex-start',
                    '&:hover': {
                      borderColor: '#10b981',
                      background: '#f0fdf4',
                    },
                  }}
                >
                  ⚙️ Account Settings
                </Button>
                <Button
                  fullWidth
                  variant="outlined"
                  sx={{
                    borderColor: '#e5e7eb',
                    color: '#374151',
                    borderRadius: 2.5,
                    py: 1.2,
                    textTransform: 'none',
                    justifyContent: 'flex-start',
                    '&:hover': {
                      borderColor: '#10b981',
                      background: '#f0fdf4',
                    },
                  }}
                >
                  📄 Download Medical Records
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Details Card */}
          <Grid item xs={12} md={8}>
            <Card
              sx={{
                borderRadius: 5,
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Typography sx={{ fontSize: 20, fontWeight: 600, color: '#111827', mb: 2 }}>
                  Personal Information
                </Typography>

                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <InfoField
                      icon={BadgeIcon}
                      label="First Name"
                      value={profile.firstName}
                      field="firstName"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <InfoField
                      icon={BadgeIcon}
                      label="Last Name"
                      value={profile.lastName}
                      field="lastName"
                    />
                  </Grid>
                </Grid>

                <InfoField
                  icon={EmailIcon}
                  label="Email Address"
                  value={profile.email}
                  field="email"
                  editable={false}
                />

                <InfoField
                  icon={PhoneIcon}
                  label="Phone Number"
                  value={profile.phone}
                  field="phone"
                />

                <InfoField
                  icon={LocationOnIcon}
                  label="Address"
                  value={profile.address}
                  field="address"
                />

                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <InfoField
                      icon={CalendarMonthIcon}
                      label="Date of Birth"
                      value={profile.dateOfBirth}
                      field="dateOfBirth"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <InfoField
                      icon={PhoneIcon}
                      label="Emergency Contact"
                      value={profile.emergencyContact}
                      field="emergencyContact"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            {/* Activity Card */}
            <Card
              sx={{
                mt: 3,
                borderRadius: 5,
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Typography sx={{ fontSize: 20, fontWeight: 600, color: '#111827', mb: 3 }}>
                  Account Activity
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ textAlign: 'center', p: 2, background: '#f0fdf4', borderRadius: 3 }}>
                      <Typography sx={{ fontSize: 28, fontWeight: 700, color: '#10b981' }}>
                        12
                      </Typography>
                      <Typography sx={{ fontSize: 13, color: '#6b7280' }}>
                        Total Appointments
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ textAlign: 'center', p: 2, background: '#eff6ff', borderRadius: 3 }}>
                      <Typography sx={{ fontSize: 28, fontWeight: 700, color: '#3b82f6' }}>
                        8
                      </Typography>
                      <Typography sx={{ fontSize: 13, color: '#6b7280' }}>
                        Prescriptions
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ textAlign: 'center', p: 2, background: '#fef3c7', borderRadius: 3 }}>
                      <Typography sx={{ fontSize: 28, fontWeight: 700, color: '#f59e0b' }}>
                        5
                      </Typography>
                      <Typography sx={{ fontSize: 13, color: '#6b7280' }}>
                        Lab Reports
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Box sx={{ textAlign: 'center', p: 2, background: '#fce7f3', borderRadius: 3 }}>
                      <Typography sx={{ fontSize: 28, fontWeight: 700, color: '#ec4899' }}>
                        3
                      </Typography>
                      <Typography sx={{ fontSize: 13, color: '#6b7280' }}>
                        Doctors Visited
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Password Change Dialog */}
      <Dialog
        open={passwordDialog}
        onClose={() => setPasswordDialog(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{ sx: { borderRadius: 4 } }}
      >
        <DialogTitle sx={{ fontWeight: 600 }}>Change Password</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            type="password"
            label="Current Password"
            value={passwords.current}
            onChange={(e) => setPasswords({ ...passwords, current: e.target.value })}
            sx={{ mt: 2, mb: 2 }}
          />
          <TextField
            fullWidth
            type="password"
            label="New Password"
            value={passwords.new}
            onChange={(e) => setPasswords({ ...passwords, new: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            type="password"
            label="Confirm New Password"
            value={passwords.confirm}
            onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })}
          />
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setPasswordDialog(false)} sx={{ color: '#6b7280' }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handlePasswordChange}
            sx={{
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              borderRadius: 2,
            }}
          >
            Update Password
          </Button>
        </DialogActions>
      </Dialog>

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

export default Profile;
