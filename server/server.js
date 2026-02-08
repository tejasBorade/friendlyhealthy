import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import authRoutes from './routes/auth.js';
import doctorRoutes from './routes/doctors.js';
import appointmentRoutes from './routes/appointments.js';
import patientsRoutes from './routes/patients.js';
import medicalRecordsRoutes from './routes/medical-records.js';
import prescriptionsRoutes from './routes/prescriptions-routes.js';
import reportsRoutes from './routes/reports.js';
import billingRoutes from './routes/billing.js';
import notificationsRoutes from './routes/notifications.js';
import auditRoutes from './routes/audit.js';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000', 'http://127.0.0.1:3001'],
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy',
    environment: process.env.NODE_ENV,
    timestamp: new Date().toISOString()
  });
});

// API Routes
app.use('/api/auth', authRoutes);
app.use('/api/doctors', doctorRoutes);
app.use('/api/appointments', appointmentRoutes);
app.use('/api/patients', patientsRoutes);
app.use('/api/medical-records', medicalRecordsRoutes);
app.use('/api/prescriptions', prescriptionsRoutes);
app.use('/api/reports', reportsRoutes);
app.use('/api/billing', billingRoutes);
app.use('/api/notifications', notificationsRoutes);
app.use('/api/audit', auditRoutes);

// 404 handler
app.use((req, res) => {
  res.status(404).json({ message: 'Route not found' });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({ 
    message: 'Internal server error',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// Start server
app.listen(PORT, () => {
  console.log('');
  console.log('==========================================');
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📊 Environment: ${process.env.NODE_ENV}`);
  console.log(`💚 Health check: http://localhost:${PORT}/health`);
  console.log('==========================================');
  console.log('');
});
