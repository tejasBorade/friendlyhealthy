from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.patient import Patient
from pydantic import BaseModel
from datetime import date


router = APIRouter()


class PatientResponse(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    date_of_birth: date | None = None
    gender: str | None = None
    phone: str
    alternate_phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    
    class Config:
        from_attributes = True


class PatientsListResponse(BaseModel):
    patients: List[PatientResponse]
    total: int


@router.get("", response_model=PatientsListResponse)
async def get_patients(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all patients (Admin/Doctor only)."""
    # Only admin and doctors can view all patients
    if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view patients"
        )
    
    # Get all patients
    result = await db.execute(
        select(Patient).order_by(Patient.first_name, Patient.last_name)
    )
    patients = result.scalars().all()
    
    return PatientsListResponse(
        patients=[PatientResponse.model_validate(p) for p in patients],
        total=len(patients)
    )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single patient by ID."""
    # Patients can only view their own profile
    if current_user.role == UserRole.PATIENT:
        # Get the patient record for this user
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient or patient.id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this patient"
            )
    # Admins and doctors can view any patient
    elif current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view patients"
        )
    
    # Get the patient
    result = await db.execute(
        select(Patient).where(Patient.id == patient_id)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return PatientResponse.model_validate(patient)
