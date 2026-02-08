import express from 'express';
import pool from '../config/database.js';
import { authenticate, authorize } from '../middleware/auth.js';

const router = express.Router();

// Log audit entry
const logAudit = async (userId, action, entityType, entityId, oldValues, newValues, req) => {
  try {
    await pool.query(
      `INSERT INTO audit_logs 
       (user_id, action, entity_type, entity_id, old_values, new_values, ip_address, user_agent) 
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
      [
        userId,
        action,
        entityType,
        entityId,
        oldValues ? JSON.stringify(oldValues) : null,
        newValues ? JSON.stringify(newValues) : null,
        req.ip,
        req.get('user-agent')
      ]
    );
  } catch (error) {
    console.error('Audit log error:', error);
  }
};

// Get audit logs (admin only)
router.get('/', authenticate, authorize('admin'), async (req, res) => {
  try {
    const { entityType, entityId, userId, fromDate, toDate, limit = 100 } = req.query;
    
    let query = `
      SELECT a.*, 
             u.email as user_email,
             u.role as user_role
      FROM audit_logs a
      LEFT JOIN users u ON a.user_id = u.id
      WHERE 1=1
    `;
    const params = [];
    
    if (entityType) {
      params.push(entityType);
      query += ` AND a.entity_type = $${params.length}`;
    }
    
    if (entityId) {
      params.push(entityId);
      query += ` AND a.entity_id = $${params.length}`;
    }
    
    if (userId) {
      params.push(userId);
      query += ` AND a.user_id = $${params.length}`;
    }
    
    if (fromDate) {
      params.push(fromDate);
      query += ` AND a.created_at >= $${params.length}`;
    }
    
    if (toDate) {
      params.push(toDate);
      query += ` AND a.created_at <= $${params.length}`;
    }
    
    params.push(limit);
    query += ` ORDER BY a.created_at DESC LIMIT $${params.length}`;
    
    const result = await pool.query(query, params);
    
    res.json({ logs: result.rows });
  } catch (error) {
    console.error('Get audit logs error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Get audit log statistics
router.get('/stats', authenticate, authorize('admin'), async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT 
        action,
        entity_type,
        COUNT(*) as count
      FROM audit_logs
      WHERE created_at >= NOW() - INTERVAL '30 days'
      GROUP BY action, entity_type
      ORDER BY count DESC
    `);
    
    res.json({ stats: result.rows });
  } catch (error) {
    console.error('Get audit stats error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

export { logAudit };
export default router;
