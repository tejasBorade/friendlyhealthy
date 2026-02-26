"""
SymptoTrack Messaging & Connection Models
- Message: In-app doctor-patient messaging
- DoctorPatientConnection: QR code / 6-digit code based connections
"""
from sqlalchemy import (
    Column, String, Text, Boolean, DateTime,
    Enum as SQLEnum, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


# ============================================================
# ENUMS
# ============================================================

class MessageType(str, enum.Enum):
    PRESCRIPTION_FOLLOWUP = "prescription_followup"
    REPORT_REQUEST = "report_request"
    FOLLOWUP_CONFIRMATION = "followup_confirmation"
    CUSTOM_CLINICAL = "custom_clinical"
    PATIENT_REQUEST = "patient_request"
    SYSTEM = "system"


class PatientRequestType(str, enum.Enum):
    REQUEST_PRESCRIPTION_COPY = "request_prescription_copy"
    ASK_ABOUT_MEDICINE = "ask_about_medicine"
    REPORT_ISSUE = "report_issue"
    REQUEST_EARLIER_APPOINTMENT = "request_earlier_appointment"


class ConnectionMethod(str, enum.Enum):
    QR_CODE = "qr"
    CONNECT_CODE = "code"
    SEARCH = "search"
    PRESCRIPTION = "prescription"  # Auto-connected via prescription


# ============================================================
# IN-APP MESSAGES
# ============================================================

class Message(Base):
    """
    Doctor-patient in-app messaging.
    Doctor can send clinical messages.
    Patient can only send pre-defined requests or replies.
    """
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    receiver_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("prescriptions.id", ondelete="SET NULL"),
        nullable=True
    )
    message_type = Column(SQLEnum(MessageType), nullable=False, index=True)
    patient_request_type = Column(SQLEnum(PatientRequestType), nullable=True)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    is_ai_drafted = Column(Boolean, default=False)  # AI-drafted, doctor approved
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================
# DOCTOR-PATIENT CONNECTIONS
# ============================================================

class DoctorPatientConnection(Base):
    """
    Tracks how patients connect to doctors.
    Required before patient can receive prescriptions.
    """
    __tablename__ = "doctor_patient_connections"

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
    connect_code = Column(String(10), nullable=True)  # 6-digit code
    connection_method = Column(SQLEnum(ConnectionMethod), nullable=False)
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, index=True)
    disconnected_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
