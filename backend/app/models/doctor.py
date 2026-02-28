from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)
    qualification = Column(String(255), nullable=True)
    experience_years = Column(Integer, nullable=True)
    phone = Column(String(20), nullable=True)
    consultation_fee = Column(Numeric(10, 2), nullable=True)
    available_days = Column(String(255), nullable=True)
    available_hours = Column(String(100), nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
