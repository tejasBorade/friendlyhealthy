"""
API Routes for Digital Signatures
Sprint 1.3: Digital Signature System
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, constr
from typing import Optional
from uuid import UUID
from io import BytesIO

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.doctor import Doctor
from app.services.signature_service import SignatureService
from app.api.dependencies import get_current_user


router = APIRouter(prefix="/signatures", tags=["Digital Signatures"])


# Request/Response Models
class SetupSignatureRequest(BaseModel):
    """Request to setup signature with PIN."""
    pin: constr(min_length=4, max_length=6, pattern=r'^\d+$')
    
    class Config:
        json_schema_extra = {
            "example": {
                "pin": "1234"
            }
        }


class VerifyPINRequest(BaseModel):
    """Request to verify signature PIN."""
    pin: constr(min_length=4, max_length=6, pattern=r'^\d+$')


class UpdatePINRequest(BaseModel):
    """Request to update signature PIN."""
    old_pin: constr(min_length=4, max_length=6, pattern=r'^\d+$')
    new_pin: constr(min_length=4, max_length=6, pattern=r'^\d+$')


class SignatureStatusResponse(BaseModel):
    """Signature status response."""
    has_signature: bool
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@router.post("/setup", status_code=status.HTTP_201_CREATED)
async def setup_signature(
    pin: str = File(..., description="4-6 digit PIN", regex=r'^\d{4,6}$'),
    signature: UploadFile = File(..., description="Signature image (PNG/JPEG, max 2MB)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload digital signature with PIN (Doctor only).
    
    The signature will be used for signing prescriptions.
    PIN is required to sign prescriptions.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can setup signatures"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Validate PIN format
    if not pin.isdigit() or len(pin) < 4 or len(pin) > 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PIN must be 4-6 digits"
        )
    
    # Validate file
    SignatureService.validate_signature_file(signature)
    
    # Read file data
    file_data = await signature.read()
    
    # Check file size
    if len(file_data) > SignatureService.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {SignatureService.MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Create signature
    sig = await SignatureService.create_signature(
        doctor_id=doctor.id,
        signature_data=file_data,
        pin=pin,
        db=db
    )
    
    return {
        "success": True,
        "message": "Digital signature setup successfully",
        "signature_id": str(sig.id)
    }


@router.get("/status", response_model=SignatureStatusResponse)
async def get_signature_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get signature setup status.
    
    Returns whether signature is setup and active.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can check signature status"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Get signature
    signature = await SignatureService.get_signature(doctor.id, db)
    
    if not signature:
        return SignatureStatusResponse(
            has_signature=False,
            is_active=False
        )
    
    return SignatureStatusResponse(
        has_signature=True,
        is_active=signature.is_active,
        created_at=signature.created_at.isoformat() if signature.created_at else None,
        updated_at=signature.updated_at.isoformat() if signature.updated_at else None
    )


@router.get("/download")
async def download_signature(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download signature image.
    
    Returns the signature as PNG/JPEG image.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can download signatures"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Get signature
    signature = await SignatureService.get_signature(doctor.id, db)
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Digital signature not setup"
        )
    
    # Decode signature
    image_data = SignatureService.decode_signature(signature.signature_data)
    
    # Return as streaming response
    return StreamingResponse(
        BytesIO(image_data),
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename=signature_{doctor.id}.png"
        }
    )


@router.post("/verify-pin")
async def verify_pin(
    request: VerifyPINRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify signature PIN.
    
    Used before signing prescriptions.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can verify PIN"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Verify PIN
    is_valid = await SignatureService.verify_signature_pin(
        doctor_id=doctor.id,
        pin=request.pin,
        db=db
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid PIN"
        )
    
    return {
        "success": True,
        "message": "PIN verified successfully"
    }


@router.put("/update-pin")
async def update_pin(
    request: UpdatePINRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update signature PIN.
    
    Requires current PIN for verification.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update PIN"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Update PIN
    await SignatureService.update_pin(
        doctor_id=doctor.id,
        old_pin=request.old_pin,
        new_pin=request.new_pin,
        db=db
    )
    
    return {
        "success": True,
        "message": "PIN updated successfully"
    }


@router.delete("/deactivate")
async def deactivate_signature(
    request: VerifyPINRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate signature.
    
    Requires PIN for verification. Can be reactivated by uploading new signature.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can deactivate signatures"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Deactivate signature
    await SignatureService.deactivate_signature(
        doctor_id=doctor.id,
        pin=request.pin,
        db=db
    )
    
    return {
        "success": True,
        "message": "Signature deactivated successfully"
    }
