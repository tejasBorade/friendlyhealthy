from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.models.medical import PatientMedicalHistory
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.medical_history import (
    MedicalHistoryCreate, MedicalHistoryUpdate, MedicalHistoryResponse
)
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/medical-history", tags=["Medical History"])


@router.post("", response_model=MedicalHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_history(
    history_data: MedicalHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create medical history record (Doctor only)."""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create medical history records"
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
    
    # Verify patient exists
    result = await db.execute(
        select(Patient).where(Patient.id == history_data.patient_id)
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Create medical history
    history = PatientMedicalHistory(
        patient_id=history_data.patient_id,
        doctor_id=doctor.id,
        appointment_id=history_data.appointment_id,
        recorded_date=history_data.recorded_date,
        past_illnesses=history_data.past_illnesses,
        allergies=history_data.allergies,
        chronic_diseases=history_data.chronic_diseases,
        surgeries=history_data.surgeries,
        family_medical_history=history_data.family_medical_history,
        current_medications=history_data.current_medications,
        notes=history_data.notes,
        created_by=current_user.id,
        version=1
    )
    
    db.add(history)
    await db.commit()
    await db.refresh(history)
    
    return history


@router.get("/patient/{patient_id}", response_model=List[MedicalHistoryResponse])
async def get_patient_history(
    patient_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get patient's medical history."""
    # Verify access rights
    if current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient or patient.id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    query = select(PatientMedicalHistory).where(
        PatientMedicalHistory.patient_id == patient_id,
        PatientMedicalHistory.is_deleted == False
    ).order_by(PatientMedicalHistory.recorded_date.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    history = result.scalars().all()
    
    return history


@router.get("/{history_id}", response_model=MedicalHistoryResponse)
async def get_medical_history(
    history_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific medical history record."""
    result = await db.execute(
        select(PatientMedicalHistory).where(
            PatientMedicalHistory.id == history_id,
            PatientMedicalHistory.is_deleted == False
        )
    )
    history = result.scalar_one_or_none()
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical history record not found"
        )
    
    return history


@router.put("/{history_id}", response_model=MedicalHistoryResponse)
async def update_medical_history(
    history_id: UUID,
    history_data: MedicalHistoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update medical history record (Doctor only)."""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update medical history"
        )
    
    # Get history record
    result = await db.execute(
        select(PatientMedicalHistory).where(
            PatientMedicalHistory.id == history_id,
            PatientMedicalHistory.is_deleted == False
        )
    )
    history = result.scalar_one_or_none()
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical history record not found"
        )
    
    # Update fields
    update_data = history_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(history, field, value)
    
    history.version += 1
    
    await db.commit()
    await db.refresh(history)
    
    return history


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical_history(
    history_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete medical history record (Doctor/Admin only)."""
    if current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    result = await db.execute(
        select(PatientMedicalHistory).where(PatientMedicalHistory.id == history_id)
    )
    history = result.scalar_one_or_none()
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical history record not found"
        )
    
    history.is_deleted = True
    await db.commit()
    
    return None
