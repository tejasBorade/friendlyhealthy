import React, { useState, useEffect } from 'react';
import {
  Box, Container, Typography, Paper, Card, CardContent, 
  Grid, Avatar, CircularProgress, Alert,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Tabs, Tab
} from '@mui/material';
import {
  Assessment as ReportsIcon,
  TrendingUp as TrendingIcon,
  People as PeopleIcon,
  EventNote as AppointmentsIcon,
  Receipt as BillingIcon,
  LocalHospital as DoctorIcon,
  CalendarMonth as CalendarIcon,
  CheckCircle as CompletedIcon
} from '@mui/icons-material';
import api from '../services/api';
import { useSelector } from 'react-redux';
import AdminSidebar from '../components/AdminSidebar';

const Reports = () => {
  const { user } = useSelector((state) => state.auth);
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [appointments, setAppointments] = useState([]);
  const [bills, setBills] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [appointmentsRes, billsRes] = await Promise.all([
        api.get('/appointments'),
        api.get('/billing')
      ]);
      setAppointments(appointmentsRes.data.appointments || []);
      setBills(billsRes.data.bills || []);
    } catch (err) {
      setError('Failed to load reports data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-IN', {
      year: 'numeric', month: 'short', day: 'numeric'
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  // Calculate statistics
  const stats = {
    totalAppointments: appointments.length,
    completedAppointments: appointments.filter(a => a.status === 'completed').length,
    pendingAppointments: appointments.filter(a => a.status === 'pending').length,
    confirmedAppointments: appointments.filter(a => a.status === 'confirmed').length,
    totalRevenue: bills.reduce((sum, b) => sum + (b.total || 0), 0),
    collectedRevenue: bills.filter(b => b.status === 'paid').reduce((sum, b) => sum + (b.total || 0), 0),
    pendingRevenue: bills.filter(b => b.status === 'pending').reduce((sum, b) => sum + (b.total || 0), 0)
  };

  if (loading) {
    const loadingContent = (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress sx={{ color: '#10b981' }} />
      </Box>
    );

    if (user?.role === 'admin') {
      return (
        <Box sx={{ display: 'flex', minHeight: '100vh', background: '#f9fafb' }}>
          <AdminSidebar activeItem="Reports" />
          <Box sx={{ ml: { xs: 0, md: '280px' }, flex: 1 }}>
            {loadingContent}
          </Box>
        </Box>
      );
    }

    return loadingContent;
  }

  const pageContent = (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 50%, #a7f3d0 100%)', py: 4 }}>
      <Container maxWidth="lg">
        {/* Header */}
        <Paper sx={{ p: 3, mb: 4, borderRadius: '20px', background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
              <ReportsIcon sx={{ fontSize: 30, color: 'white' }} />
            </Avatar>
            <Box>
              <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
                Reports & Analytics
              </Typography>
              <Typography sx={{ color: 'rgba(255,255,255,0.8)' }}>
                Overview of your healthcare activities
              </Typography>
            </Box>
          </Box>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>{error}</Alert>
        )}

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ 
              borderRadius: '20px', 
              boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: 'white'
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.8 }}>Total Appointments</Typography>
                    <Typography variant="h4" fontWeight={700}>
                      {stats.totalAppointments}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
                    <AppointmentsIcon />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ 
              borderRadius: '20px', 
              boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
              background: 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)',
              color: 'white'
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.8 }}>Completed</Typography>
                    <Typography variant="h4" fontWeight={700}>
                      {stats.completedAppointments}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
                    <CompletedIcon />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ 
              borderRadius: '20px', 
              boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
              background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
              color: 'white'
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.8 }}>Total Revenue</Typography>
                    <Typography variant="h5" fontWeight={700}>
                      {formatCurrency(stats.totalRevenue)}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
                    <TrendingIcon />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ 
              borderRadius: '20px', 
              boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
              background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
              color: 'white'
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.8 }}>Pending Amount</Typography>
                    <Typography variant="h5" fontWeight={700}>
                      {formatCurrency(stats.pendingRevenue)}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
                    <BillingIcon />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Tabs */}
        <Paper sx={{ borderRadius: '20px', overflow: 'hidden' }}>
          <Box sx={{ borderBottom: '1px solid #e5e7eb' }}>
            <Tabs 
              value={tabValue} 
              onChange={(e, v) => setTabValue(v)}
              sx={{
                px: 2,
                '& .MuiTab-root': { 
                  textTransform: 'none',
                  fontWeight: 600
                },
                '& .Mui-selected': { 
                  color: '#10b981 !important'
                },
                '& .MuiTabs-indicator': { 
                  bgcolor: '#10b981'
                }
              }}
            >
              <Tab label="Appointments Summary" icon={<AppointmentsIcon />} iconPosition="start" />
              <Tab label="Billing Summary" icon={<BillingIcon />} iconPosition="start" />
            </Tabs>
          </Box>

          {tabValue === 0 && (
            <Box sx={{ p: 3 }}>
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, borderRadius: '12px', bgcolor: '#f0fdf4', textAlign: 'center' }}>
                    <Typography variant="h3" fontWeight={700} sx={{ color: '#10b981' }}>
                      {stats.completedAppointments}
                    </Typography>
                    <Typography color="textSecondary">Completed</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, borderRadius: '12px', bgcolor: '#fef9c3', textAlign: 'center' }}>
                    <Typography variant="h3" fontWeight={700} sx={{ color: '#ca8a04' }}>
                      {stats.confirmedAppointments}
                    </Typography>
                    <Typography color="textSecondary">Confirmed</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, borderRadius: '12px', bgcolor: '#fee2e2', textAlign: 'center' }}>
                    <Typography variant="h3" fontWeight={700} sx={{ color: '#dc2626' }}>
                      {stats.pendingAppointments}
                    </Typography>
                    <Typography color="textSecondary">Pending</Typography>
                  </Paper>
                </Grid>
              </Grid>

              <Typography variant="h6" fontWeight={600} gutterBottom>
                Recent Appointments
              </Typography>
              
              {appointments.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography color="textSecondary">No appointments found</Typography>
                </Box>
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ bgcolor: '#f0fdf4' }}>
                        <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Time</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Doctor</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Reason</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {appointments.slice(0, 5).map((apt) => (
                        <TableRow key={apt.id} hover>
                          <TableCell>{formatDate(apt.appointment_date)}</TableCell>
                          <TableCell>{apt.appointment_time}</TableCell>
                          <TableCell>Dr. {apt.doctor_first_name} {apt.doctor_last_name}</TableCell>
                          <TableCell>{apt.reason || '-'}</TableCell>
                          <TableCell>
                            <Typography 
                              variant="body2" 
                              sx={{ 
                                textTransform: 'capitalize',
                                color: apt.status === 'completed' ? '#16a34a' : apt.status === 'confirmed' ? '#ca8a04' : '#6b7280'
                              }}
                            >
                              {apt.status}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          )}

          {tabValue === 1 && (
            <Box sx={{ p: 3 }}>
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, borderRadius: '12px', bgcolor: '#f0fdf4', textAlign: 'center' }}>
                    <Typography variant="h5" fontWeight={700} sx={{ color: '#10b981' }}>
                      {formatCurrency(stats.collectedRevenue)}
                    </Typography>
                    <Typography color="textSecondary">Collected</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, borderRadius: '12px', bgcolor: '#fef9c3', textAlign: 'center' }}>
                    <Typography variant="h5" fontWeight={700} sx={{ color: '#ca8a04' }}>
                      {formatCurrency(stats.pendingRevenue)}
                    </Typography>
                    <Typography color="textSecondary">Pending</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, borderRadius: '12px', bgcolor: '#ede9fe', textAlign: 'center' }}>
                    <Typography variant="h5" fontWeight={700} sx={{ color: '#7c3aed' }}>
                      {formatCurrency(stats.totalRevenue)}
                    </Typography>
                    <Typography color="textSecondary">Total</Typography>
                  </Paper>
                </Grid>
              </Grid>

              <Typography variant="h6" fontWeight={600} gutterBottom>
                Recent Bills
              </Typography>
              
              {bills.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography color="textSecondary">No bills found</Typography>
                </Box>
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ bgcolor: '#f0fdf4' }}>
                        <TableCell sx={{ fontWeight: 600 }}>Description</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Amount</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {bills.slice(0, 5).map((bill) => (
                        <TableRow key={bill.id} hover>
                          <TableCell>{bill.description}</TableCell>
                          <TableCell>{formatDate(bill.created_at)}</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>{formatCurrency(bill.total)}</TableCell>
                          <TableCell>
                            <Typography 
                              variant="body2" 
                              sx={{ 
                                textTransform: 'capitalize',
                                color: bill.status === 'paid' ? '#16a34a' : '#ca8a04'
                              }}
                            >
                              {bill.status}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          )}
        </Paper>
      </Container>
    </Box>
  );

  if (user?.role === 'admin') {
    return (
      <Box sx={{ display: 'flex', minHeight: '100vh', background: '#f9fafb' }}>
        <AdminSidebar activeItem="Reports" />
        <Box sx={{ ml: { xs: 0, md: '280px' }, flex: 1 }}>
          {pageContent}
        </Box>
      </Box>
    );
  }

  return pageContent;
};

export default Reports;

