"""
SymptoTrack Reminder Models
- MedicineReminder: Auto-generated from prescription medicines
- FollowUpReminder: Tracks 7-day, 1-day, morning-of reminders
- TestReminder: Tracks ordered tests and upload status
"""
from sqlalchemy import (
    Column, String, Integer, Date, Boolean, DateTime,
    Enum as SQLEnum, ForeignKey, Time
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


# ============================================================
# ENUMS
# ============================================================

class ReminderStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    SNOOZED = "snoozed"
    MISSED = "missed"
    CANCELLED = "cancelled"


class FollowUpStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    VISITED = "visited"
    MISSED = "missed"
    CANCELLED = "cancelled"


class TestUploadStatus(str, enum.Enum):
    ORDERED = "ordered"
    UPLOADED = "uploaded"
    MISSING = "missing"


# ============================================================
# MEDICINE REMINDERS
# ============================================================

class MedicineReminder(Base):
    """
    Auto-created when a prescription is signed.
    One reminder per medicine per prescription.
    Runs for exact duration_days then auto-stops.
    """
    __tablename__ = "medicine_reminders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("prescriptions.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    prescription_medicine_id = Column(
        UUID(as_uuid=True),
        ForeignKey("prescription_medicines.id", ondelete="CASCADE"),
        nullable=False
    )
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # Medicine info (denormalized for quick notification rendering)
    medicine_name = Column(String(200), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency_code = Column(String(50), nullable=False)  # e.g. "1-0-1"

    # Timing slots derived from frequency_code
    # e.g. [{"time": "08:00", "label": "Morning"}, {"time": "20:00", "label": "Night"}]
    timing_slots = Column(JSONB, nullable=False, default=[])

    # Duration
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # State
    status = Column(SQLEnum(ReminderStatus), default=ReminderStatus.ACTIVE, index=True)
    is_active = Column(Boolean, default=True, index=True)
    is_critical = Column(Boolean, default=False)  # Insulin, heart meds → vibrate only in quiet hours

    # Tracking
    snooze_count = Column(Integer, default=0)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    total_taken = Column(Integer, default=0)
    total_missed = Column(Integer, default=0)

    # Doctor custom note for this reminder
    custom_note = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MedicineReminderLog(Base):
    """
    Log each individual reminder event (taken, missed, snoozed).
    """
    __tablename__ = "medicine_reminder_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reminder_id = Column(
        UUID(as_uuid=True),
        ForeignKey("medicine_reminders.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    action = Column(String(20), nullable=False)  # taken, missed, snoozed
    action_time = Column(DateTime(timezone=True), nullable=True)
    snoozed_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================
# FOLLOW-UP REMINDERS
# ============================================================

class FollowUpReminder(Base):
    """
    Auto-created when prescription has a follow_up_date.
    Sends 3 reminders: 7 days before, 1 day before, morning of.
    """
    __tablename__ = "follow_up_reminders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("prescriptions.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    doctor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False
    )

    follow_up_date = Column(Date, nullable=False, index=True)

    # Reminder send tracking
    reminder_7day_sent = Column(Boolean, default=False)
    reminder_7day_sent_at = Column(DateTime(timezone=True), nullable=True)
    reminder_1day_sent = Column(Boolean, default=False)
    reminder_1day_sent_at = Column(DateTime(timezone=True), nullable=True)
    reminder_morning_sent = Column(Boolean, default=False)
    reminder_morning_sent_at = Column(DateTime(timezone=True), nullable=True)

    # Status
    status = Column(SQLEnum(FollowUpStatus), default=FollowUpStatus.UPCOMING, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ============================================================
# TEST / INVESTIGATION REMINDERS
# ============================================================

class TestReminder(Base):
    """
    Auto-created when a prescription has tests_ordered.
    Reminds patient to get tests done before follow-up.
    """
    __tablename__ = "test_reminders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("prescriptions.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    test_order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tests_ordered.id", ondelete="CASCADE"),
        nullable=False
    )
    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    test_name = Column(String(200), nullable=False)
    follow_up_date = Column(Date, nullable=True)  # Get tested before this date

    # Reminder send tracking
    reminder_3day_sent = Column(Boolean, default=False)
    reminder_3day_sent_at = Column(DateTime(timezone=True), nullable=True)
    reminder_1day_sent = Column(Boolean, default=False)
    reminder_1day_sent_at = Column(DateTime(timezone=True), nullable=True)

    # Upload tracking
    upload_status = Column(
        SQLEnum(TestUploadStatus),
        default=TestUploadStatus.ORDERED, index=True
    )
    report_id = Column(
        UUID(as_uuid=True),
        ForeignKey("medical_reports.id", ondelete="SET NULL"),
        nullable=True
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
