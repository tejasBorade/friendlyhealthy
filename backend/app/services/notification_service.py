"""
Notification service for sending various types of notifications.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.models.notification import Notification, NotificationType, NotificationPriority
from app.models.user import User
from app.services.celery_tasks import send_email_task, send_sms_task


async def create_notification(
    db: AsyncSession,
    user_id: UUID,
    notification_type: NotificationType,
    title: str,
    message: str,
    priority: NotificationPriority = NotificationPriority.NORMAL,
    related_entity_type: str = None,
    related_entity_id: UUID = None
) -> Notification:
    """Create a notification in the database."""
    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        priority=priority,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id
    )
    
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    
    return notification


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
