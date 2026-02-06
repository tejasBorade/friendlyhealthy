from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from app.core.database import get_db
from app.core.config import settings
from app.models.billing import Bill, BillItem, ChargeType, PaymentStatus
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.schemas.billing import (
    BillCreate, BillResponse, PaymentUpdate, ChargeTypeResponse
)
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/billing", tags=["Billing & Payments"])


@router.get("/charge-types", response_model=List[ChargeTypeResponse])
async def get_charge_types(
    is_active: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Get all charge types."""
    query = select(ChargeType)
    if is_active:
        query = query.where(ChargeType.is_active == True)
    
    result = await db.execute(query)
    charge_types = result.scalars().all()
    
    return charge_types


@router.post("/bills", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
async def create_bill(
    bill_data: BillCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a bill (Doctor/Admin only)."""
    if current_user.role not in [UserRole.DOCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors and admins can create bills"
        )
    
    # Verify patient exists
    result = await db.execute(
        select(Patient).where(Patient.id == bill_data.patient_id)
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Generate bill number
    today = date.today()
    result = await db.execute(
        select(func.count(Bill.id)).where(Bill.bill_date == today)
    )
    count = result.scalar() or 0
    bill_number = f"BILL{today.strftime('%Y%m%d')}{str(count + 1).zfill(4)}"
    
    # Calculate totals
    subtotal = Decimal(0)
    for item in bill_data.items:
        item_total = item.unit_price * item.quantity
        subtotal += item_total
    
    # Calculate tax
    tax_amount = subtotal * Decimal(str(settings.TAX_RATE))
    
    # Calculate total
    total_amount = subtotal + tax_amount - bill_data.discount_amount
    
    # Create bill
    bill = Bill(
        bill_number=bill_number,
        patient_id=bill_data.patient_id,
        appointment_id=bill_data.appointment_id,
        bill_date=today,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=bill_data.discount_amount,
        total_amount=total_amount,
        payment_status=PaymentStatus.PENDING,
        notes=bill_data.notes
    )
    
    db.add(bill)
    await db.flush()
    
    # Create bill items
    for item_data in bill_data.items:
        item = BillItem(
            bill_id=bill.id,
            charge_type_id=item_data.charge_type_id,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total_price=item_data.unit_price * item_data.quantity
        )
        db.add(item)
    
    await db.commit()
    await db.refresh(bill)
    
    # Load items
    result = await db.execute(
        select(BillItem).where(BillItem.bill_id == bill.id)
    )
    bill.items = result.scalars().all()
    
    return bill


@router.get("/bills", response_model=List[BillResponse])
async def get_bills(
    patient_id: Optional[UUID] = None,
    payment_status: Optional[PaymentStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get bills."""
    query = select(Bill).where(Bill.is_deleted == False)
    
    # Filter based on user role
    if current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if patient:
            query = query.where(Bill.patient_id == patient.id)
        else:
            return []
    elif patient_id:
        query = query.where(Bill.patient_id == patient_id)
    
    if payment_status:
        query = query.where(Bill.payment_status == payment_status)
    
    query = query.order_by(Bill.bill_date.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    bills = result.scalars().all()
    
    # Load items for each bill
    for bill in bills:
        result = await db.execute(
            select(BillItem).where(BillItem.bill_id == bill.id)
        )
        bill.items = result.scalars().all()
    
    return bills


@router.get("/bills/{bill_id}", response_model=BillResponse)
async def get_bill(
    bill_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get bill details."""
    result = await db.execute(
        select(Bill).where(
            Bill.id == bill_id,
            Bill.is_deleted == False
        )
    )
    bill = result.scalar_one_or_none()
    
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    # Verify access for patients
    if current_user.role == UserRole.PATIENT:
        result = await db.execute(
            select(Patient).where(Patient.user_id == current_user.id)
        )
        patient = result.scalar_one_or_none()
        if not patient or patient.id != bill.patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Load items
    result = await db.execute(
        select(BillItem).where(BillItem.bill_id == bill.id)
    )
    bill.items = result.scalars().all()
    
    return bill


@router.patch("/bills/{bill_id}/payment", response_model=BillResponse)
async def update_payment_status(
    bill_id: UUID,
    payment_data: PaymentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update payment status."""
    result = await db.execute(
        select(Bill).where(
            Bill.id == bill_id,
            Bill.is_deleted == False
        )
    )
    bill = result.scalar_one_or_none()
    
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    # Update payment details
    bill.payment_status = payment_data.payment_status
    
    if payment_data.payment_status == PaymentStatus.PAID:
        bill.payment_date = datetime.utcnow()
        bill.payment_method = payment_data.payment_method
        bill.transaction_id = payment_data.transaction_id
    
    await db.commit()
    await db.refresh(bill)
    
    # Load items
    result = await db.execute(
        select(BillItem).where(BillItem.bill_id == bill.id)
    )
    bill.items = result.scalars().all()
    
    return bill


@router.get("/bills/{bill_id}/summary")
async def get_bill_summary(
    bill_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get bill summary for display/print."""
    result = await db.execute(
        select(Bill).where(
            Bill.id == bill_id,
            Bill.is_deleted == False
        )
    )
    bill = result.scalar_one_or_none()
    
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    # Get patient details
    result = await db.execute(
        select(Patient).where(Patient.id == bill.patient_id)
    )
    patient = result.scalar_one_or_none()
    
    # Get items with charge type names
    result = await db.execute(
        select(BillItem, ChargeType).join(
            ChargeType, BillItem.charge_type_id == ChargeType.id
        ).where(BillItem.bill_id == bill.id)
    )
    items_with_types = result.all()
    
    return {
        "bill_number": bill.bill_number,
        "bill_date": bill.bill_date,
        "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "N/A",
        "patient_phone": patient.phone if patient else "N/A",
        "items": [
            {
                "charge_type": charge_type.name,
                "description": item.description or charge_type.description,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "total_price": float(item.total_price)
            }
            for item, charge_type in items_with_types
        ],
        "subtotal": float(bill.subtotal),
        "tax_rate": float(settings.TAX_RATE * 100),
        "tax_amount": float(bill.tax_amount),
        "discount_amount": float(bill.discount_amount),
        "total_amount": float(bill.total_amount),
        "payment_status": bill.payment_status,
        "payment_date": bill.payment_date,
        "payment_method": bill.payment_method,
        "transaction_id": bill.transaction_id,
        "notes": bill.notes,
        "currency": settings.CURRENCY
    }
