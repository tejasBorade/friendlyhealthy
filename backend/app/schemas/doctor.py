from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from uuid import UUID


class DoctorBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    gender: str
    phone: str = Field(..., min_length=10, max_length=20)
    registration_number: str
    qualification: str
    experience_years: int = Field(..., ge=0)
    consultation_fee: Decimal = Field(..., ge=0)
    about: Optional[str] = None


class DoctorCreate(DoctorBase):
    specialization_ids: List[UUID]
    clinic_name: str
    clinic_address: str
    clinic_city: str
    clinic_state: str


class DoctorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[Decimal] = None
    about: Optional[str] = None


class SpecializationResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    icon: Optional[str]
    
    class Config:
        from_attributes = True


class DoctorResponse(DoctorBase):
    id: UUID
    user_id: UUID
    is_verified: bool
    rating: Decimal
    total_reviews: int
    specializations: List[str] = []
    
    class Config:
        from_attributes = True
