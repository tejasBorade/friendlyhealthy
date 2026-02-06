from pydantic import BaseModel
from typing import Optional
from datetime import date, time
from uuid import UUID
from app.models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    doctor_id: UUID
    appointment_date: date
    appointment_time: time
    reason_for_visit: Optional[str] = None
    symptoms: Optional[str] = None


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    reason_for_visit: Optional[str] = None
    symptoms: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: UUID
    appointment_number: str
    patient_id: UUID
    doctor_id: UUID
    appointment_date: date
    appointment_time: time
    duration: int
    status: AppointmentStatus
    reason_for_visit: Optional[str]
    symptoms: Optional[str]
    doctor_notes: Optional[str]
    
    class Config:
        from_attributes = True


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
