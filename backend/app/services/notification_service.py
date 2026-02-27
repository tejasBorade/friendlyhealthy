"""
Unified Notification Service
Sprint 2.2: Notification Delivery

Multi-channel notification delivery with fallback:
1. Push notification (if enabled and device tokens exist)
2. WhatsApp (if enabled and push fails)
3. SMS (if all else fails)
"""

from typing import Dict, List
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.user import User
from app.models.prescription_extras import NotificationPreference, NotificationChannel
from app.services.push_notification import PushNotificationService
from app.services.whatsapp_service import WhatsAppService
from app.services.otp_service import OTPService


class NotificationService:
    """Unified notification service with multi-channel delivery."""
    
    @staticmethod
    async def get_user_phone(user_id: UUID, db: AsyncSession) -> str:
        """Get user's phone number."""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        return user.phone_number if user else None
    
    @staticmethod
    async def get_notification_preferences(
        user_id: UUID,
        db: AsyncSession
    ) -> NotificationPreference:
        """Get user's notification preferences."""
        result = await db.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id
            )
        )
        prefs = result.scalar_one_or_none()
        
        # Return default if not set
        if not prefs:
            prefs = NotificationPreference(
                user_id=user_id,
                medicine_reminders=True,
                follow_up_reminders=True,
                test_reminders=True,
                preferred_channel=NotificationChannel.PUSH
            )
            db.add(prefs)
            await db.commit()
            await db.refresh(prefs)
        
        return prefs
    
    @staticmethod
    async def should_send_now(
        user_id: UUID,
        db: AsyncSession
    ) -> bool:
        """
        Check if notification should be sent now (respects quiet hours).
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            True if notification can be sent
        """
        prefs = await NotificationService.get_notification_preferences(user_id, db)
        
        if not prefs.quiet_hours_enabled:
            return True
        
        # Check if current time is within quiet hours
        now = datetime.now().time()
        
        if prefs.quiet_hours_start and prefs.quiet_hours_end:
            start = prefs.quiet_hours_start
            end = prefs.quiet_hours_end
            
            # Handle overnight quiet hours (e.g., 22:00 - 07:00)
            if start > end:
                if now >= start or now < end:
                    return False
            else:
                if start <= now < end:
                    return False
        
        return True
    
    @staticmethod
    async def send_notification(
        user_id: UUID,
        notification_type: str,
        title: str,
        message: str,
        data: Dict = None,
        force_send: bool = False,
        db: AsyncSession = None
    ) -> Dict:
        """
        Send notification through appropriate channel with fallback.
        
        Args:
            user_id: User ID
            notification_type: Type of notification (medicine_reminder, follow_up_reminder, test_reminder)
            title: Notification title
            message: Notification message
            data: Optional data payload
            force_send: Skip quiet hours check
            db: Database session
            
        Returns:
            Dict with delivery status and channel used
        """
        # Check quiet hours
        if not force_send:
            if not await NotificationService.should_send_now(user_id, db):
                return {
                    "success": False,
                    "reason": "quiet_hours",
                    "message": "Notification suppressed due to quiet hours"
                }
        
        # Get preferences
        prefs = await NotificationService.get_notification_preferences(user_id, db)
        
        # Check if notification type is enabled
        if notification_type == "medicine_reminder" and not prefs.medicine_reminders:
            return {"success": False, "reason": "disabled", "message": "Medicine reminders disabled"}
        elif notification_type == "follow_up_reminder" and not prefs.follow_up_reminders:
            return {"success": False, "reason": "disabled", "message": "Follow-up reminders disabled"}
        elif notification_type == "test_reminder" and not prefs.test_reminders:
            return {"success": False, "reason": "disabled", "message": "Test reminders disabled"}
        
        phone_number = await NotificationService.get_user_phone(user_id, db)
        
        # Try channels in order based on preference
        channels_to_try = [prefs.preferred_channel]
        
        # Add fallback channels
        if NotificationChannel.PUSH not in channels_to_try:
            channels_to_try.append(NotificationChannel.PUSH)
        if NotificationChannel.WHATSAPP not in channels_to_try and settings.WHATSAPP_ENABLED:
            channels_to_try.append(NotificationChannel.WHATSAPP)
        if NotificationChannel.SMS not in channels_to_try:
            channels_to_try.append(NotificationChannel.SMS)
        
        last_error = None
        
        for channel in channels_to_try:
            try:
                if channel == NotificationChannel.PUSH:
                    result = await PushNotificationService.send_notification(
                        user_id=user_id,
                        title=title,
                        body=message,
                        data=data or {},
                        db=db
                    )
                    
                    if result.get("success") and result.get("sent", 0) > 0:
                        return {
                            "success": True,
                            "channel": "push",
                            "sent": result["sent"]
                        }
                    
                    last_error = result.get("error", "No devices or failed to send")
                
                elif channel == NotificationChannel.WHATSAPP and settings.WHATSAPP_ENABLED:
                    if phone_number:
                        result = await WhatsAppService.send_message(phone_number, f"*{title}*\n\n{message}")
                        
                        if result.get("success"):
                            return {
                                "success": True,
                                "channel": "whatsapp",
                                "message_sid": result["message_sid"]
                            }
                        
                        last_error = result.get("error", "Failed to send WhatsApp")
                
                elif channel == NotificationChannel.SMS:
                    if phone_number:
                        # Use OTP service's SMS sending capability
                        from twilio.rest import Client
                        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                        msg = client.messages.create(
                            body=f"{title}: {message}",
                            from_=settings.TWILIO_PHONE_NUMBER,
                            to=phone_number
                        )
                        
                        return {
                            "success": True,
                            "channel": "sms",
                            "message_sid": msg.sid
                        }
            
            except Exception as e:
                last_error = str(e)
                continue
        
        # All channels failed
        return {
            "success": False,
            "reason": "all_channels_failed",
            "error": last_error
        }
    
    @staticmethod
    async def send_medicine_reminder(
        user_id: UUID,
        medicine_name: str,
        dosage: str,
        timing_label: str,
        db: AsyncSession
    ) -> Dict:
        """Send medicine reminder notification."""
        return await NotificationService.send_notification(
            user_id=user_id,
            notification_type="medicine_reminder",
            title=f"💊 Medicine Reminder - {timing_label}",
            message=f"Time to take {medicine_name} ({dosage})",
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
    ) -> Dict:
        """Send follow-up appointment reminder."""
        if days_remaining == 0:
            title = "📅 Follow-up Today"
            message = f"You have a follow-up with Dr. {doctor_name} today"
        elif days_remaining == 1:
            title = "📅 Follow-up Tomorrow"
            message = f"Reminder: Follow-up with Dr. {doctor_name} tomorrow"
        else:
            title = "📅 Upcoming Follow-up"
            message = f"Follow-up with Dr. {doctor_name} in {days_remaining} days ({follow_up_date})"
        
        return await NotificationService.send_notification(
            user_id=user_id,
            notification_type="follow_up_reminder",
            title=title,
            message=message,
            data={
                "type": "follow_up_reminder",
                "doctor_name": doctor_name,
                "follow_up_date": follow_up_date,
                "days_remaining": str(days_remaining)
            },
            force_send=True,  # Follow-ups are important
            db=db
        )
    
    @staticmethod
    async def send_test_reminder(
        user_id: UUID,
        test_name: str,
        due_date: str,
        db: AsyncSession
    ) -> Dict:
        """Send test completion reminder."""
        return await NotificationService.send_notification(
            user_id=user_id,
            notification_type="test_reminder",
            title="🔬 Test Reminder",
            message=f"Reminder to complete {test_name}. Due by {due_date}",
            data={
                "type": "test_reminder",
                "test_name": test_name,
                "due_date": due_date
            },
            db=db
        )


# Legacy functions for backward compatibility


async def send_appointment_confirmation(
    db: AsyncSession,
    user_id: UUID,
    appointment_id: UUID,
    appointment_details: dict
):
    """Send appointment confirmation notification."""
    title = "Appointment Confirmed"
    message = f"Your appointment with Dr. {appointment_details['doctor_name']} on {appointment_details['date']} at {appointment_details['time']} has been confirmed."
    
    await create_notification(
        db=db,
        user_id=user_id,
        notification_type=NotificationType.APPOINTMENT,
        title=title,
        message=message,
        priority=NotificationPriority.HIGH,
        related_entity_type="appointment",
        related_entity_id=appointment_id
    )
    
    # Send email if user has email
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user and user.email:
        send_email_task.delay(user.email, title, message)


async def send_appointment_reminder(
    db: AsyncSession,
    user_id: UUID,
    appointment_id: UUID,
    appointment_details: dict
):
    """Send appointment reminder notification."""
    title = "Appointment Reminder"
    message = f"Reminder: You have an appointment with Dr. {appointment_details['doctor_name']} tomorrow at {appointment_details['time']}."
    
    await create_notification(
        db=db,
        user_id=user_id,
        notification_type=NotificationType.APPOINTMENT,
        title=title,
        message=message,
        priority=NotificationPriority.HIGH,
        related_entity_type="appointment",
        related_entity_id=appointment_id
    )
    
    # Send SMS for reminders
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user and user.email:
        send_email_task.delay(user.email, title, message)


async def send_prescription_notification(
    db: AsyncSession,
    user_id: UUID,
    prescription_id: UUID
):
    """Send new prescription notification."""
    title = "New Prescription"
    message = "Your doctor has created a new prescription for you. You can view and download it from your dashboard."
    
    await create_notification(
        db=db,
        user_id=user_id,
        notification_type=NotificationType.PRESCRIPTION,
        title=title,
        message=message,
        priority=NotificationPriority.NORMAL,
        related_entity_type="prescription",
        related_entity_id=prescription_id
    )


async def send_bill_notification(
    db: AsyncSession,
    user_id: UUID,
    bill_id: UUID,
    amount: str
):
    """Send bill notification."""
    title = "New Bill Generated"
    message = f"A bill of {amount} has been generated. Please review and make the payment."
    
    await create_notification(
        db=db,
        user_id=user_id,
        notification_type=NotificationType.BILLING,
        title=title,
        message=message,
        priority=NotificationPriority.NORMAL,
        related_entity_type="bill",
        related_entity_id=bill_id
    )


async def send_report_upload_notification(
    db: AsyncSession,
    user_id: UUID,
    report_id: UUID,
    report_name: str
):
    """Send report upload notification."""
    title = "Medical Report Uploaded"
    message = f"A new medical report '{report_name}' has been uploaded to your account."
    
    await create_notification(
        db=db,
        user_id=user_id,
        notification_type=NotificationType.GENERAL,
        title=title,
        message=message,
        priority=NotificationPriority.LOW,
        related_entity_type="report",
        related_entity_id=report_id
    )


async def send_payment_confirmation(
    db: AsyncSession,
    user_id: UUID,
    bill_id: UUID,
    amount: str,
    transaction_id: str
):
    """Send payment confirmation notification."""
    title = "Payment Successful"
    message = f"Your payment of {amount} has been received successfully. Transaction ID: {transaction_id}"
    
    await create_notification(
        db=db,
        user_id=user_id,
        notification_type=NotificationType.BILLING,
        title=title,
        message=message,
        priority=NotificationPriority.NORMAL,
        related_entity_type="bill",
        related_entity_id=bill_id
    )
