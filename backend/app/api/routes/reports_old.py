from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID, uuid4
from pathlib import Path
import os
import shutil
from app.core.database import get_db
from app.core.config import settings
from app.models.report import MedicalReport, ReportType
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.report import ReportResponse, ReportUpdate
from app.api.dependencies import get_current_user
from datetime import date

router = APIRouter(prefix="/reports", tags=["Medical Reports"])


# Ensure upload directory exists
UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "reports"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return os.path.splitext(filename)[1].lower()


def validate_file_type(filename: str) -> bool:
    """Validate file type is allowed."""
    extension = get_file_extension(filename).lstrip('.')
    return extension in settings.ALLOWED_FILE_TYPES


def validate_file_size(file_size: int) -> bool:
    """Validate file size is within limit."""
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes
    return file_size <= max_size


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def upload_report(
    patient_id: UUID = Form(...),
    report_type: ReportType = Form(...),
    report_name: str = Form(...),
    test_date: date = Form(...),
    lab_name: Optional[str] = Form(None),
    lab_address: Optional[str] = Form(None),
    doctor_remarks: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload medical report."""
    # Validate file type
    if not validate_file_type(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}"
        )
    
    # Read file content to check size
    file_content = await file.read()
    if not validate_file_size(len(file_content)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    # Verify patient access
    if current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient or patient.id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Verify patient exists
    result = await db.execute(
        select(Patient).where(Patient.id == patient_id)
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Generate unique filename
    file_extension = get_file_extension(file.filename)
    unique_filename = f"{uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
    
    # Get doctor ID if doctor is uploading
    doctor_id = None
    if current_user.role == UserRole.DOCTOR:
        result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        doctor = result.scalar_one_or_none()
        if doctor:
            doctor_id = doctor.id
    
    # Create report record
    report = MedicalReport(
        patient_id=patient_id,
        doctor_id=doctor_id,
        report_type=report_type,
        report_name=report_name,
        test_date=test_date,
        lab_name=lab_name,
        lab_address=lab_address,
        report_file_path=str(file_path),
        doctor_remarks=doctor_remarks,
        uploaded_by=current_user.id
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    return report


@router.get("", response_model=List[ReportResponse])
async def get_reports(
    patient_id: Optional[UUID] = None,
    report_type: Optional[ReportType] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get medical reports."""
    query = select(MedicalReport).where(MedicalReport.is_deleted == False)
    
    # Filter based on user role
    if current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if patient:
            query = query.where(MedicalReport.patient_id == patient.id)
        else:
            return []
    elif patient_id:
        # Doctors and admins can filter by patient_id
        query = query.where(MedicalReport.patient_id == patient_id)
    
    if report_type:
        query = query.where(MedicalReport.report_type == report_type)
    
    query = query.order_by(MedicalReport.test_date.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return reports


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get report details."""
    result = await db.execute(
        select(MedicalReport).where(
            MedicalReport.id == report_id,
            MedicalReport.is_deleted == False
        )
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report


@router.get("/{report_id}/download")
async def download_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download medical report file."""
    result = await db.execute(
        select(MedicalReport).where(
            MedicalReport.id == report_id,
            MedicalReport.is_deleted == False
        )
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Verify access
    if current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient or patient.id != report.patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Check if file exists
    file_path = Path(report.report_file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found"
        )
    
    return FileResponse(
        path=file_path,
        filename=f"{report.report_name}{get_file_extension(str(file_path))}",
        media_type="application/octet-stream"
    )


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: UUID,
    report_data: ReportUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update report details (not the file)."""
    result = await db.execute(
        select(MedicalReport).where(
            MedicalReport.id == report_id,
            MedicalReport.is_deleted == False
        )
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Update fields
    update_data = report_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    
    await db.commit()
    await db.refresh(report)
    
    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete report."""
    result = await db.execute(
        select(MedicalReport).where(MedicalReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Verify access
    if current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient or patient.id != report.patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    report.is_deleted = True
    await db.commit()
    
    return None
