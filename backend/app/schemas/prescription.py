from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
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
    patient_instructions: Optional[str] = None
    follow_up_date: Optional[date] = None
    diagnosis_icd10_code: Optional[str] = Field(None, max_length=20)
    diagnosis_patient_friendly: Optional[str] = None
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
    patient_instructions: Optional[str]
    follow_up_date: Optional[date]
    diagnosis_icd10_code: Optional[str]
    diagnosis_patient_friendly: Optional[str]
    is_signed: bool
    signed_at: Optional[datetime]
    pdf_path: Optional[str]
    is_locked: bool
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


# ================================
# Sprint 1.1: Prescription Enhancements
# ================================

class PrescriptionSignRequest(BaseModel):
    """Request to sign a prescription with PIN."""
    signature_pin: str = Field(..., min_length=4, max_length=6, description="Signature PIN")


class PrescriptionSignResponse(BaseModel):
    """Response after signing prescription."""
    success: bool
    message: str
    prescription_id: UUID
    signed_at: datetime
    pdf_path: Optional[str] = None


class PrescriptionSearchQuery(BaseModel):
    """Search filters for prescriptions."""
    patient_id: Optional[UUID] = None
    doctor_id: Optional[UUID] = None
    medicine_name: Optional[str] = None
    diagnosis: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    is_signed: Optional[bool] = None


class PrescriptionListResponse(BaseModel):
    """Paginated list of prescriptions."""
    prescriptions: List[PrescriptionResponse]
    total: int
    page: int
    page_size: int


class ActivePrescriptionResponse(BaseModel):
    """Active prescription with remaining medicine info."""
    id: UUID
    prescription_number: str
    doctor_id: UUID
    doctor_name: str
    prescription_date: date
    follow_up_date: Optional[date]
    medicines: List[MedicineResponse]
    days_remaining: int  # Days until medicines run out
    
    class Config:
        from_attributes = True

