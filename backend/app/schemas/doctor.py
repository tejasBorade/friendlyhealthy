from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime


class DoctorBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    specialization: str = Field(..., max_length=100)
    qualification: str | None = Field(None, max_length=255)
    experience_years: int | None = Field(None, ge=0)
    phone: str | None = Field(None, max_length=20)
    consultation_fee: Decimal | None = Field(None, ge=0)
    available_days: str | None = Field(None, max_length=255)
    available_hours: str | None = Field(None, max_length=100)


class DoctorCreate(DoctorBase):
    user_id: int


class DoctorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    specialization: Optional[str] = None
    phone: Optional[str] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[Decimal] = None
    available_days: Optional[str] = None
    available_hours: Optional[str] = None


class DoctorResponse(DoctorBase):
    id: int
    user_id: int
    is_available: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
