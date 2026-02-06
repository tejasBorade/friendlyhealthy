from pydantic import BaseModel
from typing import Optional
from datetime import date
from uuid import UUID
from app.models.report import ReportType


class ReportCreate(BaseModel):
    patient_id: UUID
    report_type: ReportType
    report_name: str
    test_date: date
    lab_name: Optional[str] = None
    lab_address: Optional[str] = None
    doctor_remarks: Optional[str] = None


class ReportUpdate(BaseModel):
    report_name: Optional[str] = None
    lab_name: Optional[str] = None
    lab_address: Optional[str] = None
    doctor_remarks: Optional[str] = None


class ReportResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: Optional[UUID]
    report_type: ReportType
    report_name: str
    test_date: date
    lab_name: Optional[str]
    lab_address: Optional[str]
    report_file_path: str
    doctor_remarks: Optional[str]
    
    class Config:
        from_attributes = True
