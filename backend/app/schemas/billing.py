from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from app.models.billing import PaymentStatus


class BillItemCreate(BaseModel):
    charge_type_id: UUID
    description: Optional[str] = None
    quantity: int = Field(1, gt=0)
    unit_price: Decimal = Field(..., ge=0)


class BillCreate(BaseModel):
    patient_id: UUID
    appointment_id: Optional[UUID] = None
    items: List[BillItemCreate]
    discount_amount: Decimal = Field(0, ge=0)
    notes: Optional[str] = None


class BillItemResponse(BaseModel):
    id: UUID
    charge_type_id: UUID
    description: Optional[str]
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    
    class Config:
        from_attributes = True


class BillResponse(BaseModel):
    id: UUID
    bill_number: str
    patient_id: UUID
    appointment_id: Optional[UUID]
    bill_date: date
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    payment_status: PaymentStatus
    payment_date: Optional[datetime]
    payment_method: Optional[str]
    transaction_id: Optional[str]
    notes: Optional[str]
    items: List[BillItemResponse] = []
    
    class Config:
        from_attributes = True


class PaymentUpdate(BaseModel):
    payment_status: PaymentStatus
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None


class ChargeTypeResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    default_amount: Decimal
    is_taxable: bool
    is_active: bool
    
    class Config:
        from_attributes = True
