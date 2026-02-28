from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
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

router = APIRouter(tags=["Prescriptions"])


class PrescriptionsListResponse(BaseModel):
    prescriptions: List[PrescriptionResponse]


@router.get("/prescriptions", response_model=PrescriptionsListResponse)
async def get_prescriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get prescriptions for current user."""
    query = select(Prescription)
    
    if current_user.role == UserRole.PATIENT:
        # Get patient prescriptions
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
    return {"prescriptions": prescriptions}


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
    return {"prescriptions": prescriptions}


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
    
    return prescription


@router.post("/prescriptions", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_prescription(
    prescription_data: PrescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new prescription (Doctor only)."""
    if current_user.role != UserRole.DOCTOR:
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
    
    # Create prescription
    prescription = Prescription(**prescription_data.model_dump())
    db.add(prescription)
    await db.commit()
    await db.refresh(prescription)
    return prescription


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
