from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List
from uuid import UUID
from datetime import datetime, date
from app.core.database import get_db
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentStatusUpdate
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/appointments", tags=["Appointments"])


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
    
    # Generate appointment number
    today = date.today()
    result = await db.execute(
        select(func.count(Appointment.id)).where(
            func.date(Appointment.created_at) == today
        )
    )
    count = result.scalar() or 0
    appointment_number = f"APT{today.strftime('%Y%m%d')}{str(count + 1).zfill(4)}"
    
    # Create appointment
    appointment = Appointment(
        appointment_number=appointment_number,
        patient_id=patient.id,
        doctor_id=appointment_data.doctor_id,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
        reason_for_visit=appointment_data.reason_for_visit,
        symptoms=appointment_data.symptoms,
        status=AppointmentStatus.BOOKED
    )
    
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    
    return appointment


@router.get("", response_model=List[AppointmentResponse])
async def get_appointments(
    status: Optional[AppointmentStatus] = None,
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
            return []
        
        query = select(Appointment).where(
            Appointment.patient_id == patient.id,
            Appointment.is_deleted == False
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
            Appointment.is_deleted == False
        )
    else:
        # Admin can see all
        query = select(Appointment).where(Appointment.is_deleted == False)
    
    if status:
        query = query.where(Appointment.status == status)
    
    query = query.order_by(Appointment.appointment_date.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    appointments = result.scalars().all()
    
    return appointments


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get appointment details."""
    result = await db.execute(
        select(Appointment).where(
            Appointment.id == appointment_id,
            Appointment.is_deleted == False
        )
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
    appointment_id: UUID,
    status_update: AppointmentStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update appointment status."""
    result = await db.execute(
        select(Appointment).where(
            Appointment.id == appointment_id,
            Appointment.is_deleted == False
        )
    )
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    appointment.status = status_update.status
    if status_update.notes:
        appointment.doctor_notes = status_update.notes
    if status_update.cancellation_reason:
        appointment.cancellation_reason = status_update.cancellation_reason
        appointment.cancelled_by = current_user.id
        appointment.cancelled_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(appointment)
    
    return appointment


@router.post("/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: UUID,
    reason: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel an appointment."""
    result = await db.execute(
        select(Appointment).where(
            Appointment.id == appointment_id,
            Appointment.is_deleted == False
        )
    )
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancellation_reason = reason
    appointment.cancelled_by = current_user.id
    appointment.cancelled_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Appointment cancelled successfully"}
