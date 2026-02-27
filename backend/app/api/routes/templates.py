"""
API Routes for Prescription Templates
Sprint 1.2: Templates & Favorites
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.doctor import Doctor
from app.models.prescription_extras import PrescriptionTemplate
from app.schemas.template import (
    PrescriptionTemplateCreate,
    PrescriptionTemplateUpdate,
    PrescriptionTemplateResponse,
    PrescriptionTemplateListResponse,
    PrescriptionFromTemplateRequest
)
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/templates", tags=["Prescription Templates"])


@router.post("", response_model=PrescriptionTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: PrescriptionTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new prescription template (Doctor only).
    
    Templates allow doctors to quickly create prescriptions for common diagnoses.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create templates"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Convert medicines and tests to JSONB format
    medicines_json = [med.model_dump() for med in template_data.medicines]
    tests_json = [test.model_dump() for test in template_data.tests] if template_data.tests else []
    
    # Create template
    template = PrescriptionTemplate(
        doctor_id=doctor.id,
        template_name=template_data.template_name,
        diagnosis=template_data.diagnosis,
        diagnosis_icd10_code=template_data.diagnosis_icd10_code,
        medicines=medicines_json,
        tests=tests_json,
        instructions=template_data.instructions,
        follow_up_days=template_data.follow_up_days,
        is_active=True,
        usage_count=0
    )
    
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return template


@router.get("", response_model=PrescriptionTemplateListResponse)
async def get_templates(
    search: Optional[str] = Query(None, description="Search by template name or diagnosis"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all templates for the current doctor.
    
    Supports search and pagination.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view templates"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Build query
    query = select(PrescriptionTemplate).where(
        PrescriptionTemplate.doctor_id == doctor.id
    )
    
    # Apply filters
    if search:
        query = query.where(
            or_(
                PrescriptionTemplate.template_name.ilike(f"%{search}%"),
                PrescriptionTemplate.diagnosis.ilike(f"%{search}%")
            )
        )
    
    if is_active is not None:
        query = query.where(PrescriptionTemplate.is_active == is_active)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(PrescriptionTemplate.usage_count.desc(), PrescriptionTemplate.template_name)
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    templates = result.scalars().all()
    
    return PrescriptionTemplateListResponse(
        templates=templates,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{template_id}", response_model=PrescriptionTemplateResponse)
async def get_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific template by ID."""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view templates"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Get template
    result = await db.execute(
        select(PrescriptionTemplate).where(
            PrescriptionTemplate.id == template_id,
            PrescriptionTemplate.doctor_id == doctor.id
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return template


@router.put("/{template_id}", response_model=PrescriptionTemplateResponse)
async def update_template(
    template_id: UUID,
    template_data: PrescriptionTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a template."""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update templates"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Get template
    result = await db.execute(
        select(PrescriptionTemplate).where(
            PrescriptionTemplate.id == template_id,
            PrescriptionTemplate.doctor_id == doctor.id
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Update fields
    if template_data.template_name is not None:
        template.template_name = template_data.template_name
    if template_data.diagnosis is not None:
        template.diagnosis = template_data.diagnosis
    if template_data.diagnosis_icd10_code is not None:
        template.diagnosis_icd10_code = template_data.diagnosis_icd10_code
    if template_data.medicines is not None:
        template.medicines = [med.model_dump() for med in template_data.medicines]
    if template_data.tests is not None:
        template.tests = [test.model_dump() for test in template_data.tests]
    if template_data.instructions is not None:
        template.instructions = template_data.instructions
    if template_data.follow_up_days is not None:
        template.follow_up_days = template_data.follow_up_days
    if template_data.is_active is not None:
        template.is_active = template_data.is_active
    
    await db.commit()
    await db.refresh(template)
    
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a template."""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can delete templates"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Get template
    result = await db.execute(
        select(PrescriptionTemplate).where(
            PrescriptionTemplate.id == template_id,
            PrescriptionTemplate.doctor_id == doctor.id
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    await db.delete(template)
    await db.commit()
    
    return None


@router.post("/{template_id}/use")
async def use_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Increment usage count for a template.
    
    Called when a prescription is created from this template.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can use templates"
        )
    
    # Get doctor
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Get template
    result = await db.execute(
        select(PrescriptionTemplate).where(
            PrescriptionTemplate.id == template_id,
            PrescriptionTemplate.doctor_id == doctor.id
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    template.usage_count += 1
    await db.commit()
    
    return {"success": True, "usage_count": template.usage_count}
