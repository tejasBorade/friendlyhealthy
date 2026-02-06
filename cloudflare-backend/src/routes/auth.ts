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
    return c.json({ error: 'Registration failed' }, 500);
  }
});

// POST /login
auth.post('/login', zValidator('json', loginSchema), async (c) => {
  try {
    const { email, password } = c.req.valid('json');
    
    // Get user
    const user = await c.env.DB.prepare(
      'SELECT id, email, password_hash, role FROM users WHERE email = ? AND is_active = 1'
    ).bind(email).first();
    
    if (!user) {
      return c.json({ error: 'Invalid credentials' }, 401);
    }
    
    // Verify password
    const validPassword = await bcrypt.compare(password, user.password_hash);
    if (!validPassword) {
      return c.json({ error: 'Invalid credentials' }, 401);
    }
    
    // Generate token
    const token = await generateToken(user.id, c.env.JWT_SECRET);
    
    return c.json({
      access_token: token,
      token_type: 'bearer',
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
      },
    });
  } catch (error) {
    console.error('Login error:', error);
    return c.json({ error: 'Login failed' }, 500);
  }
});

export default auth;
