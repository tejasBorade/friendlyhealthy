"""
SymptoTrack Consent & Compliance Models
- ConsentRecord: DPDP Act consent tracking
- EmergencyAccessLog: Break-the-Glass access audit
- DataErasureRequest: Right to erasure workflow
- DoctorVerification: NMC/State Council verification queue
"""
from sqlalchemy import (
    Column, String, Integer, Text, Boolean, DateTime, Date,
    Enum as SQLEnum, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


# ============================================================
# ENUMS
# ============================================================

class ConsentType(str, enum.Enum):
    VIEW_RECORDS = "view_records"
    VIEW_REPORTS = "view_reports"
    VIEW_PRESCRIPTIONS = "view_prescriptions"
    SHARE_TIMELINE = "share_timeline"
    EMERGENCY_ACCESS = "emergency_access"
    ABDM_DATA_PULL = "abdm_data_pull"
    AI_PROCESSING = "ai_processing"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"


class ErasureStatus(str, enum.Enum):
    REQUESTED = "requested"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"  # Some data legally retained
    REJECTED = "rejected"


class EmergencyReviewStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    FLAGGED = "flagged"


# ============================================================
# CONSENT RECORDS (DPDP Act)
# ============================================================

class ConsentRecord(Base):
    """
    Every consent event logged: Patient grants/revokes doctor access.
    Immutable — cannot be edited or deleted.
    """
    __tablename__ = "consent_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    doctor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    consent_type = Column(SQLEnum(ConsentType), nullable=False)
    purpose = Column(Text, nullable=False)  # Why consent is needed
    duration_days = Column(Integer, nullable=True)  # NULL = indefinite until revoked
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    device_info = Column(JSONB, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================
# EMERGENCY ACCESS LOG (Break-the-Glass)
# ============================================================

class EmergencyAccessLog(Base):
    """
    Logged when a doctor accesses patient data without prior consent.
    Requires justification and mandatory review within 48 hours.
    Patient auto-notified after access.
    """
    __tablename__ = "emergency_access_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    justification = Column(Text, nullable=False)
    accessed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Review tracking (mandatory within 48 hours)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    review_status = Column(
        SQLEnum(EmergencyReviewStatus),
        default=EmergencyReviewStatus.PENDING, index=True
    )
    review_notes = Column(Text, nullable=True)
    patient_notified = Column(Boolean, default=False)
    patient_notified_at = Column(DateTime(timezone=True), nullable=True)


# ============================================================
# DATA ERASURE REQUESTS (DPDP Right to Erasure)
# ============================================================

class DataErasureRequest(Base):
    """
    Patient requests data deletion under DPDP Act.
    30-day processing deadline.
    Prescriptions retained 7 years per Indian medical law.
    """
    __tablename__ = "data_erasure_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    deadline_date = Column(Date, nullable=False)  # requested_at + 30 days
    status = Column(
        SQLEnum(ErasureStatus),
        default=ErasureStatus.REQUESTED, index=True
    )
    processed_at = Column(DateTime(timezone=True), nullable=True)
    processed_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    processing_notes = Column(Text, nullable=True)
    data_retained_reason = Column(Text, nullable=True)  # Legal basis for retention
    erasure_report = Column(JSONB, nullable=True)  # What was deleted vs retained
    confirmation_sent = Column(Boolean, default=False)


# ============================================================
# DOCTOR VERIFICATION QUEUE
# ============================================================

class DoctorVerification(Base):
    """
    NMC/State Medical Council verification workflow.
    Auto-verified via API or falls to manual queue.
    """
    __tablename__ = "doctor_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="CASCADE"),
        unique=True, nullable=False, index=True
    )
    nmc_registration_number = Column(String(100), nullable=False)
    state_council = Column(String(100), nullable=True)
    verification_status = Column(
        SQLEnum(VerificationStatus),
        default=VerificationStatus.PENDING, index=True
    )
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    rejection_reason = Column(Text, nullable=True)
    appeal_text = Column(Text, nullable=True)
    appeal_submitted_at = Column(DateTime(timezone=True), nullable=True)
    nmc_api_response = Column(JSONB, nullable=True)  # Raw API response for audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
