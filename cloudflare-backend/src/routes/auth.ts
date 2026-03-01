import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';
import { z } from 'zod';
import * as bcrypt from 'bcryptjs';
import { SignJWT, jwtVerify } from 'jose';

const auth = new Hono();

// Schemas
const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  role: z.enum(['patient', 'doctor', 'admin']),
});

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string(),
});

// Helper: Generate JWT
async function generateToken(userId: string, secret: string) {
  const encoder = new TextEncoder();
  const token = await new SignJWT({ sub: userId })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('15m')
    .sign(encoder.encode(secret));
  return token;
}

// Helper: Verify JWT and get user
async function verifyToken(token: string, secret: string) {
  try {
    const encoder = new TextEncoder();
    const { payload } = await jwtVerify(token, encoder.encode(secret));
    return payload;
  } catch (error) {
    return null;
  }
}

// POST /register
auth.post('/register', zValidator('json', registerSchema), async (c) => {
  try {
    const { email, password, role } = c.req.valid('json');
    
    // Check if user exists
    const existing = await c.env.DB.prepare(
      'SELECT id FROM users WHERE email = ?'
    ).bind(email).first();
    
    if (existing) {
      return c.json({ error: 'User already exists' }, 409);
    }
    
    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);
    
    // Insert user
    const result = await c.env.DB.prepare(
      'INSERT INTO users (id, email, password_hash, role, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?)'
    ).bind(
      crypto.randomUUID(),
      email,
      hashedPassword,
      role,
      1,
      new Date().toISOString()
    ).run();
    
    // Generate token
    const token = await generateToken(result.meta.last_row_id.toString(), c.env.JWT_SECRET);
    
    return c.json({
      access_token: token,
      token_type: 'bearer',
      user: {
        id: result.meta.last_row_id,
        email,
        role,
      },
    }, 201);
  } catch (error) {
    console.error('Register error:', error);
    console.error('Error details:', error instanceof Error ? error.message : String(error));
    return c.json({ error: 'Registration failed', details: error instanceof Error ? error.message : String(error) }, 500);
  }
});

// POST /login
auth.post('/login', zValidator('json', loginSchema), async (c) => {
  try {
    const { email, password } = c.req.valid('json');
    
    console.log('Login attempt for:', email);
    
    // Get user
    const user = await c.env.DB.prepare(
      'SELECT id, email, password_hash, role FROM users WHERE email = ? AND is_active = 1'
    ).bind(email).first();
    
    console.log('User found:', user ? 'yes' : 'no');
    
    if (!user) {
      return c.json({ error: 'Invalid credentials' }, 401);
    }
    
    // Verify password
    const validPassword = await bcrypt.compare(password, user.password_hash);
    console.log('Password valid:', validPassword);
    
    if (!validPassword) {
      return c.json({ error: 'Invalid credentials' }, 401);
    }
    
    // Generate access token
    const accessToken = await generateToken(user.id, c.env.JWT_SECRET);
    
    // Generate refresh token
    const encoder = new TextEncoder();
    const refreshToken = await new SignJWT({ sub: user.id, type: 'refresh' })
      .setProtectedHeader({ alg: 'HS256' })
      .setIssuedAt()
      .setExpirationTime('7d')
      .sign(encoder.encode(c.env.JWT_SECRET));
    
    // Store refresh token in database
    const tokenId = crypto.randomUUID();
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();
    await c.env.DB.prepare(
      'INSERT INTO refresh_tokens (id, user_id, token, expires_at, created_at) VALUES (?, ?, ?, ?, ?)'
    ).bind(tokenId, user.id, refreshToken, expiresAt, new Date().toISOString()).run();
    
    return c.json({
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: 'bearer',
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
      },
    });
  } catch (error) {
    console.error('Login error:', error);
    console.error('Error details:', error instanceof Error ? error.message : String(error));
    return c.json({ error: 'Login failed', details: error instanceof Error ? error.message : String(error) }, 500);
  }
});

// Schema for refresh token
const refreshTokenSchema = z.object({
  refresh_token: z.string(),
});

// POST /refresh
auth.post('/refresh', zValidator('json', refreshTokenSchema), async (c) => {
  try {
    const { refresh_token } = c.req.valid('json');
    
    // Verify and decode refresh token
    const encoder = new TextEncoder();
    const { payload } = await jwtVerify(refresh_token, encoder.encode(c.env.JWT_SECRET));
    
    if (payload.type !== 'refresh') {
      return c.json({ error: 'Invalid token type' }, 401);
    }
    
    const userId = payload.sub as string;
    
    // Check if refresh token exists and is not revoked
    const storedToken = await c.env.DB.prepare(
      'SELECT id, expires_at FROM refresh_tokens WHERE token = ? AND user_id = ? AND revoked_at IS NULL'
    ).bind(refresh_token, userId).first();
    
    if (!storedToken) {
      return c.json({ error: 'Invalid or revoked refresh token' }, 401);
    }
    
    // Check if token is expired
    if (new Date(storedToken.expires_at) < new Date()) {
      return c.json({ error: 'Refresh token expired' }, 401);
    }
    
    // Get user
    const user = await c.env.DB.prepare(
      'SELECT id, email, role FROM users WHERE id = ? AND is_active = 1'
    ).bind(userId).first();
    
    if (!user) {
      return c.json({ error: 'User not found or inactive' }, 401);
    }
    
    // Generate new tokens
    const newAccessToken = await generateToken(user.id, c.env.JWT_SECRET);
    const newRefreshToken = await new SignJWT({ sub: user.id, type: 'refresh' })
      .setProtectedHeader({ alg: 'HS256' })
      .setIssuedAt()
      .setExpirationTime('7d')
      .sign(encoder.encode(c.env.JWT_SECRET));
    
    // Revoke old refresh token
    await c.env.DB.prepare(
      'UPDATE refresh_tokens SET revoked_at = ? WHERE token = ?'
    ).bind(new Date().toISOString(), refresh_token).run();
    
    // Store new refresh token
    const newTokenId = crypto.randomUUID();
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();
    await c.env.DB.prepare(
      'INSERT INTO refresh_tokens (id, user_id, token, expires_at, created_at) VALUES (?, ?, ?, ?, ?)'
    ).bind(newTokenId, user.id, newRefreshToken, expiresAt, new Date().toISOString()).run();
    
    return c.json({
      access_token: newAccessToken,
      refresh_token: newRefreshToken,
      token_type: 'bearer',
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
      },
    });
  } catch (error) {
    console.error('Refresh token error:', error);
    return c.json({ error: 'Token refresh failed' }, 401);
  }
});

// GET /me - Get current user info
auth.get('/me', async (c) => {
  try {
    // Get token from Authorization header
    const authHeader = c.req.header('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return c.json({ error: 'Missing or invalid authorization header' }, 401);
    }

    const token = authHeader.substring(7); // Remove 'Bearer ' prefix
    
    // Verify token
    const payload = await verifyToken(token, c.env.JWT_SECRET);
    if (!payload || !payload.sub) {
      return c.json({ error: 'Invalid token' }, 401);
    }

    const userId = payload.sub as string;

    // Get user from database
    const user = await c.env.DB.prepare(
      'SELECT id, email, role, is_active FROM users WHERE id = ?'
    ).bind(userId).first();

    if (!user || !user.is_active) {
      return c.json({ error: 'User not found or inactive' }, 401);
    }

    // Base user response
    const userResponse: any = {
      id: user.id,
      email: user.email,
      role: user.role,
      is_active: user.is_active,
    };

    // If patient, get patient_id
    if (user.role === 'patient') {
      const patient = await c.env.DB.prepare(
        'SELECT id FROM patients WHERE user_id = ?'
      ).bind(userId).first();
      if (patient) {
        userResponse.patient_id = patient.id;
      }
    }

    // If doctor, get doctor_id
    if (user.role === 'doctor') {
      const doctor = await c.env.DB.prepare(
        'SELECT id FROM doctors WHERE user_id = ?'
      ).bind(userId).first();
      if (doctor) {
        userResponse.doctor_id = doctor.id;
      }
    }

    return c.json(userResponse);
  } catch (error) {
    console.error('Get current user error:', error);
    return c.json({ error: 'Failed to get user info' }, 500);
  }
});

export default auth;
