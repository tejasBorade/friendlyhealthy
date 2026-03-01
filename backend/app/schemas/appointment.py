from pydantic import BaseModel
from typing import Optional
from datetime import date, time


class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_id: Optional[int] = None  # For admin/doctor creating appointments for patients
    appointment_date: date
    appointment_time: time
    reason: Optional[str] = None


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    reason: Optional[str] = None
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    status: str
    reason: Optional[str]
    notes: Optional[str]
    
    class Config:
        from_attributes = True


class AppointmentStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
