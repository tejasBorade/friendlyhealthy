from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token, validate_password_strength
from app.models.user import User, RefreshToken, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.auth import (
    UserCreate, UserLogin, TokenResponse, RefreshTokenRequest, UserResponse,
    SendOTPRequest, SendOTPResponse, VerifyOTPRequest, BiometricLoginRequest
)
from app.services.otp_service import otp_service
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Validate password strength
    if not validate_password_strength(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet strength requirements"
        )
    
    # Check if user exists
    result = await db.execute(
        select(User).where(User.email == user_data.email, User.is_deleted == False)
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        is_active=True,
        is_verified=False
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token_str = create_refresh_token({"sub": str(user.id)})
    
    # Store refresh token
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(refresh_token)
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        user=UserResponse.from_orm(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user and return JWT tokens."""
    # Find user
    result = await db.execute(
        select(User).where(User.email == credentials.email, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    
    # Generate tokens
    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token_str = create_refresh_token({"sub": str(user.id)})
    
    # Store refresh token
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(refresh_token)
    await db.commit()
    await db.refresh(user)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        user=UserResponse.from_orm(user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    # Decode refresh token
    payload = decode_token(request.refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    
    # Verify refresh token exists and not revoked
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == request.refresh_token,
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None)
        )
    )
    stored_token = result.scalar_one_or_none()
    
    if not stored_token or stored_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Revoke old refresh token
    stored_token.revoked_at = datetime.utcnow()
    
    # Store new refresh token
    refresh_token = RefreshToken(
        user_id=user.id,
        token=new_refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(refresh_token)
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.from_orm(user)
    )


@router.post("/logout")
async def logout(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Logout user by revoking refresh token."""
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == request.refresh_token,
            RefreshToken.revoked_at.is_(None)
        )
    )
    token = result.scalar_one_or_none()
    
    if token:
        token.revoked_at = datetime.utcnow()
        await db.commit()
    
    return {"message": "Successfully logged out"}


# ================================
# OTP-Based Authentication Endpoints
# ================================

@router.post("/send-otp", response_model=SendOTPResponse)
async def send_otp(request: SendOTPRequest, db: AsyncSession = Depends(get_db)):
    """
    Send OTP to user's phone number.
    
    Used for OTP-based login flow. User must be registered first.
    """
    return await otp_service.send_otp(db, request.phone)


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(request: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    """
    Verify OTP and issue JWT tokens.
    
    Verifies the OTP sent to user's phone and returns access/refresh tokens.
    """
    # Verify OTP and get user
    user = await otp_service.verify_otp_and_login(
        db=db,
        phone=request.phone,
        otp=request.otp,
        device_info=request.device_info
    )
    
    # Generate tokens
    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token_str = create_refresh_token({"sub": str(user.id)})
    
    # Store refresh token
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(refresh_token)
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        user=UserResponse.from_orm(user)
    )


@router.post("/resend-otp", response_model=SendOTPResponse)
async def resend_otp(request: SendOTPRequest, db: AsyncSession = Depends(get_db)):
    """
    Resend OTP to user's phone number.
    
    Can be used if the previous OTP was not received or expired.
    """
    return await otp_service.resend_otp(db, request.phone)


@router.post("/biometric-login", response_model=TokenResponse)
async def biometric_login(request: BiometricLoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login using biometric authentication.
    
    This endpoint is used after initial OTP login. The app stores an encrypted
    biometric token on the device, which is sent here for verification.
    
    Note: The biometric_token should be the user_id encrypted on the device.
    In production, implement proper token encryption/decryption.
    """
    try:
        # In a real implementation, decrypt and validate the biometric token
        # For now, we'll treat it as a user_id
        # TODO: Implement proper biometric token encryption/decryption
        user_id = request.biometric_token
        
        # Get user
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == False)
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid biometric token"
            )
        
        # Verify device matches (optional security check)
        if user.last_device_info:
            stored_device_id = user.last_device_info.get('device_id')
            if stored_device_id and stored_device_id != request.device_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Device mismatch. Please login with OTP."
                )
        
        # Update last login and device info
        user.last_login = datetime.utcnow()
        if request.device_info:
            user.last_device_info = request.device_info
        
        # Generate tokens
        access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
        refresh_token_str = create_refresh_token({"sub": str(user.id)})
        
        # Store refresh token
        refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token_str,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(refresh_token)
        await db.commit()
        await db.refresh(user)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            user=UserResponse.from_orm(user)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid biometric token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user information.
    
    Returns the user profile including id, email, role, etc.
    For patients, also returns patient_id.
    For doctors, also returns doctor_id.
    Requires a valid Bearer token in the Authorization header.
    """
    user_data = UserResponse.from_orm(current_user)
    
    # Fetch patient_id if user is a patient
    if current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if patient:
            user_data.patient_id = patient.id
    
    # Fetch doctor_id if user is a doctor
    elif current_user.role == UserRole.DOCTOR:
        result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        doctor = result.scalar_one_or_none()
        if doctor:
            user_data.doctor_id = doctor.id
    
    return user_data
