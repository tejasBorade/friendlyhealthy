"""
API Routes for Reminders
Sprint 2.1: Reminder Engine Core
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.reminder import (
    MedicineReminder,
    FollowUpReminder,
    TestReminder,
    ReminderStatus,
    FollowUpStatus,
    MedicineReminderLog
)
from app.services.reminder_service import ReminderService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/reminders", tags=["Reminders"])


# Request/Response Models
class MedicineReminderResponse(BaseModel):
    id: UUID
    prescription_id: UUID
    medicine_name: str
    dosage: str
    frequency_code: str
    timing_slots: List[dict]
    start_date: date
    end_date: date
    status: str
    is_active: bool
    total_taken: int
    total_missed: int
    
    class Config:
        from_attributes = True


class FollowUpReminderResponse(BaseModel):
    id: UUID
    prescription_id: UUID
    doctor_id: UUID
    follow_up_date: date
    status: str
    reminder_7day_sent: bool
    reminder_1day_sent: bool
    reminder_morning_sent: bool
    
    class Config:
        from_attributes = True


class TestReminderResponse(BaseModel):
    id: UUID
    prescription_id: UUID
    test_order_id: UUID
    test_name: str
    follow_up_date: Optional[date]
    upload_status: str
    reminder_3day_sent: bool
    reminder_1day_sent: bool
    
    class Config:
        from_attributes = True


class MarkTakenRequest(BaseModel):
    """Request to mark medicine as taken."""
    taken_at: Optional[datetime] = None


class SnoozeRequest(BaseModel):
    """Request to snooze reminder."""
    snooze_minutes: int = 15


@router.get("/medicines", response_model=List[MedicineReminderResponse])
async def get_medicine_reminders(
    active_only: bool = Query(True, description="Only show active reminders"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get medicine reminders for current patient.
    
    Returns list of active medicine reminders with timing information.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can view medicine reminders"
        )
    
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
    
    # Build query
    query = select(MedicineReminder).where(
        MedicineReminder.patient_id == patient.id
    )
    
    if active_only:
        query = query.where(
            and_(
                MedicineReminder.is_active == True,
                MedicineReminder.end_date >= date.today()
            )
        )
    
    query = query.order_by(MedicineReminder.start_date.desc())
    
    result = await db.execute(query)
    reminders = result.scalars().all()
    
    return reminders


@router.post("/medicines/{reminder_id}/taken")
async def mark_medicine_taken(
    reminder_id: UUID,
    request: MarkTakenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark medicine reminder as taken.
    
    Logs the action and updates reminder statistics.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can mark medicines as taken"
        )
    
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
    
    # Get reminder
    result = await db.execute(
        select(MedicineReminder).where(
            and_(
                MedicineReminder.id == reminder_id,
                MedicineReminder.patient_id == patient.id
            )
        )
    )
    reminder = result.scalar_one_or_none()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    # Update statistics
    reminder.total_taken += 1
    reminder.last_triggered_at = request.taken_at or datetime.utcnow()
    
    # Log the action
    log_entry = MedicineReminderLog(
        reminder_id=reminder_id,
        scheduled_time=datetime.utcnow(),
        action="taken",
        action_time=request.taken_at or datetime.utcnow()
    )
    db.add(log_entry)
    
    await db.commit()
    
    return {
        "success": True,
        "message": f"{reminder.medicine_name} marked as taken",
        "total_taken": reminder.total_taken
    }


@router.post("/medicines/{reminder_id}/snooze")
async def snooze_medicine_reminder(
    reminder_id: UUID,
    request: SnoozeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Snooze medicine reminder.
    
    Delays the reminder for specified minutes (default 15).
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can snooze reminders"
        )
    
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
    
    # Get reminder
    result = await db.execute(
        select(MedicineReminder).where(
            and_(
                MedicineReminder.id == reminder_id,
                MedicineReminder.patient_id == patient.id
            )
        )
    )
    reminder = result.scalar_one_or_none()
    
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    # Update snooze count
    reminder.snooze_count += 1
    
    # Calculate snooze time
    from datetime import timedelta
    snooze_until = datetime.utcnow() + timedelta(minutes=request.snooze_minutes)
    
    # Log the action
    log_entry = MedicineReminderLog(
        reminder_id=reminder_id,
        scheduled_time=datetime.utcnow(),
        action="snoozed",
        action_time=datetime.utcnow(),
        snoozed_until=snooze_until
    )
    db.add(log_entry)
    
    await db.commit()
    
    return {
        "success": True,
        "message": f"Reminder snoozed for {request.snooze_minutes} minutes",
        "snooze_until": snooze_until.isoformat()
    }


@router.get("/follow-ups", response_model=List[FollowUpReminderResponse])
async def get_follow_up_reminders(
    upcoming_only: bool = Query(True, description="Only show upcoming follow-ups"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get follow-up reminders for current patient.
    
    Returns list of scheduled follow-up appointments.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can view follow-up reminders"
        )
    
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
    
    # Build query
    query = select(FollowUpReminder).where(
        FollowUpReminder.patient_id == patient.id
    )
    
    if upcoming_only:
        query = query.where(
            and_(
                FollowUpReminder.status == FollowUpStatus.UPCOMING,
                FollowUpReminder.follow_up_date >= date.today()
            )
        )
    
    query = query.order_by(FollowUpReminder.follow_up_date.asc())
    
    result = await db.execute(query)
    reminders = result.scalars().all()
    
    return reminders


@router.get("/tests", response_model=List[TestReminderResponse])
async def get_test_reminders(
    pending_only: bool = Query(True, description="Only show pending tests"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get test reminders for current patient.
    
    Returns list of ordered tests that need to be completed.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can view test reminders"
        )
    
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
    
    # Build query
    query = select(TestReminder).where(
        TestReminder.patient_id == patient.id
    )
    
    if pending_only:
        query = query.where(
            TestReminder.upload_status == "ordered"
        )
    
    query = query.order_by(TestReminder.follow_up_date.asc().nullslast())
    
    result = await db.execute(query)
    reminders = result.scalars().all()
    
    return reminders


@router.post("/prescriptions/{prescription_id}/generate")
async def generate_reminders_for_prescription(
    prescription_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger reminder generation for a prescription.
    
    Normally happens automatically when prescription is signed.
    Useful for regenerating reminders if needed.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can generate reminders"
        )
    
    # Generate reminders
    result = await ReminderService.auto_generate_all_reminders(
        prescription_id=prescription_id,
        db=db
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    
    return result
