"""
API Routes for Notification Preferences
Sprint 2.2: Notification Delivery
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID
from datetime import time
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User
from app.models.prescription_extras import (
    NotificationPreference,
    NotificationChannel,
    DeviceToken,
    DevicePlatform
)
from app.services.push_notification import PushNotificationService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/notification-preferences", tags=["Notification Preferences"])


# Request/Response Models
class NotificationPreferenceResponse(BaseModel):
    medicine_reminders: bool
    follow_up_reminders: bool
    test_reminders: bool
    doctor_messages: bool
    report_alerts: bool
    security_alerts: bool
    quiet_hours_enabled: bool
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    preferred_channel: str
    
    class Config:
        from_attributes = True


class UpdatePreferenceRequest(BaseModel):
    medicine_reminders: Optional[bool] = None
    follow_up_reminders: Optional[bool] = None
    test_reminders: Optional[bool] = None
    doctor_messages: Optional[bool] = None
    report_alerts: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None  # HH:MM format
    preferred_channel: Optional[str] = None


class RegisterDeviceRequest(BaseModel):
    device_token: str
    platform: str  # android, ios, web
    device_info: Optional[dict] = None


class DeviceTokenResponse(BaseModel):
    id: UUID
    device_token: str
    platform: str
    is_active: bool
    registered_at: str
    
    class Config:
        from_attributes = True


@router.get("", response_model=NotificationPreferenceResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's notification preferences.
    
    Returns notification settings including quiet hours and preferred channel.
    """
    # Get preferences
    result = await db.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == current_user.id
        )
    )
    prefs = result.scalar_one_or_none()
    
    # Create default if not exists
    if not prefs:
        prefs = NotificationPreference(
            user_id=current_user.id,
            medicine_reminders=True,
            follow_up_reminders=True,
            test_reminders=True,
            doctor_messages=True,
            report_alerts=True,
            security_alerts=True,
            quiet_hours_enabled=True,
            quiet_hours_start=time(22, 0),  # 10 PM
            quiet_hours_end=time(7, 0),  # 7 AM
            preferred_channel=NotificationChannel.PUSH
        )
        db.add(prefs)
        await db.commit()
        await db.refresh(prefs)
    
    # Convert time to string
    response = NotificationPreferenceResponse(
        medicine_reminders=prefs.medicine_reminders,
        follow_up_reminders=prefs.follow_up_reminders,
        test_reminders=prefs.test_reminders,
        doctor_messages=prefs.doctor_messages,
        report_alerts=prefs.report_alerts,
        security_alerts=prefs.security_alerts,
        quiet_hours_enabled=prefs.quiet_hours_enabled,
        quiet_hours_start=prefs.quiet_hours_start.strftime("%H:%M") if prefs.quiet_hours_start else None,
        quiet_hours_end=prefs.quiet_hours_end.strftime("%H:%M") if prefs.quiet_hours_end else None,
        preferred_channel=prefs.preferred_channel.value
    )
    
    return response


@router.put("", response_model=NotificationPreferenceResponse)
async def update_preferences(
    request: UpdatePreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update notification preferences.
    
    Allows configuring which types of notifications to receive and quiet hours.
    """
    # Get preferences
    result = await db.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == current_user.id
        )
    )
    prefs = result.scalar_one_or_none()
    
    # Create if not exists
    if not prefs:
        prefs = NotificationPreference(
            user_id=current_user.id,
            preferred_channel=NotificationChannel.PUSH
        )
        db.add(prefs)
    
    # Update fields
    if request.medicine_reminders is not None:
        prefs.medicine_reminders = request.medicine_reminders
    if request.follow_up_reminders is not None:
        prefs.follow_up_reminders = request.follow_up_reminders
    if request.test_reminders is not None:
        prefs.test_reminders = request.test_reminders
    if request.doctor_messages is not None:
        prefs.doctor_messages = request.doctor_messages
    if request.report_alerts is not None:
        prefs.report_alerts = request.report_alerts
    if request.quiet_hours_enabled is not None:
        prefs.quiet_hours_enabled = request.quiet_hours_enabled
    
    # Parse and update quiet hours
    if request.quiet_hours_start:
        try:
            hour, minute = map(int, request.quiet_hours_start.split(":"))
            prefs.quiet_hours_start = time(hour, minute)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid time format. Use HH:MM (e.g., 22:00)"
            )
    
    if request.quiet_hours_end:
        try:
            hour, minute = map(int, request.quiet_hours_end.split(":"))
            prefs.quiet_hours_end = time(hour, minute)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid time format. Use HH:MM (e.g., 07:00)"
            )
    
    # Update preferred channel
    if request.preferred_channel:
        try:
            prefs.preferred_channel = NotificationChannel(request.preferred_channel)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid channel. Choose from: push, sms, whatsapp"
            )
    
    await db.commit()
    await db.refresh(prefs)
    
    # Convert to response
    response = NotificationPreferenceResponse(
        medicine_reminders=prefs.medicine_reminders,
        follow_up_reminders=prefs.follow_up_reminders,
        test_reminders=prefs.test_reminders,
        doctor_messages=prefs.doctor_messages,
        report_alerts=prefs.report_alerts,
        security_alerts=prefs.security_alerts,
        quiet_hours_enabled=prefs.quiet_hours_enabled,
        quiet_hours_start=prefs.quiet_hours_start.strftime("%H:%M") if prefs.quiet_hours_start else None,
        quiet_hours_end=prefs.quiet_hours_end.strftime("%H:%M") if prefs.quiet_hours_end else None,
        preferred_channel=prefs.preferred_channel.value
    )
    
    return response


@router.post("/devices/register", response_model=DeviceTokenResponse)
async def register_device(
    request: RegisterDeviceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Register device for push notifications.
    
    Stores FCM/APNS device token for sending push notifications.
    """
    try:
        platform = DevicePlatform(request.platform.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid platform. Choose from: android, ios, web"
        )
    
    # Register device
    device = await PushNotificationService.register_device(
        user_id=current_user.id,
        device_token=request.device_token,
        platform=platform,
        device_info=request.device_info,
        db=db
    )
    
    return DeviceTokenResponse(
        id=device.id,
        device_token=device.device_token,
        platform=device.platform.value,
        is_active=device.is_active,
        registered_at=device.registered_at.isoformat()
    )


@router.delete("/devices/{device_token}")
async def unregister_device(
    device_token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Unregister device token.
    
    Deactivates push notifications for this device.
    """
    # Verify ownership
    result = await db.execute(
        select(DeviceToken).where(
            DeviceToken.device_token == device_token,
            DeviceToken.user_id == current_user.id
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device token not found"
        )
    
    success = await PushNotificationService.unregister_device(device_token, db)
    
    if success:
        return {"success": True, "message": "Device unregistered successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unregister device"
        )


@router.get("/devices", response_model=list[DeviceTokenResponse])
async def get_registered_devices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all registered devices for current user.
    
    Shows active and inactive device tokens.
    """
    result = await db.execute(
        select(DeviceToken).where(
            DeviceToken.user_id == current_user.id
        ).order_by(DeviceToken.registered_at.desc())
    )
    devices = result.scalars().all()
    
    return [
        DeviceTokenResponse(
            id=device.id,
            device_token=device.device_token,
            platform=device.platform.value,
            is_active=device.is_active,
            registered_at=device.registered_at.isoformat()
        )
        for device in devices
    ]
