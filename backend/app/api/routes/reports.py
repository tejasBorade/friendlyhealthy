from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel, Field
from datetime import date, datetime
from app.core.database import get_db
from app.models.report import Report
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])


class ReportBase(BaseModel):
    patient_id: int
    doctor_id: int | None = None
    report_type: str = Field(..., max_length=100)
    report_date: date
    findings: str | None = None
    file_url: str | None = Field(None, max_length=500)
    test_name: str | None = Field(None, max_length=200)


class ReportCreate(ReportBase):
    pass


class ReportResponse(ReportBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[ReportResponse])
async def get_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get reports for current user."""
    query = select(Report)
    
    if current_user.role == UserRole.PATIENT:
        # Get patient reports
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient:
            return []
        query = query.where(Report.patient_id == patient.id)
    
    elif current_user.role == UserRole.DOCTOR:
        # Get doctor's reports
        result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        doctor = result.scalar_one_or_none()
        if not doctor:
            return []
        query = query.where(Report.doctor_id == doctor.id)
    
    elif current_user.role in [UserRole.ADMIN, UserRole.STAFF]:
        # Admins and staff can see all
        pass
    else:
        return []
    
    result = await db.execute(query.order_by(Report.report_date.desc()))
    reports = result.scalars().all()
    return reports


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new report."""
    if current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN, UserRole.STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    report = Report(**report_data.model_dump())
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report
