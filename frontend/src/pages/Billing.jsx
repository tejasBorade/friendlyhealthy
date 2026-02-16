import React, { useState, useEffect } from 'react';
import {
  Box, Container, Typography, Paper, Card, CardContent, Chip, 
  Grid, Divider, Avatar, CircularProgress, Alert, IconButton,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Dialog, DialogTitle, DialogContent, DialogActions, Button,
  FormControl, InputLabel, Select, MenuItem
} from '@mui/material';
import {
  Receipt as ReceiptIcon,
  Payment as PaymentIcon,
  AccountBalance as AccountIcon,
  CheckCircle as PaidIcon,
  HourglassEmpty as PendingIcon,
  CalendarMonth as CalendarIcon,
  CreditCard as CardIcon,
  AccountBalanceWallet as WalletIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon
} from '@mui/icons-material';
import api from '../services/api';
import { useSelector } from 'react-redux';
import AdminSidebar from '../components/AdminSidebar';

const Billing = () => {
  const { user } = useSelector((state) => state.auth);
  const [bills, setBills] = useState([]);
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [paymentOpen, setPaymentOpen] = useState(false);
  const [selectedBill, setSelectedBill] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('');
  const [paying, setPaying] = useState(false);

  useEffect(() => {
    fetchBills();
  }, []);

  const fetchBills = async () => {
    try {
      const response = await api.get('/billing');
      setBills(response.data.bills || []);
      setSummary(response.data.summary || {});
    } catch (err) {
      setError('Failed to load billing information');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handlePayNow = (bill) => {
    setSelectedBill(bill);
    setPaymentOpen(true);
  };

  const processPayment = async () => {
    if (!paymentMethod) return;
    setPaying(true);
    try {
      await api.patch(`/billing/${selectedBill.id}/pay`, { payment_method: paymentMethod });
      setPaymentOpen(false);
      fetchBills(); // Refresh bills
    } catch (err) {
      console.error(err);
    } finally {
      setPaying(false);
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

  const getStatusColor = (status) => {
    switch (status) {
      case 'paid': return { bg: '#dcfce7', color: '#16a34a' };
      case 'pending': return { bg: '#fef9c3', color: '#ca8a04' };
      case 'overdue': return { bg: '#fee2e2', color: '#dc2626' };
      default: return { bg: '#f3f4f6', color: '#6b7280' };
    }
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
          <AdminSidebar activeItem="Billing" />
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
              <ReceiptIcon sx={{ fontSize: 30, color: 'white' }} />
            </Avatar>
            <Box>
              <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
                Billing & Payments
              </Typography>
              <Typography sx={{ color: 'rgba(255,255,255,0.8)' }}>
                Manage your medical bills and payments
              </Typography>
            </Box>
          </Box>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: '12px' }}>{error}</Alert>
        )}

        {/* Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ borderRadius: '20px', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" variant="body2">Total Amount</Typography>
                    <Typography variant="h5" fontWeight={700} sx={{ color: '#10b981' }}>
                      {formatCurrency(summary.total_amount)}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: '#ecfdf5' }}>
                    <AccountIcon sx={{ color: '#10b981' }} />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ borderRadius: '20px', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" variant="body2">Paid</Typography>
                    <Typography variant="h5" fontWeight={700} sx={{ color: '#16a34a' }}>
                      {formatCurrency(summary.paid_amount)}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: '#dcfce7' }}>
                    <PaidIcon sx={{ color: '#16a34a' }} />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ borderRadius: '20px', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" variant="body2">Pending</Typography>
                    <Typography variant="h5" fontWeight={700} sx={{ color: '#ca8a04' }}>
                      {formatCurrency(summary.pending_amount)}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: '#fef9c3' }}>
                    <PendingIcon sx={{ color: '#ca8a04' }} />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ borderRadius: '20px', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" variant="body2">Total Bills</Typography>
                    <Typography variant="h5" fontWeight={700}>
                      {summary.total_bills || 0}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: '#ede9fe' }}>
                    <ReceiptIcon sx={{ color: '#7c3aed' }} />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Bills Table */}
        <Paper sx={{ borderRadius: '20px', overflow: 'hidden' }}>
          <Box sx={{ p: 3, borderBottom: '1px solid #e5e7eb' }}>
            <Typography variant="h6" fontWeight={600}>
              Billing History
            </Typography>
          </Box>
          
          {bills.length === 0 ? (
            <Box sx={{ p: 6, textAlign: 'center' }}>
              <ReceiptIcon sx={{ fontSize: 80, color: '#10b981', opacity: 0.5, mb: 2 }} />
              <Typography variant="h6" color="textSecondary">
                No bills found
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Your billing history will appear here
              </Typography>
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: '#f0fdf4' }}>
                    <TableCell sx={{ fontWeight: 600 }}>Description</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Amount</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Tax</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Total</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {bills.map((bill) => {
                    const statusStyle = getStatusColor(bill.status);
                    return (
                      <TableRow key={bill.id} hover>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight={600}>{bill.description}</Typography>
                            {bill.doctor_first_name && (
                              <Typography variant="caption" color="textSecondary">
                                Dr. {bill.doctor_first_name} {bill.doctor_last_name}
                              </Typography>
                            )}
                          </Box>
                        </TableCell>
                        <TableCell>{formatDate(bill.appointment_date || bill.created_at)}</TableCell>
                        <TableCell>{formatCurrency(bill.amount)}</TableCell>
                        <TableCell>{formatCurrency(bill.tax)}</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>{formatCurrency(bill.total)}</TableCell>
                        <TableCell>
                          <Chip 
                            label={bill.status.toUpperCase()} 
                            size="small"
                            sx={{ 
                              bgcolor: statusStyle.bg, 
                              color: statusStyle.color,
                              fontWeight: 600,
                              fontSize: '0.7rem'
                            }} 
                          />
                        </TableCell>
                        <TableCell>
                          {bill.status === 'pending' ? (
                            <Button
                              variant="contained"
                              size="small"
                              onClick={() => handlePayNow(bill)}
                              sx={{ 
                                borderRadius: '8px',
                                bgcolor: '#10b981',
                                '&:hover': { bgcolor: '#059669' }
                              }}
                            >
                              Pay Now
                            </Button>
                          ) : (
                            <IconButton size="small">
                              <DownloadIcon sx={{ color: '#10b981' }} />
                            </IconButton>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>

        {/* Payment Dialog */}
        <Dialog 
          open={paymentOpen} 
          onClose={() => setPaymentOpen(false)}
          maxWidth="sm"
          fullWidth
          PaperProps={{ sx: { borderRadius: '20px' } }}
        >
          <DialogTitle sx={{ 
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', 
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            gap: 2
          }}>
            <PaymentIcon />
            Make Payment
          </DialogTitle>
          <DialogContent sx={{ mt: 3 }}>
            {selectedBill && (
              <Box>
                <Paper sx={{ p: 3, borderRadius: '12px', bgcolor: '#f0fdf4', mb: 3 }}>
                  <Typography variant="h6" fontWeight={600} gutterBottom>
                    {selectedBill.description}
                  </Typography>
                  <Divider sx={{ my: 2 }} />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography>Amount:</Typography>
                    <Typography>{formatCurrency(selectedBill.amount)}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography>Tax (18%):</Typography>
                    <Typography>{formatCurrency(selectedBill.tax)}</Typography>
                  </Box>
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography fontWeight={600}>Total:</Typography>
                    <Typography fontWeight={600} color="primary">
                      {formatCurrency(selectedBill.total)}
                    </Typography>
                  </Box>
                </Paper>

                <FormControl fullWidth>
                  <InputLabel>Payment Method</InputLabel>
                  <Select
                    value={paymentMethod}
                    label="Payment Method"
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    sx={{ borderRadius: '12px' }}
                  >
                    <MenuItem value="Credit Card">
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CardIcon /> Credit Card
                      </Box>
                    </MenuItem>
                    <MenuItem value="Debit Card">
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CardIcon /> Debit Card
                      </Box>
                    </MenuItem>
                    <MenuItem value="UPI">
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <WalletIcon /> UPI
                      </Box>
                    </MenuItem>
                    <MenuItem value="Net Banking">
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AccountIcon /> Net Banking
                      </Box>
                    </MenuItem>
                  </Select>
                </FormControl>
              </Box>
            )}
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button 
              onClick={() => setPaymentOpen(false)}
              sx={{ borderRadius: '12px' }}
            >
              Cancel
            </Button>
            <Button 
              variant="contained"
              onClick={processPayment}
              disabled={!paymentMethod || paying}
              sx={{ 
                borderRadius: '12px',
                bgcolor: '#10b981',
                '&:hover': { bgcolor: '#059669' }
              }}
            >
              {paying ? <CircularProgress size={24} color="inherit" /> : 'Pay Now'}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );

  if (user?.role === 'admin') {
    return (
      <Box sx={{ display: 'flex', minHeight: '100vh', background: '#f9fafb' }}>
        <AdminSidebar activeItem="Billing" />
        <Box sx={{ ml: { xs: 0, md: '280px' }, flex: 1 }}>
          {pageContent}
        </Box>
      </Box>
    );
  }

  return pageContent;
};

export default Billing;

