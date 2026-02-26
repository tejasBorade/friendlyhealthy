"""
SymptoTrack Prescription Extras Models
- DigitalSignature: Doctor's PIN-protected digital signature
- PrescriptionSignature: Links a signature to a signed prescription
- DoctorMedicineFavorite: Doctor's personal medicine quick-select list
- PrescriptionTemplate: Template-based prescription entry
- TestOrdered: Individual test ordered in a prescription
- NotificationPreference: Per-user notification settings
- DeviceToken: FCM/APNS device registration for push notifications
"""
from sqlalchemy import (
    Column, String, Integer, Text, Boolean, DateTime, Date, Time,
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

class TestOrderStatus(str, enum.Enum):
    ORDERED = "ordered"
    UPLOADED = "uploaded"
    MISSING = "missing"


class NotificationChannel(str, enum.Enum):
    PUSH = "push"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class DevicePlatform(str, enum.Enum):
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"


# ============================================================
# DIGITAL SIGNATURES
# ============================================================

class DigitalSignature(Base):
    """
    Doctor's digital signature for prescriptions.
    PIN-protected. Signature image stored as file.
    """
    __tablename__ = "digital_signatures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="CASCADE"),
        unique=True, nullable=False, index=True
    )
    signature_image_path = Column(String(500), nullable=False)
    signature_pin_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PrescriptionSignature(Base):
    """
    Links a signature to a signed prescription.
    Once signed, the prescription is locked (immutable).
    """
    __tablename__ = "prescription_signatures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("prescriptions.id", ondelete="CASCADE"),
        unique=True, nullable=False, index=True
    )
    signature_id = Column(
        UUID(as_uuid=True),
        ForeignKey("digital_signatures.id", ondelete="CASCADE"),
        nullable=False
    )
    signed_at = Column(DateTime(timezone=True), server_default=func.now())
    is_locked = Column(Boolean, default=True)  # Prescription immutable after signing


# ============================================================
# DOCTOR MEDICINE FAVORITES
# ============================================================

class DoctorMedicineFavorite(Base):
    """
    Doctor's personal quick-select medicine list.
    Frequently used medicines for fast prescription writing.
    """
    __tablename__ = "doctor_medicine_favorites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    medicine_name = Column(String(200), nullable=False)
    dosage = Column(String(100), nullable=True)
    frequency = Column(String(50), nullable=True)  # e.g., "1-0-1"
    usage_instructions = Column(Text, nullable=True)  # e.g., "after food"
    duration_days = Column(Integer, nullable=True)
    category = Column(String(100), nullable=True)  # e.g., "Antibiotics"
    usage_count = Column(Integer, default=0)  # Auto-increment on use
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ============================================================
# PRESCRIPTION TEMPLATES
# ============================================================

class PrescriptionTemplate(Base):
    """
    Template-based prescription entry for common diagnoses.
    Doctor creates reusable templates for quick prescriptions.
    """
    __tablename__ = "prescription_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    template_name = Column(String(200), nullable=False)
    diagnosis = Column(Text, nullable=False)
    diagnosis_icd10_code = Column(String(20), nullable=True)

    # Structured medicine list
    # [{medicine_name, dosage, frequency, duration_days, instructions}]
    medicines = Column(JSONB, nullable=False, default=[])

    # Structured test list
    # [{test_name, test_type, notes}]
    tests = Column(JSONB, nullable=True, default=[])

    instructions = Column(Text, nullable=True)
    follow_up_days = Column(Integer, nullable=True)
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ============================================================
# TESTS ORDERED
# ============================================================

class TestOrdered(Base):
    """
    Individual test ordered within a prescription.
    Tracks ordered → uploaded → missing lifecycle.
    """
    __tablename__ = "tests_ordered"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("prescriptions.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    test_name = Column(String(200), nullable=False)
    test_type = Column(String(100), nullable=True)  # blood_test, xray, mri, etc.
    notes = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)  # Should be done before follow-up
    status = Column(
        SQLEnum(TestOrderStatus),
        default=TestOrderStatus.ORDERED, index=True
    )
    report_id = Column(
        UUID(as_uuid=True),
        ForeignKey("medical_reports.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ============================================================
# NOTIFICATION PREFERENCES
# ============================================================

class NotificationPreference(Base):
    """
    Per-user notification settings.
    Controls which reminders/alerts to receive and through which channel.
    """
    __tablename__ = "notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False, index=True
    )

    # Reminder toggles
    medicine_reminders = Column(Boolean, default=True)
    follow_up_reminders = Column(Boolean, default=True)
    test_reminders = Column(Boolean, default=True)
    doctor_messages = Column(Boolean, default=True)
    report_alerts = Column(Boolean, default=True)
    security_alerts = Column(Boolean, default=True)  # Always on, but user can see setting

    # Quiet hours (default 10 PM - 7 AM)
    quiet_hours_enabled = Column(Boolean, default=True)
    quiet_hours_start = Column(Time, nullable=True)  # Default: 22:00
    quiet_hours_end = Column(Time, nullable=True)  # Default: 07:00

    # Preferred channel
    preferred_channel = Column(
        SQLEnum(NotificationChannel),
        default=NotificationChannel.PUSH
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ============================================================
# DEVICE TOKENS (Push Notifications)
# ============================================================

class DeviceToken(Base):
    """
    FCM/APNS device token for push notifications.
    Supports multiple devices per user.
    """
    __tablename__ = "device_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    device_token = Column(String(500), unique=True, nullable=False)
    platform = Column(SQLEnum(DevicePlatform), nullable=False)
    device_info = Column(JSONB, nullable=True)  # {model, os_version, app_version}
    is_active = Column(Boolean, default=True, index=True)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
