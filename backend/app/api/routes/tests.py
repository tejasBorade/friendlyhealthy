"""
API Routes for Test Orders
Sprint 1.4: Tests Ordered Tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.medical import Prescription
from app.models.prescription_extras import TestOrdered, TestOrderStatus
from app.schemas.test_order import (
    TestOrderCreate,
    TestOrderUpdate,
    TestOrderStatusUpdate,
    TestOrderResponse,
    TestOrderWithPrescription,
    TestOrderListResponse,
    PendingTestsSummary
)
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/tests", tags=["Test Orders"])


@router.post("/prescriptions/{prescription_id}/tests", response_model=TestOrderResponse, status_code=status.HTTP_201_CREATED)
async def add_test_to_prescription(
    prescription_id: UUID,
    test_data: TestOrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a test order to a prescription (Doctor only).
    
    Tests can be added to prescriptions to track which investigations are ordered.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can order tests"
        )
    
    # Get prescription and verify ownership
    result = await db.execute(
        select(Prescription).where(Prescription.id == prescription_id)
    )
    prescription = result.scalar_one_or_none()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    # Get doctor and verify
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor or prescription.doctor_id != doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot add tests to this prescription"
        )
    
    # Create test order
    test = TestOrdered(
        prescription_id=prescription_id,
        test_name=test_data.test_name,
        test_type=test_data.test_type,
        notes=test_data.notes,
        due_date=test_data.due_date,
        status=TestOrderStatus.ORDERED
    )
    
    db.add(test)
    await db.commit()
    await db.refresh(test)
    
    return test


@router.get("/prescriptions/{prescription_id}/tests", response_model=List[TestOrderResponse])
async def get_prescription_tests(
    prescription_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tests ordered in a prescription.
    
    Accessible by both doctor and patient of the prescription.
    """
    # Get prescription
    result = await db.execute(
        select(Prescription).where(Prescription.id == prescription_id)
    )
    prescription = result.scalar_one_or_none()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    # Verify access
    if current_user.role == UserRole.DOCTOR:
        result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        doctor = result.scalar_one_or_none()
        if not doctor or prescription.doctor_id != doctor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view tests for this prescription"
            )
    elif current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient or prescription.patient_id != patient.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view tests for this prescription"
            )
    
    # Get tests
    query = (
        select(TestOrdered)
        .where(TestOrdered.prescription_id == prescription_id)
        .order_by(TestOrdered.created_at.desc())
    )
    
    result = await db.execute(query)
    tests = result.scalars().all()
    
    return tests


@router.put("/tests/{test_id}", response_model=TestOrderResponse)
async def update_test_order(
    test_id: UUID,
    test_data: TestOrderUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update test order details (Doctor only).
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update test orders"
        )
    
    # Get test order
    result = await db.execute(
        select(TestOrdered).where(TestOrdered.id == test_id)
    )
    test = result.scalar_one_or_none()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test order not found"
        )
    
    # Get prescription and verify ownership
    result = await db.execute(
        select(Prescription).where(Prescription.id == test.prescription_id)
    )
    prescription = result.scalar_one_or_none()
    
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor or prescription.doctor_id != doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update this test order"
        )
    
    # Update fields
    if test_data.test_name is not None:
        test.test_name = test_data.test_name
    if test_data.test_type is not None:
        test.test_type = test_data.test_type
    if test_data.notes is not None:
        test.notes = test_data.notes
    if test_data.due_date is not None:
        test.due_date = test_data.due_date
    if test_data.status is not None:
        test.status = test_data.status
    
    await db.commit()
    await db.refresh(test)
    
    return test


@router.patch("/tests/{test_id}/status", response_model=TestOrderResponse)
async def update_test_status(
    test_id: UUID,
    status_data: TestOrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update test status (Patient can mark as uploaded, Doctor can mark any).
    
    When status is 'uploaded', link the report_id.
    """
    # Get test order
    result = await db.execute(
        select(TestOrdered).where(TestOrdered.id == test_id)
    )
    test = result.scalar_one_or_none()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test order not found"
        )
    
    # Get prescription
    result = await db.execute(
        select(Prescription).where(Prescription.id == test.prescription_id)
    )
    prescription = result.scalar_one_or_none()
    
    # Verify access
    if current_user.role == UserRole.DOCTOR:
        result = await db.execute(
            select(Doctor).where(Doctor.user_id == current_user.id)
        )
        doctor = result.scalar_one_or_none()
        if not doctor or prescription.doctor_id != doctor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update this test"
            )
    elif current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient or prescription.patient_id != patient.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update this test"
            )
        
        # Patients can only mark as uploaded
        if status_data.status != TestOrderStatus.UPLOADED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patients can only mark tests as uploaded"
            )
    
    # Update status
    test.status = status_data.status
    if status_data.report_id:
        test.report_id = status_data.report_id
    
    await db.commit()
    await db.refresh(test)
    
    return test


@router.get("/pending", response_model=PendingTestsSummary)
async def get_pending_tests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all pending tests for current patient.
    
    Returns tests with status 'ordered' that haven't been completed.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can view pending tests"
        )
    
    # Get patient
    result = await db.execute(
        select(Patient).where(Patient.user_id == current_user.id)
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    
    # Get pending tests
    query = (
        select(TestOrdered, Prescription, Doctor, User)
        .join(Prescription, TestOrdered.prescription_id == Prescription.id)
        .join(Doctor, Prescription.doctor_id == Doctor.id)
        .join(User, Doctor.user_id == User.id)
        .where(
            and_(
                Prescription.patient_id == patient.id,
                TestOrdered.status == TestOrderStatus.ORDERED
            )
        )
        .order_by(TestOrdered.due_date.asc().nullslast(), TestOrdered.created_at.desc())
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    today = date.today()
    overdue_count = 0
    upcoming_count = 0
    tests_with_details = []
    
    for test, prescription, doctor, doctor_user in rows:
        # Count overdue and upcoming
        if test.due_date:
            if test.due_date < today:
                overdue_count += 1
            else:
                upcoming_count += 1
        
        # Build response
        test_detail = TestOrderWithPrescription(
            id=test.id,
            prescription_id=test.prescription_id,
            test_name=test.test_name,
            test_type=test.test_type,
            notes=test.notes,
            due_date=test.due_date,
            status=test.status,
            report_id=test.report_id,
            created_at=test.created_at,
            updated_at=test.updated_at,
            patient_name=f"{current_user.first_name} {current_user.last_name}",
            doctor_name=f"Dr. {doctor_user.first_name} {doctor_user.last_name}",
            prescribed_date=prescription.created_at,
            diagnosis=prescription.diagnosis
        )
        tests_with_details.append(test_detail)
    
    return PendingTestsSummary(
        total_pending=len(tests_with_details),
        overdue=overdue_count,
        upcoming=upcoming_count,
        tests=tests_with_details
    )


@router.delete("/tests/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_order(
    test_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a test order (Doctor only).
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can delete test orders"
        )
    
    # Get test order
    result = await db.execute(
        select(TestOrdered).where(TestOrdered.id == test_id)
    )
    test = result.scalar_one_or_none()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test order not found"
        )
    
    # Get prescription and verify ownership
    result = await db.execute(
        select(Prescription).where(Prescription.id == test.prescription_id)
    )
    prescription = result.scalar_one_or_none()
    
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == current_user.id)
    )
    doctor = result.scalar_one_or_none()
    if not doctor or prescription.doctor_id != doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete this test order"
        )
    
    await db.delete(test)
    await db.commit()
    
    return None
