import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography } from '@mui/material';
import {
  Dashboard,
  EventNote,
  People,
  Assessment,
  Description,
  Person,
  Logout,
} from '@mui/icons-material';

const DoctorSidebar = ({ activeItem }) => {
  const navigate = useNavigate();

  const menuItems = [
    { icon: Dashboard, label: 'Dashboard', path: '/doctor/dashboard' },
    { icon: EventNote, label: 'Appointments', path: '/doctor/appointments' },
    { icon: People, label: 'My Patients', path: '/doctor/patients' },
    { icon: Assessment, label: 'Reports', path: '/reports' },
    { icon: Description, label: 'Prescriptions', path: '/prescriptions' },
    { icon: Person, label: 'Profile', path: '/profile' },
  ];

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  return (
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
        <Box>
          <Typography
            sx={{
              fontSize: 22,
              fontWeight: 700,
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              lineHeight: 1,
            }}
          >
            HealthCare
          </Typography>
          <Typography sx={{ fontSize: 12, color: '#6b7280' }}>Doctor Portal</Typography>
        </Box>
      </Box>

      <Box sx={{ px: 1.5, mt: 2 }}>
        {menuItems.map((item) => {
          const isActive = activeItem === item.label;
          return (
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
                background: isActive ? '#d1fae5' : 'transparent',
                color: isActive ? '#059669' : '#6b7280',
                fontWeight: isActive ? 600 : 400,
                '&:hover': {
                  background: isActive ? '#d1fae5' : '#f9fafb',
                  color: '#10b981',
                },
              }}
            >
              <item.icon sx={{ fontSize: 22 }} />
              <Typography sx={{ fontSize: 15 }}>{item.label}</Typography>
            </Box>
          );
        })}
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
  );
};

export default DoctorSidebar;
