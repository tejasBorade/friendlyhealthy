import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  AppBar,
  Toolbar,
} from '@mui/material';
import {
  LocalHospital,
  Psychology,
  CalendarToday,
  Description,
  MonetizationOn,
  People,
  ArrowForward,
  Login as LoginIcon,
} from '@mui/icons-material';
import IntegratedHealthFlow from '../components/IntegratedHealthFlow';
import DrugSearch from '../components/DrugSearch';

const Home = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: Psychology,
      title: 'AI Symptom Checker',
      description: 'Get instant AI-powered preliminary health assessments',
      color: '#10b981',
    },
    {
      icon: CalendarToday,
      title: 'Easy Appointments',
      description: 'Book appointments with top doctors in your area',
      color: '#3b82f6',
    },
    {
      icon: People,
      title: 'Expert Doctors',
      description: 'Access to qualified healthcare professionals',
      color: '#8b5cf6',
    },
    {
      icon: Description,
      title: 'Medical Records',
      description: 'Securely store and access your health records',
      color: '#f59e0b',
    },
    {
      icon: MonetizationOn,
      title: 'Transparent Billing',
      description: 'Clear pricing and insurance integration',
      color: '#10b981',
    },
    {
      icon: LocalHospital,
      title: '24/7 Support',
      description: 'Round-the-clock healthcare assistance',
      color: '#ef4444',
    },
  ];

  return (
    <Box sx={{ minHeight: '100vh', background: '#f9fafb' }}>
      {/* Header */}
      <AppBar
        position="sticky"
        sx={{
          background: 'white',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}
      >
        <Toolbar>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexGrow: 1 }}>
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
              HealthCare Platform
            </Typography>
          </Box>
          <Button
            variant="outlined"
            startIcon={<LoginIcon />}
            onClick={() => navigate('/login')}
            sx={{
              borderColor: '#10b981',
              color: '#10b981',
              '&:hover': {
                borderColor: '#059669',
                backgroundColor: '#f0fdf4',
              },
            }}
          >
            Login
          </Button>
          <Button
            variant="contained"
            onClick={() => navigate('/register')}
            sx={{
              ml: 2,
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
              },
            }}
          >
            Sign Up
          </Button>
        </Toolbar>
      </AppBar>

      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          color: 'white',
          py: 8,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography
                variant="h2"
                sx={{
                  fontWeight: 800,
                  mb: 2,
                  fontSize: { xs: '2.5rem', md: '3.5rem' },
                }}
              >
                Your Health, Our Priority
              </Typography>
              <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
                Experience the future of healthcare with AI-powered symptom checking, easy
                appointment booking, and comprehensive medical care.
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  size="large"
                  endIcon={<ArrowForward />}
                  onClick={() => {
                    document.getElementById('symptom-checker')?.scrollIntoView({ behavior: 'smooth' });
                  }}
                  sx={{
                    bgcolor: 'white',
                    color: '#10b981',
                    '&:hover': {
                      bgcolor: '#f9fafb',
                    },
                  }}
                >
                  Try Symptom Checker
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => navigate('/register')}
                  sx={{
                    borderColor: 'white',
                    color: 'white',
                    '&:hover': {
                      borderColor: 'white',
                      bgcolor: 'rgba(255,255,255,0.1)',
                    },
                  }}
                >
                  Get Started Free
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                }}
              >
                <LocalHospital sx={{ fontSize: 300, opacity: 0.2 }} />
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography
          variant="h3"
          align="center"
          sx={{ fontWeight: 700, mb: 2, color: '#111827' }}
        >
          Why Choose Us?
        </Typography>
        <Typography
          variant="h6"
          align="center"
          color="text.secondary"
          sx={{ mb: 6, maxWidth: 600, mx: 'auto' }}
        >
          Comprehensive healthcare solutions powered by cutting-edge technology
        </Typography>

        <Grid container spacing={3}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card
                sx={{
                  height: '100%',
                  transition: 'transform 0.3s, box-shadow 0.3s',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 12px 24px rgba(0,0,0,0.15)',
                  },
                }}
              >
                <CardContent>
                  <Box
                    sx={{
                      width: 60,
                      height: 60,
                      borderRadius: 3,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 2,
                      background: `linear-gradient(135deg, ${feature.color} 0%, ${feature.color}dd 100%)`,
                    }}
                  >
                    <feature.icon sx={{ fontSize: 32, color: 'white' }} />
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Integrated Health Flow Section */}
      <IntegratedHealthFlow />

      {/* Drug Search Section */}
      <DrugSearch />

      {/* CTA Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
          color: 'white',
          py: 8,
        }}
      >
        <Container maxWidth="md">
          <Typography
            variant="h3"
            align="center"
            sx={{ fontWeight: 700, mb: 2 }}
          >
            Ready to Get Started?
          </Typography>
          <Typography
            variant="h6"
            align="center"
            sx={{ mb: 4, opacity: 0.9 }}
          >
            Join thousands of patients who trust us with their healthcare needs
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/register')}
              sx={{
                bgcolor: 'white',
                color: '#10b981',
                px: 4,
                '&:hover': {
                  bgcolor: '#f9fafb',
                },
              }}
            >
              Create Free Account
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/login')}
              sx={{
                borderColor: 'white',
                color: 'white',
                px: 4,
                '&:hover': {
                  borderColor: 'white',
                  bgcolor: 'rgba(255,255,255,0.1)',
                },
              }}
            >
              Login
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Footer */}
      <Box sx={{ bgcolor: '#111827', color: 'white', py: 4 }}>
        <Container maxWidth="lg">
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                HealthCare Platform
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Providing quality healthcare services with modern technology and compassionate care.
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                Quick Links
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  onClick={() => navigate('/login')}
                  sx={{ color: 'white', justifyContent: 'flex-start', textTransform: 'none' }}
                >
                  Login
                </Button>
                <Button
                  onClick={() => navigate('/register')}
                  sx={{ color: 'white', justifyContent: 'flex-start', textTransform: 'none' }}
                >
                  Register
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                Contact
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                Email: support@healthcare.com
                <br />
                Phone: +1 (555) 123-4567
                <br />
                Available 24/7
              </Typography>
            </Grid>
          </Grid>
          <Box sx={{ borderTop: '1px solid rgba(255,255,255,0.1)', mt: 4, pt: 4, textAlign: 'center' }}>
            <Typography variant="body2" sx={{ opacity: 0.6 }}>
              © 2026 HealthCare Platform. All rights reserved. | Powered by ApiMedic, openFDA & OpenStreetMap
            </Typography>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};

export default Home;
