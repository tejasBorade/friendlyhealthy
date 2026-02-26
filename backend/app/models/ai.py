"""
SymptoTrack AI Models
- AISuggestion: Logs every AI suggestion + doctor action
- AISession: Groups suggestions by prescription writing session
"""
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime,
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

class AISuggestionType(str, enum.Enum):
    DRUG_INTERACTION = "drug_interaction"
    DOSAGE_REFERENCE = "dosage_reference"
    DIAGNOSIS_GUIDANCE = "diagnosis_guidance"
    FOLLOW_UP_SUGGESTION = "follow_up_suggestion"
    TEST_SUGGESTION = "test_suggestion"
    FREE_CHAT = "free_chat"


class AIDoctorAction(str, enum.Enum):
    USED = "used"
    DISMISSED = "dismissed"
    NOTED = "noted"
    PENDING = "pending"  # Doctor hasn't acted yet


class AIStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    FALLBACK = "fallback"  # AI failed, showed generic response
    TIMEOUT = "timeout"


# ============================================================
# AI SESSION
# ============================================================

class AISession(Base):
    """
    Groups all AI interactions during one prescription writing session.
    """
    __tablename__ = "ai_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    # Context hash — hashed clinical context (no PII)
    patient_context_hash = Column(String(64), nullable=True)
    prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("prescriptions.id", ondelete="SET NULL"),
        nullable=True
    )
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    total_suggestions = Column(Integer, default=0)
    suggestions_used = Column(Integer, default=0)
    suggestions_dismissed = Column(Integer, default=0)


# ============================================================
# AI SUGGESTIONS
# ============================================================

class AISuggestion(Base):
    """
    Every AI suggestion generated, logged with:
    - What was suggested
    - What the doctor did (used/dismissed/noted)
    - Response time
    - NO patient PII — only clinical terms
    """
    __tablename__ = "ai_suggestions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_sessions.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    doctor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    # Suggestion details
    suggestion_type = Column(SQLEnum(AISuggestionType), nullable=False, index=True)
    input_context = Column(JSONB, nullable=True)  # Clinical terms only, no PII
    suggestion_text = Column(Text, nullable=False)
    suggestion_data = Column(JSONB, nullable=True)  # Structured data (drug list, dosages, etc.)
    reference_links = Column(JSONB, nullable=True)  # Source references

    # AI model metadata
    ai_model = Column(String(50), nullable=True)  # e.g. "gemini-pro"
    ai_status = Column(SQLEnum(AIStatus), default=AIStatus.SUCCESS)
    response_time_ms = Column(Integer, nullable=True)

    # Doctor action
    doctor_action = Column(
        SQLEnum(AIDoctorAction),
        default=AIDoctorAction.PENDING, index=True
    )
    doctor_action_at = Column(DateTime(timezone=True), nullable=True)
    doctor_notes = Column(Text, nullable=True)  # Doctor can add note when dismissing

    created_at = Column(DateTime(timezone=True), server_default=func.now())
