import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { prettyJSON } from 'hono/pretty-json';
import auth from './routes/auth';
import doctors from './routes/doctors';
import appointments from './routes/appointments';
import prescriptions from './routes/prescriptions';
import billing from './routes/billing';
import medicalRecords from './routes/medical-records';

type Bindings = {
  DB: D1Database;
  JWT_SECRET: string;
  ENVIRONMENT: string;
};

const app = new Hono<{ Bindings: Bindings }>();

// Middleware
app.use('*', cors({
  origin: ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002', 'http://localhost:3003', 'https://friendlyhealthy.pages.dev'],
  credentials: true,
}));
app.use('*', logger());
app.use('*', prettyJSON());

// Health check
app.get('/health', (c) => {
  return c.json({
    status: 'healthy',
    environment: c.env.ENVIRONMENT,
    timestamp: new Date().toISOString(),
  });
});

// API routes
app.route('/api/v1/auth', auth);
app.route('/api/v1/doctors', doctors);
app.route('/api/v1/appointments', appointments);
app.route('/api/v1/prescriptions', prescriptions);
app.route('/api/v1/billing', billing);
app.route('/api/v1/medical-records', medicalRecords);

// 404 handler
app.notFound((c) => {
  return c.json({ error: 'Not found' }, 404);
});

// Error handler
app.onError((err, c) => {
  console.error(err);
  return c.json({
    error: 'Internal server error',
    message: c.env.ENVIRONMENT === 'development' ? err.message : undefined,
  }, 500);
});

export default app;
