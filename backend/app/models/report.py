from sqlalchemy import Column, String, Integer, Date, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True, index=True)
    report_type = Column(String(100), nullable=False)
    report_date = Column(Date, nullable=False)
    findings = Column(Text, nullable=True)
    file_url = Column(String(500), nullable=True)
    test_name = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
