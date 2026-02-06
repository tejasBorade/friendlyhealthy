from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from app.core.database import get_db
from app.core.config import settings
from app.models.medical import Consultation, Prescription, PrescriptionMedicine, PrescriptionHistory
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.prescription import (
    ConsultationCreate, ConsultationResponse,
    PrescriptionCreate, PrescriptionResponse, PrescriptionUpdate,
    MedicineResponse
)
from app.api.dependencies import get_current_user
import json

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


@router.post("/consultations", response_model=ConsultationResponse, status_code=status.HTTP_201_CREATED)
async def create_consultation(
    consultation_data: ConsultationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a consultation record (Doctor only)."""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create consultations"
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
    
    # Verify appointment exists and belongs to this doctor
    result = await db.execute(
        select(Appointment).where(
            Appointment.id == consultation_data.appointment_id,
            Appointment.doctor_id == doctor.id,
            Appointment.status == AppointmentStatus.CONFIRMED
        )
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found or not confirmed"
        )
    
    # Check if consultation already exists
    result = await db.execute(
        select(Consultation).where(Consultation.appointment_id == consultation_data.appointment_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Consultation already exists for this appointment"
        )
    
    # Create consultation
    consultation = Consultation(
        appointment_id=consultation_data.appointment_id,
        patient_id=appointment.patient_id,
        doctor_id=doctor.id,
        consultation_date=datetime.utcnow(),
        chief_complaint=consultation_data.chief_complaint,
        diagnosis=consultation_data.diagnosis,
        consultation_notes=consultation_data.consultation_notes,
        follow_up_required=consultation_data.follow_up_required,
        follow_up_after_days=consultation_data.follow_up_after_days
    )
    
    # Update appointment status
    appointment.status = AppointmentStatus.COMPLETED
    
    db.add(consultation)
    await db.commit()
    await db.refresh(consultation)
    
    return consultation


@router.post("", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_prescription(
    prescription_data: PrescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a prescription (Doctor only)."""
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
    
    # Verify consultation exists
    result = await db.execute(
        select(Consultation).where(
            Consultation.id == prescription_data.consultation_id,
            Consultation.doctor_id == doctor.id
        )
    )
    consultation = result.scalar_one_or_none()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    
    # Generate prescription number
    today = date.today()
    result = await db.execute(
        select(func.count(Prescription.id)).where(
            Prescription.prescription_date == today
        )
    )
    count = result.scalar() or 0
    prescription_number = f"RX{today.strftime('%Y%m%d')}{str(count + 1).zfill(4)}"
    
    # Create prescription
    prescription = Prescription(
        prescription_number=prescription_number,
        consultation_id=consultation.id,
        patient_id=consultation.patient_id,
        doctor_id=doctor.id,
        prescription_date=today,
        notes=prescription_data.notes,
        special_instructions=prescription_data.special_instructions,
        version=1
    )
    
    db.add(prescription)
    await db.flush()
    
    # Add medicines
    for medicine_data in prescription_data.medicines:
        medicine = PrescriptionMedicine(
            prescription_id=prescription.id,
            medicine_name=medicine_data.medicine_name,
            dosage=medicine_data.dosage,
            usage=medicine_data.usage,
            frequency=medicine_data.frequency,
            duration_days=medicine_data.duration_days,
            special_instructions=medicine_data.special_instructions
        )
        db.add(medicine)
    
    await db.commit()
    await db.refresh(prescription)
    
    # Load medicines
    result = await db.execute(
        select(PrescriptionMedicine).where(PrescriptionMedicine.prescription_id == prescription.id)
    )
    prescription.medicines = result.scalars().all()
    
    return prescription


@router.get("", response_model=List[PrescriptionResponse])
async def get_prescriptions(
    patient_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get prescriptions."""
    query = select(Prescription).where(Prescription.is_deleted == False)
    
    if current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if patient:
            query = query.where(Prescription.patient_id == patient.id)
        else:
            return []
    elif current_user.role == UserRole.DOCTOR:
        result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        doctor = result.scalar_one_or_none()
        if doctor:
            query = query.where(Prescription.doctor_id == doctor.id)
        else:
            return []
    elif patient_id:
        query = query.where(Prescription.patient_id == patient_id)
    
    query = query.order_by(Prescription.prescription_date.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    prescriptions = result.scalars().all()
    
    # Load medicines for each prescription
    for prescription in prescriptions:
        result = await db.execute(
            select(PrescriptionMedicine).where(PrescriptionMedicine.prescription_id == prescription.id)
        )
        prescription.medicines = result.scalars().all()
    
    return prescriptions


@router.get("/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription(
    prescription_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get prescription details."""
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
    
    # Load medicines
    result = await db.execute(
        select(PrescriptionMedicine).where(PrescriptionMedicine.prescription_id == prescription.id)
    )
    prescription.medicines = result.scalars().all()
    
    return prescription


@router.put("/{prescription_id}", response_model=PrescriptionResponse)
async def update_prescription(
    prescription_id: UUID,
    prescription_data: PrescriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update prescription (Doctor only, creates new version)."""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update prescriptions"
        )
    
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
    
    # Save current version to history
    result = await db.execute(
        select(PrescriptionMedicine).where(PrescriptionMedicine.prescription_id == prescription.id)
    )
    current_medicines = result.scalars().all()
    
    history_data = {
        "prescription_number": prescription.prescription_number,
        "notes": prescription.notes,
        "special_instructions": prescription.special_instructions,
        "medicines": [
            {
                "medicine_name": m.medicine_name,
                "dosage": m.dosage,
                "usage": m.usage,
                "frequency": m.frequency,
                "duration_days": m.duration_days,
                "special_instructions": m.special_instructions
            }
            for m in current_medicines
        ]
    }
    
    history = PrescriptionHistory(
        prescription_id=prescription.id,
        version=prescription.version,
        prescription_data=history_data,
        modified_by=current_user.id
    )
    db.add(history)
    
    # Update prescription
    if prescription_data.notes is not None:
        prescription.notes = prescription_data.notes
    if prescription_data.special_instructions is not None:
        prescription.special_instructions = prescription_data.special_instructions
    
    prescription.version += 1
    
    # Update medicines if provided
    if prescription_data.medicines is not None:
        # Delete existing medicines
        for medicine in current_medicines:
            await db.delete(medicine)
        
        # Add new medicines
        for medicine_data in prescription_data.medicines:
            medicine = PrescriptionMedicine(
                prescription_id=prescription.id,
                medicine_name=medicine_data.medicine_name,
                dosage=medicine_data.dosage,
                usage=medicine_data.usage,
                frequency=medicine_data.frequency,
                duration_days=medicine_data.duration_days,
                special_instructions=medicine_data.special_instructions
            )
            db.add(medicine)
    
    await db.commit()
    await db.refresh(prescription)
    
    # Load medicines
    result = await db.execute(
        select(PrescriptionMedicine).where(PrescriptionMedicine.prescription_id == prescription.id)
    )
    prescription.medicines = result.scalars().all()
    
    return prescription


@router.get("/{prescription_id}/history")
async def get_prescription_history(
    prescription_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get prescription version history."""
    result = await db.execute(
        select(PrescriptionHistory).where(
            PrescriptionHistory.prescription_id == prescription_id
        ).order_by(PrescriptionHistory.version.desc())
    )
    history = result.scalars().all()
    
    return [
        {
            "version": h.version,
            "modified_at": h.modified_at,
            "modified_by": h.modified_by,
            "data": h.prescription_data
        }
        for h in history
    ]
