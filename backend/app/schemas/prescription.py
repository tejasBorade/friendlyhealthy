from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from uuid import UUID


class MedicineBase(BaseModel):
    medicine_name: str = Field(..., min_length=1, max_length=200)
    dosage: str = Field(..., min_length=1, max_length=100)
    usage: Optional[str] = Field(None, max_length=50)
    frequency: str = Field(..., min_length=1, max_length=50)
    duration_days: int = Field(..., gt=0)
    special_instructions: Optional[str] = None


class PrescriptionCreate(BaseModel):
    consultation_id: UUID
    notes: Optional[str] = None
    special_instructions: Optional[str] = None
    medicines: List[MedicineBase]


class PrescriptionUpdate(BaseModel):
    notes: Optional[str] = None
    special_instructions: Optional[str] = None
    medicines: Optional[List[MedicineBase]] = None


class MedicineResponse(MedicineBase):
    id: UUID
    prescription_id: UUID
    
    class Config:
        from_attributes = True


class PrescriptionResponse(BaseModel):
    id: UUID
    prescription_number: str
    consultation_id: UUID
    patient_id: UUID
    doctor_id: UUID
    prescription_date: date
    notes: Optional[str]
    special_instructions: Optional[str]
    version: int
    medicines: List[MedicineResponse] = []
    
    class Config:
        from_attributes = True


class ConsultationCreate(BaseModel):
    appointment_id: UUID
    chief_complaint: Optional[str] = None
    diagnosis: str = Field(..., min_length=1)
    consultation_notes: Optional[str] = None
    follow_up_required: bool = False
    follow_up_after_days: Optional[int] = None


class ConsultationResponse(BaseModel):
    id: UUID
    appointment_id: UUID
    patient_id: UUID
    doctor_id: UUID
    chief_complaint: Optional[str]
    diagnosis: str
    consultation_notes: Optional[str]
    follow_up_required: bool
    follow_up_after_days: Optional[int]
    
    class Config:
        from_attributes = True
