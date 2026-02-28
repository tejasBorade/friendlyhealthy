from sqlalchemy import Column, String, Integer, Date, Time, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, nullable=True)
    doctor_id = Column(Integer, nullable=True)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    status = Column(String(20), default='scheduled')
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    status_updated_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    rescheduled_from = Column(Integer, nullable=True)
