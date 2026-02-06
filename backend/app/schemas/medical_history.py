from pydantic import BaseModel
from typing import Optional
from datetime import date
from uuid import UUID


class MedicalHistoryCreate(BaseModel):
    patient_id: UUID
    appointment_id: Optional[UUID] = None
    recorded_date: date
    past_illnesses: Optional[str] = None
    allergies: Optional[str] = None
    chronic_diseases: Optional[str] = None
    surgeries: Optional[str] = None
    family_medical_history: Optional[str] = None
    current_medications: Optional[str] = None
    notes: Optional[str] = None


class MedicalHistoryUpdate(BaseModel):
    past_illnesses: Optional[str] = None
    allergies: Optional[str] = None
    chronic_diseases: Optional[str] = None
    surgeries: Optional[str] = None
    family_medical_history: Optional[str] = None
    current_medications: Optional[str] = None
    notes: Optional[str] = None


class MedicalHistoryResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    appointment_id: Optional[UUID]
    recorded_date: date
    past_illnesses: Optional[str]
    allergies: Optional[str]
    chronic_diseases: Optional[str]
    surgeries: Optional[str]
    family_medical_history: Optional[str]
    current_medications: Optional[str]
    notes: Optional[str]
    version: int
    
    class Config:
        from_attributes = True
