"""
Test Order Schemas
Sprint 1.4: Tests Ordered Tracking
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from enum import Enum


class TestOrderStatus(str, Enum):
    """Test order status enum."""
    ORDERED = "ordered"
    UPLOADED = "uploaded"
    MISSING = "missing"


class TestOrderBase(BaseModel):
    """Base test order schema."""
    test_name: str = Field(..., max_length=200, description="Name of the test")
    test_type: Optional[str] = Field(None, max_length=100, description="Type of test (blood_test, xray, mri, etc.)")
    notes: Optional[str] = Field(None, description="Additional notes or instructions")
    due_date: Optional[date] = Field(None, description="When test should be completed by")


class TestOrderCreate(TestOrderBase):
    """Schema for creating test order."""
    pass


class TestOrderUpdate(BaseModel):
    """Schema for updating test order."""
    test_name: Optional[str] = Field(None, max_length=200)
    test_type: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[TestOrderStatus] = None


class TestOrderStatusUpdate(BaseModel):
    """Schema for updating only test status."""
    status: TestOrderStatus = Field(..., description="New status")
    report_id: Optional[UUID] = Field(None, description="Link to uploaded report (for 'uploaded' status)")


class TestOrderResponse(TestOrderBase):
    """Test order response schema."""
    id: UUID
    prescription_id: UUID
    status: TestOrderStatus
    report_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TestOrderWithPrescription(TestOrderResponse):
    """Test order with prescription details."""
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    prescribed_date: Optional[datetime] = None
    diagnosis: Optional[str] = None


class TestOrderListResponse(BaseModel):
    """Paginated list of test orders."""
    tests: List[TestOrderResponse]
    total: int
    page: int
    page_size: int


class PendingTestsSummary(BaseModel):
    """Summary of pending tests for a patient."""
    total_pending: int
    overdue: int
    upcoming: int
    tests: List[TestOrderWithPrescription]
