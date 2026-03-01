from fastapi import APIRouter, Depends, status, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.medical import MedicalRecord
from app.models.doctor import Doctor
from pydantic import BaseModel, Field


router = APIRouter()


class MedicalRecordCreate(BaseModel):
    """Schema for creating a medical record from frontend."""
    patientId: int = Field(..., alias="patientId")
    appointmentId: Optional[int] = Field(None, alias="appointmentId")
    recordType: Optional[str] = Field(None, alias="recordType")
    title: Optional[str] = None
    description: Optional[str] = None
    resultSummary: Optional[str] = Field(None, alias="resultSummary")
    testDate: Optional[date] = Field(None, alias="testDate")
    
    class Config:
        populate_by_name = True


class MedicalRecordResponse(BaseModel):
    """Response schema mapping backend fields to frontend expectations."""
    id: int
    patient_id: int
    doctor_id: int
    appointment_id: int | None = None
    record_type: str = "Clinical Note"
    title: str
    description: str | None = None
    test_date: date
    result_summary: str | None = None
    created_at: Optional[str] = None
    
    @classmethod
    def from_model(cls, record: MedicalRecord):
        """Map MedicalRecord model to response format."""
        # Map diagnosis -> title
        # Map visit_date -> test_date
        # Map symptoms + treatment  -> description
        description = ""
        if record.symptoms:
            description += f"Symptoms: {record.symptoms}\n"
        if record.treatment:
            description += f"Treatment: {record.treatment}"
        
        return cls(
            id=record.id,
            patient_id=record.patient_id,
            doctor_id=record.doctor_id,
            appointment_id=record.appointment_id,
            title=record.diagnosis,
            test_date=record.visit_date,
            description=description.strip() if description.strip() else None,
            result_summary=record.treatment,  # Use treatment as result_summary
            record_type="Clinical Note"
        )
    
    class Config:
        from_attributes = True


class MedicalRecordsListResponse(BaseModel):
    records: List[MedicalRecordResponse]  # Changed from medical_records to records


@router.get("", response_model=MedicalRecordsListResponse)
async def get_medical_records(
    patient_id: Optional[int] = Query(None, alias="patientId"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get medical records for a patient."""
    # If patient_id is provided
    if patient_id:
        # Patients can only view their own records
        if current_user.role == UserRole.PATIENT:
            # Verify this user owns this patient record
            from app.models.patient import Patient
            result = await db.execute(
                select(Patient).where(Patient.user_id == current_user.id)
            )
            patient = result.scalar_one_or_none()
            if not patient or patient.id != patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view these records"
                )
        # Admins and doctors can view any records
        elif current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view medical records"
            )
        
        # Get medical records for this patient
        result = await db.execute(
            select(MedicalRecord)
            .where(MedicalRecord.patient_id == patient_id)
            .order_by(MedicalRecord.visit_date.desc())
        )
        records = result.scalars().all()
    else:
        # No patient_id provided - only for admin/doctor to view all
        if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view all medical records"
            )
        
        result = await db.execute(
            select(MedicalRecord).order_by(MedicalRecord.visit_date.desc())
        )
        records = result.scalars().all()
    
    return MedicalRecordsListResponse(
        records=[MedicalRecordResponse.from_model(r) for r in records]
    )


@router.get("/{record_id}", response_model=MedicalRecordResponse)
async def get_medical_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single medical record by ID."""
    # Get the record
    result = await db.execute(
        select(MedicalRecord).where(MedicalRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )
    
    # Verify access
    if current_user.role == UserRole.PATIENT:
        # Verify this user owns this patient record
        from app.models.patient import Patient
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient or patient.id != record.patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this record"
            )
    elif current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view medical records"
        )
    
    return MedicalRecordResponse.from_model(record)


@router.post("", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    record_data: MedicalRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new medical record (Doctor only)."""
    if current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create medical records"
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
    
    # Parse the frontend data into backend format
    # The description field contains symptoms and treatment in format:
    # "Symptoms: ...
# Treatment: ..."
    symptoms = None
    treatment = None
    if record_data.description:
        lines = record_data.description.split('\n')
        for line in lines:
            if line.startswith('Symptoms:'):
                symptoms = line.replace('Symptoms:', '').strip()
            elif line.startswith('Treatment:'):
                treatment = line.replace('Treatment:', '').strip()
    
    # Use title as diagnosis or use recordType as fallback
    diagnosis = record_data.title or record_data.recordType or "General Record"
    
    # Create medical record
    new_record = MedicalRecord(
        patient_id=record_data.patientId,
        doctor_id=doctor.id,
        appointment_id=record_data.appointmentId,
        diagnosis=diagnosis,
        symptoms=symptoms,
        treatment=treatment,
        visit_date=record_data.testDate or date.today()
    )
    
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    
    return MedicalRecordResponse.from_model(new_record)
