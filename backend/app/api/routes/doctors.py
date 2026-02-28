from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from app.core.database import get_db
from app.models.doctor import Doctor
from app.models.user import User, UserRole
from app.schemas.doctor import DoctorResponse
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/doctors", tags=["Doctors"])


class SpecializationResponse(BaseModel):
    specialization: str


class DoctorsListResponse(BaseModel):
    doctors: List[DoctorResponse]


@router.get("/specializations", response_model=List[SpecializationResponse])
async def get_specializations(db: AsyncSession = Depends(get_db)):
    """Get all unique specializations."""
    result = await db.execute(
        select(Doctor.specialization).distinct()
    )
    specializations = result.scalars().all()
    return [{"specialization": s} for s in specializations]


@router.get("", response_model=DoctorsListResponse)
async def get_doctors(
    specialization: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get list of doctors with optional filters."""
    query = select(Doctor).where(Doctor.is_available == True)
    
    if specialization:
        query = query.where(Doctor.specialization == specialization)
    
    # Add pagination
    query = query.offset(skip).limit(limit).order_by(Doctor.id.desc())
    
    result = await db.execute(query)
    doctors = result.scalars().all()
    
    return {"doctors": doctors}


@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(doctor_id: int, db: AsyncSession = Depends(get_db)):
    """Get doctor details by ID."""
    result = await db.execute(
        select(Doctor).where(Doctor.id == doctor_id)
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    return doctor


@router.get("/me", response_model=DoctorResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current doctor's profile."""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can access this endpoint"
        )
    
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    return doctor
