"""
Schemas for Prescription Templates and Medicine Favorites
Sprint 1.2: Templates & Favorites
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ================================
# Medicine Favorites Schemas
# ================================

class MedicineFavoriteBase(BaseModel):
    """Base schema for medicine favorite."""
    medicine_name: str = Field(..., min_length=1, max_length=200)
    dosage: Optional[str] = Field(None, max_length=100)
    frequency: Optional[str] = Field(None, max_length=50, description="e.g., 1-0-1")
    usage_instructions: Optional[str] = Field(None, description="e.g., after food")
    duration_days: Optional[int] = Field(None, ge=1, le=365)
    category: Optional[str] = Field(None, max_length=100, description="e.g., Antibiotics")


class MedicineFavoriteCreate(MedicineFavoriteBase):
    """Schema for creating a medicine favorite."""
    pass


class MedicineFavoriteUpdate(BaseModel):
    """Schema for updating a medicine favorite."""
    medicine_name: Optional[str] = Field(None, min_length=1, max_length=200)
    dosage: Optional[str] = Field(None, max_length=100)
    frequency: Optional[str] = Field(None, max_length=50)
    usage_instructions: Optional[str] = None
    duration_days: Optional[int] = Field(None, ge=1, le=365)
    category: Optional[str] = Field(None, max_length=100)


class MedicineFavoriteResponse(MedicineFavoriteBase):
    """Schema for medicine favorite response."""
    id: UUID
    doctor_id: UUID
    usage_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MedicineFavoriteListResponse(BaseModel):
    """Paginated list of medicine favorites."""
    favorites: List[MedicineFavoriteResponse]
    total: int
    page: int
    page_size: int


# ================================
# Prescription Template Schemas
# ================================

class TemplateMedicine(BaseModel):
    """Medicine in a template."""
    medicine_name: str = Field(..., min_length=1, max_length=200)
    dosage: str = Field(..., min_length=1, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=50)
    duration_days: int = Field(..., ge=1, le=365)
    instructions: Optional[str] = None


class TemplateTest(BaseModel):
    """Test in a template."""
    test_name: str = Field(..., min_length=1, max_length=200)
    test_type: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class PrescriptionTemplateBase(BaseModel):
    """Base schema for prescription template."""
    template_name: str = Field(..., min_length=1, max_length=200)
    diagnosis: str = Field(..., min_length=1)
    diagnosis_icd10_code: Optional[str] = Field(None, max_length=20)
    medicines: List[TemplateMedicine] = Field(..., min_items=1)
    tests: Optional[List[TemplateTest]] = Field(default=[])
    instructions: Optional[str] = None
    follow_up_days: Optional[int] = Field(None, ge=1, le=365)


class PrescriptionTemplateCreate(PrescriptionTemplateBase):
    """Schema for creating a prescription template."""
    pass


class PrescriptionTemplateUpdate(BaseModel):
    """Schema for updating a prescription template."""
    template_name: Optional[str] = Field(None, min_length=1, max_length=200)
    diagnosis: Optional[str] = Field(None, min_length=1)
    diagnosis_icd10_code: Optional[str] = Field(None, max_length=20)
    medicines: Optional[List[TemplateMedicine]] = Field(None, min_items=1)
    tests: Optional[List[TemplateTest]] = None
    instructions: Optional[str] = None
    follow_up_days: Optional[int] = Field(None, ge=1, le=365)
    is_active: Optional[bool] = None


class PrescriptionTemplateResponse(PrescriptionTemplateBase):
    """Schema for prescription template response."""
    id: UUID
    doctor_id: UUID
    usage_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PrescriptionTemplateListResponse(BaseModel):
    """Paginated list of prescription templates."""
    templates: List[PrescriptionTemplateResponse]
    total: int
    page: int
    page_size: int


class PrescriptionFromTemplateRequest(BaseModel):
    """Request to create prescription from template."""
    template_id: UUID
    consultation_id: UUID
    customize_medicines: Optional[List[TemplateMedicine]] = None
    customize_tests: Optional[List[TemplateTest]] = None
    customize_instructions: Optional[str] = None
    customize_follow_up_days: Optional[int] = Field(None, ge=1, le=365)
