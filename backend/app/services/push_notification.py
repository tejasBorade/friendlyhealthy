"""
Push Notification Service (FCM)
Sprint 2.2: Notification Delivery
"""

from typing import List, Dict, Optional
from uuid import UUID
import json

from firebase_admin import messaging, credentials, initialize_app
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.prescription_extras import DeviceToken, DevicePlatform
from app.models.user import User


class PushNotificationService:
    """Service for sending push notifications via Firebase Cloud Messaging."""
    
    _app = None
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK."""
        if cls._app is None and settings.FIREBASE_CREDENTIALS_PATH:
            try:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                cls._app = initialize_app(cred)
            except Exception as e:
                print(f"Failed to initialize Firebase: {e}")
    
    @staticmethod
    async def send_notification(
        user_id: UUID,
        title: str,
        body: str,
        data: Dict = None,
        db: AsyncSession = None
    ) -> Dict:
        """
        Send push notification to all active devices of a user.
        
        Args:
            user_id: User ID
            title: Notification title
            body: Notification body
            data: Optional data payload
            db: Database session
            
        Returns:
            Dict with success count and failed tokens
        """
        if not PushNotificationService._app:
            PushNotificationService.initialize()
        
        if not db:
            return {"error": "Database session required"}
        
        # Get user's active device tokens
        result = await db.execute(
            select(DeviceToken).where(
                DeviceToken.user_id == user_id,
                DeviceToken.is_active == True
            )
        )
        devices = result.scalars().all()
        
        if not devices:
            return {
                "success": False,
                "message": "No active devices found",
                "sent": 0
            }
        
        # Prepare messages
        tokens = [device.device_token for device in devices]
        
        # Create multicast message
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            tokens=tokens
        )
        
        try:
            # Send
            response = messaging.send_multicast(message)
            
            # Handle failed tokens
            failed_tokens = []
            if response.failure_count > 0:
                for idx, resp in enumerate(response.responses):
                    if not resp.success:
                        failed_tokens.append(tokens[idx])
                        # Deactivate invalid tokens
                        device = devices[idx]
                        device.is_active = False
                
                await db.commit()
            
            return {
                "success": True,
                "sent": response.success_count,
                "failed": response.failure_count,
                "failed_tokens": failed_tokens
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sent": 0
            }
    
    @staticmethod
    async def send_medicine_reminder(
        user_id: UUID,
        medicine_name: str,
        dosage: str,
        timing_label: str,
        db: AsyncSession
    ):
        """
        Send medicine reminder notification.
        
        Args:
            user_id: Patient user ID
            medicine_name: Medicine name
            dosage: Dosage information
            timing_label: Time label (Morning/Afternoon/Night)
            db: Database session
        """
        return await PushNotificationService.send_notification(
            user_id=user_id,
            title=f"💊 Medicine Reminder - {timing_label}",
            body=f"Time to take {medicine_name} ({dosage})",
            data={
                "type": "medicine_reminder",
                "medicine_name": medicine_name,
                "dosage": dosage,
                "timing": timing_label
            },
            db=db
        )
    
    @staticmethod
    async def send_follow_up_reminder(
        user_id: UUID,
        doctor_name: str,
        follow_up_date: str,
        days_remaining: int,
        db: AsyncSession
    ):
        """
        Send follow-up appointment reminder.
        
        Args:
            user_id: Patient user ID
            doctor_name: Doctor's name
            follow_up_date: Follow-up date string
            days_remaining: Days until follow-up
            db: Database session
        """
        if days_remaining == 0:
            title = "📅 Follow-up Today"
            body = f"You have a follow-up with Dr. {doctor_name} today"
        elif days_remaining == 1:
            title = "📅 Follow-up Tomorrow"
            body = f"Reminder: Follow-up with Dr. {doctor_name} tomorrow"
        else:
            title = "📅 Upcoming Follow-up"
            body = f"Follow-up with Dr. {doctor_name} in {days_remaining} days ({follow_up_date})"
        
        return await PushNotificationService.send_notification(
            user_id=user_id,
            title=title,
            body=body,
            data={
                "type": "follow_up_reminder",
                "doctor_name": doctor_name,
                "follow_up_date": follow_up_date,
                "days_remaining": str(days_remaining)
            },
            db=db
        )
    
    @staticmethod
    async def send_test_reminder(
        user_id: UUID,
        test_name: str,
        due_date: str,
        db: AsyncSession
    ):
        """
        Send test completion reminder.
        
        Args:
            user_id: Patient user ID
            test_name: Test name
            due_date: Test due date
            db: Database session
        """
        return await PushNotificationService.send_notification(
            user_id=user_id,
            title="🔬 Test Reminder",
            body=f"Reminder to complete {test_name}. Due by {due_date}",
            data={
                "type": "test_reminder",
                "test_name": test_name,
                "due_date": due_date
            },
            db=db
        )
    
    @staticmethod
    async def register_device(
        user_id: UUID,
        device_token: str,
        platform: DevicePlatform,
        device_info: Dict = None,
        db: AsyncSession = None
    ) -> DeviceToken:
        """
        Register or update device token for push notifications.
        
        Args:
            user_id: User ID
            device_token: FCM device token
            platform: Device platform (android/ios/web)
            device_info: Optional device metadata
            db: Database session
            
        Returns:
            DeviceToken object
        """
        # Check if token already exists
        result = await db.execute(
            select(DeviceToken).where(DeviceToken.device_token == device_token)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing
            existing.user_id = user_id
            existing.platform = platform
            existing.device_info = device_info
            existing.is_active = True
            from datetime import datetime
            existing.last_used_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(existing)
            return existing
        else:
            # Create new
            device = DeviceToken(
                user_id=user_id,
                device_token=device_token,
                platform=platform,
                device_info=device_info,
                is_active=True
            )
            
            db.add(device)
            await db.commit()
            await db.refresh(device)
            return device
    
    @staticmethod
    async def unregister_device(
        device_token: str,
        db: AsyncSession
    ) -> bool:
        """
        Unregister device token.
        
        Args:
            device_token: FCM device token
            db: Database session
            
        Returns:
            True if successful
        """
        result = await db.execute(
            select(DeviceToken).where(DeviceToken.device_token == device_token)
        )
        device = result.scalar_one_or_none()
        
        if device:
            device.is_active = False
            await db.commit()
            return True
        
        return False
