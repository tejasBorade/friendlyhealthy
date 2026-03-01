from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date
from app.core.database import get_db
from app.models.medical import Prescription, MedicalRecord
from app.models.user import User, UserRole
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.schemas.prescription import (
    PrescriptionCreate, PrescriptionResponse, PrescriptionUpdate,
    MedicalRecordCreate, MedicalRecordResponse, MedicalRecordUpdate
)
from app.api.dependencies import get_current_user
from app.services.celery_tasks import send_prescription_notification_email

router = APIRouter(tags=["Prescriptions"])


class PrescriptionCreateFrontend(BaseModel):
    """Schema for creating prescription from frontend."""
    patientId: int = Field(..., alias="patientId")
    appointmentId: Optional[int] = Field(None, alias="appointmentId")
    diagnosis: Optional[str] = None
    medicationName: str = Field(..., alias="medicationName")
    dosage: str
    frequency: str
    duration: str
    instructions: Optional[str] = None
    
    class Config:
        populate_by_name = True


class PrescriptionsListResponse(BaseModel):
    prescriptions: List[PrescriptionResponse]


@router.get("/prescriptions", response_model=PrescriptionsListResponse)
async def get_prescriptions(
    patient_id: Optional[int] = Query(None, alias="patientId"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get prescriptions for a patient."""
    query = select(Prescription)
    
    # If patientId is provided, filter by it
    if patient_id:
        # Verify authorization
        if current_user.role == UserRole.PATIENT:
            result = await db.execute(
                select(Patient).where(Patient.user_id == current_user.id)
            )
            patient = result.scalar_one_or_none()
            if not patient or patient.id != patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view these prescriptions"
                )
        query = query.where(Prescription.patient_id == patient_id)
    elif current_user.role == UserRole.PATIENT:
        # No patientId provided, get for current user
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient:
            return {"prescriptions": []}
        query = query.where(Prescription.patient_id == patient.id)
    
    elif current_user.role == UserRole.DOCTOR:
        # Get doctor's prescribed medications
        result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        doctor = result.scalar_one_or_none()
        if not doctor:
            return {"prescriptions": []}
        query = query.where(Prescription.doctor_id == doctor.id)
    
    elif current_user.role in [UserRole.ADMIN, UserRole.STAFF]:
        # Admins and staff can see all
        pass
    else:
        return {"prescriptions": []}
    
    result = await db.execute(query.order_by(Prescription.prescribed_date.desc()))
    prescriptions = result.scalars().all()
    return {"prescriptions": [PrescriptionResponse.from_model(p) for p in prescriptions]}


@router.get("/prescriptions/active", response_model=PrescriptionsListResponse)
async def get_active_prescriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get active prescriptions (prescribed in last 90 days)."""
    from datetime import date, timedelta
    
    cutoff_date = date.today() - timedelta(days=90)
    query = select(Prescription).where(Prescription.prescribed_date >= cutoff_date)
    
    if current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient:
            return {"prescriptions": []}
        query = query.where(Prescription.patient_id == patient.id)
    
    elif current_user.role == UserRole.DOCTOR:
        result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        doctor = result.scalar_one_or_none()
        if not doctor:
            return {"prescriptions": []}
        query = query.where(Prescription.doctor_id == doctor.id)
    
    result = await db.execute(query.order_by(Prescription.prescribed_date.desc()))
    prescriptions = result.scalars().all()
    return {"prescriptions": [PrescriptionResponse.from_model(p) for p in prescriptions]}


@router.get("/prescriptions/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription(
    prescription_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific prescription by ID."""
    result = await db.execute(
        select(Prescription).where(Prescription.id == prescription_id)
    )
    prescription = result.scalar_one_or_none()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient or prescription.patient_id != patient.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this prescription"
            )
    elif current_user.role == UserRole.DOCTOR:
        result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        doctor = result.scalar_one_or_none()
        if not doctor or prescription.doctor_id != doctor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this prescription"
            )
    # Admin and staff can see any prescription
    
    return PrescriptionResponse.from_model(prescription)


@router.post("/prescriptions", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_prescription(
    prescription_data: PrescriptionCreateFrontend,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new prescription (Doctor only)."""
    if current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create prescriptions"
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
    
    # Create prescription with doctor_id derived from current user
    prescription = Prescription(
        patient_id=prescription_data.patientId,
        doctor_id=doctor.id,
        medication_name=prescription_data.medicationName,
        dosage=prescription_data.dosage,
        frequency=prescription_data.frequency,
        duration=prescription_data.duration,
        instructions=prescription_data.instructions,
        prescribed_date=date.today()
    )
    db.add(prescription)
    await db.commit()
    await db.refresh(prescription)
    
    # Send email notification to patient
    try:
        # Get patient details
        patient_result = await db.execute(
            select(Patient).where(Patient.id == prescription.patient_id)
        )
        patient = patient_result.scalar_one_or_none()
        
        # Get patient user for email
        if patient:
            patient_user_result = await db.execute(
                select(User).where(User.id == patient.user_id)
            )
            patient_user = patient_user_result.scalar_one_or_none()
            
            if patient_user:
                # Count medicines (if prescription has medicines field)
                medicines_count = len(prescription.medicines) if hasattr(prescription, 'medicines') and prescription.medicines else 0
                
                # Send async email notification
                send_prescription_notification_email.delay(
                    patient_email=patient_user.email,
                    patient_name=patient.full_name,
                    doctor_name=doctor.full_name,
                    prescription_date=prescription.prescribed_date.isoformat(),
                    prescription_id=prescription.id,
                    medicines_count=medicines_count
                )
    except Exception as e:
        # Log error but don't fail the prescription creation
        print(f"Failed to send prescription notification email: {str(e)}")
    
    return PrescriptionResponse.from_model(prescription)


@router.get("/medical-history", response_model=List[MedicalRecordResponse])
async def get_medical_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get medical history for current user."""
    query = select(MedicalRecord)
    
    if current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient:
            return []
        query = query.where(MedicalRecord.patient_id == patient.id)
    
    elif current_user.role == UserRole.DOCTOR:
        result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        doctor = result.scalar_one_or_none()
        if not doctor:
            return []
        query = query.where(MedicalRecord.doctor_id == doctor.id)
    
    elif current_user.role in [UserRole.ADMIN, UserRole.STAFF]:
        # Admins can see all records
        pass
    else:
        return []
    
    result = await db.execute(query.order_by(MedicalRecord.visit_date.desc()))
    records = result.scalars().all()
    return records


@router.post("/medical-history", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    record_data: MedicalRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new medical record (Doctor only)."""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create medical records"
        )
    
    record = MedicalRecord(**record_data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record
