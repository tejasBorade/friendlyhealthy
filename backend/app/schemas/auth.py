from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: UserRole
    

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# OTP-based Authentication Schemas

class SendOTPRequest(BaseModel):
    """Request to send OTP to phone number."""
    phone: str = Field(..., description="Phone number in E.164 format (e.g., +919876543210)")
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        # Basic validation for E.164 format
        if not v.startswith('+'):
            raise ValueError('Phone number must start with + and country code')
        if len(v) < 10 or len(v) > 15:
            raise ValueError('Phone number must be between 10-15 digits')
        return v


class SendOTPResponse(BaseModel):
    """Response after sending OTP."""
    success: bool
    message: str
    expires_in_minutes: int


class VerifyOTPRequest(BaseModel):
    """Request to verify OTP."""
    phone: str = Field(..., description="Phone number in E.164 format")
    otp: str = Field(..., min_length=4, max_length=8, description="OTP code")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Device information")
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        if not v.startswith('+'):
            raise ValueError('Phone number must start with + and country code')
        if len(v) < 10 or len(v) > 15:
            raise ValueError('Phone number must be between 10-15 digits')
        return v


class BiometricLoginRequest(BaseModel):
    """Request for biometric login using stored token."""
    biometric_token: str = Field(..., description="Encrypted biometric token from device")
    device_id: str = Field(..., description="Unique device identifier")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Device information")

