"""
Digital Signature Service
Sprint 1.3: Digital Signature System
"""

import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt

from app.models.doctor import Doctor
from app.models.prescription_extras import DigitalSignature
from app.core.config import settings


class SignatureService:
    """Service for managing digital signatures."""
    
    # Allowed image formats for signatures
    ALLOWED_FORMATS = {
        "image/png",
        "image/jpeg",
        "image/jpg"
    }
    
    # Max file size: 2MB
    MAX_FILE_SIZE = 2 * 1024 * 1024
    
    @staticmethod
    def validate_signature_file(file: UploadFile) -> None:
        """
        Validate signature image file.
        
        Args:
            file: Uploaded signature image
            
        Raises:
            HTTPException: If file is invalid
        """
        # Check content type
        if file.content_type not in SignatureService.ALLOWED_FORMATS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file format. Allowed: PNG, JPEG"
            )
    
    @staticmethod
    def hash_pin(pin: str) -> str:
        """
        Hash signature PIN using bcrypt.
        
        Args:
            pin: Plain text PIN (4-6 digits)
            
        Returns:
            Hashed PIN
        """
        return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
    
    @staticmethod
    def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
        """
        Verify PIN against hashed version.
        
        Args:
            plain_pin: Plain text PIN
            hashed_pin: Bcrypt hashed PIN
            
        Returns:
            True if PIN matches
        """
        return bcrypt.checkpw(plain_pin.encode(), hashed_pin.encode())
    
    @staticmethod
    async def create_signature(
        doctor_id: UUID,
        signature_data: bytes,
        pin: str,
        db: AsyncSession
    ) -> DigitalSignature:
        """
        Create or update doctor's digital signature.
        
        Args:
            doctor_id: Doctor's ID
            signature_data: Signature image bytes
            pin: Signature PIN (4-6 digits)
            db: Database session
            
        Returns:
            Created/updated DigitalSignature
        """
        # Check if signature already exists
        result = await db.execute(
            select(DigitalSignature).where(
                DigitalSignature.doctor_id == doctor_id
            )
        )
        existing = result.scalar_one_or_none()
        
        # Hash PIN
        hashed_pin = SignatureService.hash_pin(pin)
        
        # Encode signature as base64 for storage
        signature_base64 = base64.b64encode(signature_data).decode()
        
        if existing:
            # Update existing signature
            existing.signature_data = signature_base64
            existing.pin_hash = hashed_pin
            existing.is_active = True
            existing.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(existing)
            return existing
        else:
            # Create new signature
            signature = DigitalSignature(
                doctor_id=doctor_id,
                signature_data=signature_base64,
                pin_hash=hashed_pin,
                is_active=True
            )
            
            db.add(signature)
            await db.commit()
            await db.refresh(signature)
            return signature
    
    @staticmethod
    async def get_signature(
        doctor_id: UUID,
        db: AsyncSession
    ) -> Optional[DigitalSignature]:
        """
        Get doctor's digital signature.
        
        Args:
            doctor_id: Doctor's ID
            db: Database session
            
        Returns:
            DigitalSignature or None
        """
        result = await db.execute(
            select(DigitalSignature).where(
                DigitalSignature.doctor_id == doctor_id,
                DigitalSignature.is_active == True
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def verify_signature_pin(
        doctor_id: UUID,
        pin: str,
        db: AsyncSession
    ) -> bool:
        """
        Verify doctor's signature PIN.
        
        Args:
            doctor_id: Doctor's ID
            pin: Plain text PIN
            db: Database session
            
        Returns:
            True if PIN is correct
            
        Raises:
            HTTPException: If signature not found
        """
        signature = await SignatureService.get_signature(doctor_id, db)
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Digital signature not setup"
            )
        
        return SignatureService.verify_pin(pin, signature.pin_hash)
    
    @staticmethod
    async def update_pin(
        doctor_id: UUID,
        old_pin: str,
        new_pin: str,
        db: AsyncSession
    ) -> DigitalSignature:
        """
        Update signature PIN.
        
        Args:
            doctor_id: Doctor's ID
            old_pin: Current PIN
            new_pin: New PIN
            db: Database session
            
        Returns:
            Updated DigitalSignature
            
        Raises:
            HTTPException: If signature not found or old PIN invalid
        """
        signature = await SignatureService.get_signature(doctor_id, db)
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Digital signature not setup"
            )
        
        # Verify old PIN
        if not SignatureService.verify_pin(old_pin, signature.pin_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid current PIN"
            )
        
        # Update PIN
        signature.pin_hash = SignatureService.hash_pin(new_pin)
        signature.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(signature)
        
        return signature
    
    @staticmethod
    async def deactivate_signature(
        doctor_id: UUID,
        pin: str,
        db: AsyncSession
    ) -> None:
        """
        Deactivate doctor's signature.
        
        Args:
            doctor_id: Doctor's ID
            pin: Signature PIN
            db: Database session
            
        Raises:
            HTTPException: If signature not found or PIN invalid
        """
        signature = await SignatureService.get_signature(doctor_id, db)
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Digital signature not setup"
            )
        
        # Verify PIN
        if not SignatureService.verify_pin(pin, signature.pin_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid PIN"
            )
        
        # Deactivate
        signature.is_active = False
        signature.updated_at = datetime.utcnow()
        
        await db.commit()
    
    @staticmethod
    def decode_signature(signature_base64: str) -> bytes:
        """
        Decode base64 signature to bytes.
        
        Args:
            signature_base64: Base64 encoded signature
            
        Returns:
            Signature image bytes
        """
        return base64.b64decode(signature_base64)
