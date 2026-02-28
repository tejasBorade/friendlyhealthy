from sqlalchemy import Column, String, Integer, Date, Text, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)  # Stored as string, not SQLEnum
    phone = Column(String(20), nullable=False, index=True)
    alternate_phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    country = Column(String(100), default="India")
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    blood_group = Column(String(10), nullable=True)
    profile_picture = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    # SymptoTrack: ABHA & health profile
    abha_id = Column(String(50), unique=True, nullable=True, index=True)
    abha_address = Column(String(100), nullable=True)
    known_allergies = Column(Text, nullable=True)
    chronic_conditions = Column(Text, nullable=True)
    caregiver_name = Column(String(200), nullable=True)
    caregiver_phone = Column(String(20), nullable=True)
