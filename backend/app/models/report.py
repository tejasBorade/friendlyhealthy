from sqlalchemy import Column, String, Date, Text, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


class ReportType(str, enum.Enum):
    BLOOD_TEST = "blood_test"
    XRAY = "xray"
    MRI = "mri"
    CT_SCAN = "ct_scan"
    ECG = "ecg"
    ECHO = "echo"
    ULTRASOUND = "ultrasound"
    OTHER = "other"


class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True, index=True)
    report_type = Column(SQLEnum(ReportType), nullable=False, index=True)
    report_name = Column(String(200), nullable=False)
    test_date = Column(Date, nullable=False)
    lab_name = Column(String(200), nullable=True)
    lab_address = Column(Text, nullable=True)
    report_file_path = Column(String(500), nullable=False)
    doctor_remarks = Column(Text, nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    # SymptoTrack: Report linking & structured data for trends
    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id", ondelete="SET NULL"), nullable=True, index=True)
    test_order_id = Column(UUID(as_uuid=True), ForeignKey("tests_ordered.id", ondelete="SET NULL"), nullable=True)
    follow_up_date = Column(Date, nullable=True)
    structured_values = Column(JSONB, nullable=True)  # {"HbA1c": 6.5, "glucose": 110}
