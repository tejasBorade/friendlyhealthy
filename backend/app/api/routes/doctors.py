from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.models.doctor import Doctor, Specialization, DoctorSpecialization, Clinic
from app.models.user import User
from app.schemas.doctor import DoctorResponse, SpecializationResponse
from app.api.dependencies import get_current_user, get_current_doctor
from decimal import Decimal

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/specializations", response_model=List[SpecializationResponse])
async def get_specializations(db: AsyncSession = Depends(get_db)):
    """Get all specializations."""
    result = await db.execute(
        select(Specialization).where(Specialization.is_active == True)
    )
    specializations = result.scalars().all()
    return specializations


@router.get("/search", response_model=List[DoctorResponse])
async def search_doctors(
    specialization: Optional[str] = None,
    city: Optional[str] = None,
    min_fee: Optional[Decimal] = None,
    max_fee: Optional[Decimal] = None,
    is_verified: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Search doctors with filters."""
    query = select(Doctor).where(Doctor.is_deleted == False)
    
    if is_verified is not None:
        query = query.where(Doctor.is_verified == is_verified)
    
    if min_fee is not None:
        query = query.where(Doctor.consultation_fee >= min_fee)
    
    if max_fee is not None:
        query = query.where(Doctor.consultation_fee <= max_fee)
    
    # Add pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    doctors = result.scalars().all()
    
    return doctors


@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(doctor_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get doctor details by ID."""
    result = await db.execute(
        select(Doctor).where(
            Doctor.id == doctor_id,
            Doctor.is_deleted == False
        )
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    return doctor


@router.get("/{doctor_id}/availability")
async def get_doctor_availability(
    doctor_id: UUID,
    date: str,
    db: AsyncSession = Depends(get_db)
):
    """Get available time slots for a doctor on a specific date."""
    # This would call the PostgreSQL function get_available_slots
    # For now, return a simple response
    return {
        "doctor_id": doctor_id,
        "date": date,
        "slots": []
    }


@router.get("/me", response_model=DoctorResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db)
):
    """Get current doctor's profile."""
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
