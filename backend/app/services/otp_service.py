"""
OTP Service for SymptoTrack
Handles OTP generation, verification, rate limiting, and SMS delivery.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status
from twilio.rest import Client
from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


class OTPService:
    """Service for managing OTP-based authentication."""

    def __init__(self):
        """Initialize OTP service with Twilio client."""
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        else:
            self.twilio_client = None
            logger.warning("Twilio credentials not configured. OTP SMS will not be sent.")

    def generate_otp(self) -> str:
        """Generate a random OTP of specified length."""
        return ''.join(random.choices(string.digits, k=settings.OTP_LENGTH))

    def hash_otp(self, otp: str) -> str:
        """Hash OTP for secure storage."""
        return hash_password(otp)

    def verify_otp(self, plain_otp: str, hashed_otp: str) -> bool:
        """Verify OTP against stored hash."""
        return verify_password(plain_otp, hashed_otp)

    async def send_otp_sms(self, phone: str, otp: str) -> bool:
        """
        Send OTP via SMS using Twilio.
        
        Args:
            phone: Phone number in E.164 format (e.g., +919876543210)
            otp: OTP code to send
            
        Returns:
            bool: True if SMS sent successfully, False otherwise.
        """
        if not self.twilio_client:
            # In development, log OTP instead of sending
            logger.info(f"OTP for {phone}: {otp} (SMS not configured)")
            return True

        try:
            message = self.twilio_client.messages.create(
                body=f"Your SymptoTrack verification code is: {otp}. Valid for {settings.OTP_EXPIRY_MINUTES} minutes. Do not share this code.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )
            logger.info(f"OTP SMS sent to {phone}. Message SID: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send OTP SMS to {phone}: {str(e)}")
            return False

    async def check_rate_limit(self, user: User) -> Tuple[bool, Optional[str]]:
        """
        Check if user is rate-limited or locked out.
        
        Args:
            user: User object to check
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        now = datetime.utcnow()

        # Check if user is locked out
        if user.locked_until and user.locked_until > now:
            remaining_minutes = int((user.locked_until - now).total_seconds() / 60)
            return False, f"Account locked due to too many failed attempts. Try again in {remaining_minutes} minutes."

        # Reset failed attempts if lockout period has passed
        if user.locked_until and user.locked_until <= now:
            user.failed_otp_attempts = 0
            user.locked_until = None
            return True, None

        # Check if max attempts exceeded
        if user.failed_otp_attempts >= settings.OTP_MAX_ATTEMPTS:
            user.locked_until = now + timedelta(minutes=settings.OTP_LOCKOUT_MINUTES)
            return False, f"Too many failed OTP attempts. Account locked for {settings.OTP_LOCKOUT_MINUTES} minutes."

        return True, None

    async def send_otp(self, db: AsyncSession, phone: str) -> dict:
        """
        Generate and send OTP to user's phone.
        
        Args:
            db: Database session
            phone: Phone number in E.164 format
            
        Returns:
            dict: Response with success status and message
        """
        # Find user by phone
        result = await db.execute(
            select(User).where(User.phone == phone, User.is_deleted == False)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number not registered"
            )

        # Check rate limit
        is_allowed, error_message = await self.check_rate_limit(user)
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_message
            )

        # Generate OTP
        otp = self.generate_otp()
        otp_hash = self.hash_otp(otp)
        otp_expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)

        # Update user with OTP details
        user.otp_hash = otp_hash
        user.otp_expires_at = otp_expires_at
        await db.commit()

        # Send OTP via SMS
        sms_sent = await self.send_otp_sms(phone, otp)
        if not sms_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP. Please try again."
            )

        logger.info(f"OTP sent to {phone}")
        return {
            "success": True,
            "message": f"OTP sent to {phone}",
            "expires_in_minutes": settings.OTP_EXPIRY_MINUTES
        }

    async def verify_otp_and_login(
        self,
        db: AsyncSession,
        phone: str,
        otp: str,
        device_info: Optional[dict] = None
    ) -> User:
        """
        Verify OTP and return user if valid.
        
        Args:
            db: Database session
            phone: Phone number
            otp: OTP code to verify
            device_info: Optional device information
            
        Returns:
            User: User object if OTP is valid
            
        Raises:
            HTTPException: If OTP is invalid or expired
        """
        # Find user by phone
        result = await db.execute(
            select(User).where(User.phone == phone, User.is_deleted == False)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number not registered"
            )

        # Check rate limit
        is_allowed, error_message = await self.check_rate_limit(user)
        if not is_allowed:
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_message
            )

        # Check if OTP exists
        if not user.otp_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No OTP sent to this phone number. Please request a new OTP."
            )

        # Check if OTP expired
        if not user.otp_expires_at or user.otp_expires_at < datetime.utcnow():
            user.otp_hash = None
            user.otp_expires_at = None
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired. Please request a new OTP."
            )

        # Verify OTP
        if not self.verify_otp(otp, user.otp_hash):
            user.failed_otp_attempts += 1
            await db.commit()
            
            remaining_attempts = settings.OTP_MAX_ATTEMPTS - user.failed_otp_attempts
            if remaining_attempts > 0:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid OTP. {remaining_attempts} attempts remaining."
                )
            else:
                user.locked_until = datetime.utcnow() + timedelta(minutes=settings.OTP_LOCKOUT_MINUTES)
                await db.commit()
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many failed attempts. Account locked for {settings.OTP_LOCKOUT_MINUTES} minutes."
                )

        # OTP verified successfully - reset attempts and clear OTP
        user.failed_otp_attempts = 0
        user.locked_until = None
        user.otp_hash = None
        user.otp_expires_at = None
        user.last_login = datetime.utcnow()
        
        if device_info:
            user.last_device_info = device_info

        await db.commit()
        await db.refresh(user)

        logger.info(f"User {user.id} logged in successfully via OTP")
        return user

    async def resend_otp(self, db: AsyncSession, phone: str) -> dict:
        """
        Resend OTP to user's phone.
        
        Args:
            db: Database session
            phone: Phone number
            
        Returns:
            dict: Response with success status
        """
        # Same as send_otp, but with a "resend" message
        return await self.send_otp(db, phone)


# Singleton instance
otp_service = OTPService()
