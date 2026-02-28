from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from app.core.database import get_db
from app.models.appointment import Appointment
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/appointments", tags=["Appointments"])


class AppointmentsListResponse(BaseModel):
    appointments: List[AppointmentResponse]


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new appointment."""
    # Get patient
    result = await db.execute(
        select(Patient).where(Patient.user_id == current_user.id)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    
   # Verify doctor exists
    result = await db.execute(
        select(Doctor).where(Doctor.id == appointment_data.doctor_id)
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Create appointment
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=appointment_data.doctor_id,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
        reason=appointment_data.reason,
        status='scheduled'
    )
    
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    
    return appointment


@router.get("", response_model=AppointmentsListResponse)
async def get_appointments(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's appointments."""
    if current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient:
            return {"appointments": []}
        
        query = select(Appointment).where(
            Appointment.patient_id == patient.id
        )
    elif current_user.role == UserRole.DOCTOR:
        result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        doctor = result.scalar_one_or_none()
        if not doctor:
            return {"appointments": []}
        
        query = select(Appointment).where(
            Appointment.doctor_id == doctor.id
        )
    else:
        # Admin can see all
        query = select(Appointment)
    
    if status:
        query = query.where(Appointment.status == status)
    
    query = query.order_by(Appointment.appointment_date.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    appointments = result.scalars().all()
    
    return {"appointments": appointments}


@router.get("/upcoming", response_model=List[AppointmentResponse])
async def get_upcoming_appointments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get upcoming appointments (today and future)."""
    today = date.today()
    
    if current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient:
            return []
        
        query = select(Appointment).where(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date >= today,
            Appointment.status == 'scheduled'
        )
    elif current_user.role == UserRole.DOCTOR:
        result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        doctor = result.scalar_one_or_none()
        if not doctor:
            return []
        
        query = select(Appointment).where(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date >= today,
            Appointment.status == 'scheduled'
        )
    else:
        query = select(Appointment).where(
            Appointment.appointment_date >= today,
            Appointment.status == 'scheduled'
        )
    
    result = await db.execute(query.order_by(Appointment.appointment_date.asc()))
    appointments = result.scalars().all()
    
    return appointments


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get appointment details."""
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    return appointment


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
async def update_appointment_status(
    appointment_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update appointment status."""
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    appointment.status = status
    
    await db.commit()
    await db.refresh(appointment)
    
    return appointment


@router.post("/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel an appointment."""
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    appointment.status = 'cancelled'
    
    await db.commit()
    
    return {"message": "Appointment cancelled successfully"}
