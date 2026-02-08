import express from 'express';
import pool from '../config/database.js';
import { authenticate } from '../middleware/auth.js';

const router = express.Router();

// Get notifications for user
router.get('/', authenticate, async (req, res) => {
  try {
    const { userId } = req.user;
    const { isRead, type, limit = 50 } = req.query;
    
    let query = 'SELECT * FROM notifications WHERE user_id = $1';
    const params = [userId];
    
    if (isRead !== undefined) {
      params.push(isRead === 'true');
      query += ` AND is_read = $${params.length}`;
    }
    
    if (type) {
      params.push(type);
      query += ` AND notification_type = $${params.length}`;
    }
    
    params.push(limit);
    query += ` ORDER BY created_at DESC LIMIT $${params.length}`;
    
    const result = await pool.query(query, params);
    
    res.json({ notifications: result.rows });
  } catch (error) {
    console.error('Get notifications error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Create notification
router.post('/', authenticate, async (req, res) => {
  try {
    const {
      userId,
      notificationType,
      title,
      message,
      priority,
      sendVia,
      scheduledTime,
      referenceType,
      referenceId
    } = req.body;
    
    const result = await pool.query(
      `INSERT INTO notifications 
       (user_id, notification_type, title, message, priority, send_via, scheduled_time, reference_type, reference_id) 
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) 
       RETURNING *`,
      [userId, notificationType, title, message, priority, sendVia, scheduledTime, referenceType, referenceId]
    );
    
    res.status(201).json({ 
      message: 'Notification created successfully',
      notification: result.rows[0] 
    });
  } catch (error) {
    console.error('Create notification error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Mark notification as read
router.put('/:id/read', authenticate, async (req, res) => {
  try {
    const { id } = req.params;
    const { userId } = req.user;
    
    const result = await pool.query(
      'UPDATE notifications SET is_read = true WHERE id = $1 AND user_id = $2 RETURNING *',
      [id, userId]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Notification not found' });
    }
    
    res.json({ 
      message: 'Notification marked as read',
      notification: result.rows[0] 
    });
  } catch (error) {
    console.error('Mark notification read error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Mark all notifications as read
router.put('/read-all', authenticate, async (req, res) => {
  try {
    const { userId } = req.user;
    
    await pool.query(
      'UPDATE notifications SET is_read = true WHERE user_id = $1 AND is_read = false',
      [userId]
    );
    
    res.json({ message: 'All notifications marked as read' });
  } catch (error) {
    console.error('Mark all notifications read error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Delete notification
router.delete('/:id', authenticate, async (req, res) => {
  try {
    const { id } = req.params;
    const { userId } = req.user;
    
    await pool.query('DELETE FROM notifications WHERE id = $1 AND user_id = $2', [id, userId]);
    
    res.json({ message: 'Notification deleted successfully' });
  } catch (error) {
    console.error('Delete notification error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// Get unread count
router.get('/unread/count', authenticate, async (req, res) => {
  try {
    const { userId } = req.user;
    
    const result = await pool.query(
      'SELECT COUNT(*) as unread_count FROM notifications WHERE user_id = $1 AND is_read = false',
      [userId]
    );
    
    res.json({ unreadCount: parseInt(result.rows[0].unread_count) });
  } catch (error) {
    console.error('Get unread count error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

export default router;
