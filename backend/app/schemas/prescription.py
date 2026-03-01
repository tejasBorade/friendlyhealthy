from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class PrescriptionBase(BaseModel):
    patient_id: int
    doctor_id: int
    medical_record_id: Optional[int] = None
    medication_name: str = Field(..., min_length=1, max_length=255)
    dosage: str = Field(..., min_length=1, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=100)
    duration: str = Field(..., min_length=1, max_length=100)
    instructions: Optional[str] = None


class PrescriptionCreate(PrescriptionBase):
    prescribed_date: Optional[date] = None


class PrescriptionUpdate(BaseModel):
    medication_name: Optional[str] = Field(None, max_length=255)
    dosage: Optional[str] = Field(None, max_length=100)
    frequency: Optional[str] = Field(None, max_length=100)
    duration: Optional[str] = Field(None, max_length=100)
    instructions: Optional[str] = None


class PrescriptionResponse(PrescriptionBase):
    id: int
    prescribed_date: Optional[date]
    created_at: datetime
    # Add fields the frontend expects
    diagnosis: Optional[str] = None  # Map to medication_name
    appointment_date: Optional[date] = None  # Map to prescribed_date  
    notes: Optional[str] = None  # Map to instructions
    
    @classmethod
    def from_model(cls, prescription):
        """Map Prescription model to response with frontend-expected fields."""
        return cls(
            id=prescription.id,
            patient_id=prescription.patient_id,
            doctor_id=prescription.doctor_id,
            medical_record_id=prescription.medical_record_id,
            medication_name=prescription.medication_name,
            dosage=prescription.dosage,
            frequency=prescription.frequency,
            duration=prescription.duration,
            instructions=prescription.instructions,
            prescribed_date=prescription.prescribed_date,
            created_at=prescription.created_at,
            # Map to frontend fields
            diagnosis=prescription.medication_name,
            appointment_date=prescription.prescribed_date,
            notes=prescription.instructions
        )
    
    class Config:
        from_attributes = True


class MedicalRecordBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    diagnosis: str = Field(..., min_length=1)
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    visit_date: date


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecordUpdate(BaseModel):
    diagnosis: Optional[str] = Field(None, min_length=1)
    symptoms: Optional[str] = None
    treatment: Optional[str] = None


class MedicalRecordResponse(MedicalRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

    
    class Config:
        from_attributes = True

