"""
Prescription Service for SymptoTrack
Handles prescription signing, locking, PDF generation, and search.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from fastapi import HTTPException, status
import logging

from app.core.security import verify_password
from app.models.medical import Prescription, PrescriptionMedicine
from app.models.prescription_extras import (
    DigitalSignature, 
    PrescriptionSignature,
    PrescriptionTemplate
)
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.services.pdf_generator import PDFGenerator

logger = logging.getLogger(__name__)


class PrescriptionService:
    """Service for managing prescriptions with signing, PDF generation, and search."""

    def __init__(self):
        """Initialize prescription service."""
        self.pdf_generator = PDFGenerator()

    async def verify_signature_pin(
        self, 
        db: AsyncSession, 
        doctor_id: UUID, 
        pin: str
    ) -> DigitalSignature:
        """
        Verify doctor's signature PIN.
        
        Args:
            db: Database session
            doctor_id: Doctor UUID
            pin: PIN to verify
            
        Returns:
            DigitalSignature: Doctor's signature record
            
        Raises:
            HTTPException: If signature not found or PIN invalid
        """
        # Get doctor's signature
        result = await db.execute(
            select(DigitalSignature).where(
                DigitalSignature.doctor_id == doctor_id,
                DigitalSignature.is_active == True
            )
        )
        signature = result.scalar_one_or_none()
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Digital signature not set up. Please set up your signature first."
            )
        
        # Verify PIN
        if not verify_password(pin, signature.signature_pin_hash):
            logger.warning(f"Invalid signature PIN attempt for doctor {doctor_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature PIN"
            )
        
        return signature

    async def sign_prescription(
        self,
        db: AsyncSession,
        prescription_id: UUID,
        doctor_id: UUID,
        signature_pin: str,
        generate_pdf: bool = True
    ) -> Dict[str, Any]:
        """
        Sign a prescription with doctor's digital signature.
        
        Args:
            db: Database session
            prescription_id: Prescription UUID
            doctor_id: Doctor UUID
            signature_pin: Doctor's signature PIN
            generate_pdf: Whether to generate PDF immediately
            
        Returns:
            dict: Success message and prescription details
            
        Raises:
            HTTPException: If prescription not found, already signed, or PIN invalid
        """
        # Get prescription
        result = await db.execute(
            select(Prescription).where(
                Prescription.id == prescription_id,
                Prescription.doctor_id == doctor_id,
                Prescription.is_deleted == False
            )
        )
        prescription = result.scalar_one_or_none()
        
        if not prescription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prescription not found"
            )
        
        # Check if already signed
        if prescription.is_signed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prescription is already signed and locked"
            )
        
        # Verify signature PIN
        signature = await self.verify_signature_pin(db, doctor_id, signature_pin)
        
        # Sign prescription
        prescription.is_signed = True
        prescription.signed_at = datetime.utcnow()
        prescription.is_locked = True  # Lock prescription (immutable)
        
        # Create prescription signature record
        prescription_signature = PrescriptionSignature(
            prescription_id=prescription_id,
            signature_id=signature.id,
            signed_at=datetime.utcnow(),
            is_locked=True
        )
        db.add(prescription_signature)
        
        # Generate PDF if requested
        pdf_path = None
        if generate_pdf:
            try:
                pdf_path = await self.pdf_generator.generate_prescription_pdf(
                    db=db,
                    prescription_id=prescription_id
                )
                prescription.pdf_path = pdf_path
            except Exception as e:
                logger.error(f"Failed to generate PDF for prescription {prescription_id}: {str(e)}")
                # Don't fail the signing if PDF generation fails
        
        await db.commit()
        await db.refresh(prescription)
        
        logger.info(f"Prescription {prescription_id} signed by doctor {doctor_id}")
        
        return {
            "success": True,
            "message": "Prescription signed successfully",
            "prescription_id": prescription_id,
            "signed_at": prescription.signed_at,
            "pdf_path": pdf_path
        }

    async def get_prescription_pdf(
        self,
        db: AsyncSession,
        prescription_id: UUID,
        user_id: UUID,
        user_role: str
    ) -> str:
        """
        Get or generate prescription PDF.
        
        Args:
            db: Database session
            prescription_id: Prescription UUID
            user_id: Requesting user UUID
            user_role: User role (doctor/patient)
            
        Returns:
            str: PDF file path
            
        Raises:
            HTTPException: If prescription not found or unauthorized
        """
        # Get prescription
        result = await db.execute(
            select(Prescription).where(
                Prescription.id == prescription_id,
                Prescription.is_deleted == False
            )
        )
        prescription = result.scalar_one_or_none()
        
        if not prescription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prescription not found"
            )
        
        # Verify authorization
        if user_role == "doctor":
            result = await db.execute(
                select(Doctor).where(Doctor.user_id == user_id)
            )
            doctor = result.scalar_one_or_none()
            if not doctor or prescription.doctor_id != doctor.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized to access this prescription"
                )
        elif user_role == "patient":
            result = await db.execute(
                select(Patient).where(Patient.user_id == user_id)
            )
            patient = result.scalar_one_or_none()
            if not patient or prescription.patient_id != patient.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized to access this prescription"
                )
        
        # Check if prescription is signed
        if not prescription.is_signed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prescription must be signed before generating PDF"
            )
        
        # Return existing PDF or generate new one
        if prescription.pdf_path:
            return prescription.pdf_path
        
        # Generate PDF
        try:
            pdf_path = await self.pdf_generator.generate_prescription_pdf(
                db=db,
                prescription_id=prescription_id
            )
            prescription.pdf_path = pdf_path
            await db.commit()
            return pdf_path
        except Exception as e:
            logger.error(f"Failed to generate PDF for prescription {prescription_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate prescription PDF"
            )

    async def search_prescriptions(
        self,
        db: AsyncSession,
        patient_id: Optional[UUID] = None,
        doctor_id: Optional[UUID] = None,
        medicine_name: Optional[str] = None,
        diagnosis: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        is_signed: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Search prescriptions with various filters.
        
        Args:
            db: Database session
            patient_id: Filter by patient
            doctor_id: Filter by doctor
            medicine_name: Filter by medicine name (partial match)
            diagnosis: Filter by diagnosis (partial match)
            date_from: Filter by date range start
            date_to: Filter by date range end
            is_signed: Filter by signed status
            page: Page number
            page_size: Items per page
            
        Returns:
            dict: Paginated prescription list with metadata
        """
        # Build query
        query = select(Prescription).where(Prescription.is_deleted == False)
        
        # Apply filters
        if patient_id:
            query = query.where(Prescription.patient_id == patient_id)
        
        if doctor_id:
            query = query.where(Prescription.doctor_id == doctor_id)
        
        if date_from:
            query = query.where(Prescription.prescription_date >= date_from)
        
        if date_to:
            query = query.where(Prescription.prescription_date <= date_to)
        
        if is_signed is not None:
            query = query.where(Prescription.is_signed == is_signed)
        
        # Medicine name filter (requires join with prescription_medicines)
        if medicine_name:
            query = query.join(PrescriptionMedicine).where(
                PrescriptionMedicine.medicine_name.ilike(f"%{medicine_name}%")
            )
        
        # Diagnosis filter (requires join with consultations)
        # Note: This would need a join with consultations table
        # Skipping for now to keep it simple
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.order_by(Prescription.prescription_date.desc())
        query = query.offset(offset).limit(page_size)
        
        # Execute query
        result = await db.execute(query)
        prescriptions = result.scalars().all()
        
        return {
            "prescriptions": prescriptions,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def get_active_prescriptions(
        self,
        db: AsyncSession,
        patient_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Get patient's currently active prescriptions (medicines not yet completed).
        
        Args:
            db: Database session
            patient_id: Patient UUID
            
        Returns:
            list: Active prescriptions with remaining days info
        """
        today = date.today()
        
        # Get all signed prescriptions for this patient
        result = await db.execute(
            select(Prescription).where(
                Prescription.patient_id == patient_id,
                Prescription.is_signed == True,
                Prescription.is_deleted == False
            ).order_by(Prescription.prescription_date.desc())
        )
        prescriptions = result.scalars().all()
        
        active_prescriptions = []
        
        for prescription in prescriptions:
            # Get medicines for this prescription
            result = await db.execute(
                select(PrescriptionMedicine).where(
                    PrescriptionMedicine.prescription_id == prescription.id
                )
            )
            medicines = result.scalars().all()
            
            # Calculate days remaining (based on longest medicine duration)
            max_end_date = prescription.prescription_date
            for medicine in medicines:
                end_date = prescription.prescription_date + timedelta(days=medicine.duration_days)
                if end_date > max_end_date:
                    max_end_date = end_date
            
            days_remaining = (max_end_date - today).days
            
            # Only include if still active (days_remaining >= 0)
            if days_remaining >= 0:
                # Get doctor info
                result = await db.execute(
                    select(Doctor).where(Doctor.id == prescription.doctor_id)
                )
                doctor = result.scalar_one_or_none()
                doctor_name = f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else "Unknown"
                
                active_prescriptions.append({
                    "id": prescription.id,
                    "prescription_number": prescription.prescription_number,
                    "doctor_id": prescription.doctor_id,
                    "doctor_name": doctor_name,
                    "prescription_date": prescription.prescription_date,
                    "follow_up_date": prescription.follow_up_date,
                    "medicines": medicines,
                    "days_remaining": days_remaining
                })
        
        return active_prescriptions


# Singleton instance
prescription_service = PrescriptionService()
