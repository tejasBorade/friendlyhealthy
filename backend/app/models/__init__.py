# Import all models for Alembic migrations
from app.models.user import User, RefreshToken, UserRole
from app.models.patient import Patient, Gender
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.medical import (
    MedicalRecord, Prescription
)
from app.models.report import Report
from app.models.billing import Bill, BillItem, ChargeType, PaymentStatus
from app.models.notification import Notification

# --- SymptoTrack PRD v1.0: New models ---
from app.models.reminder import (
    MedicineReminder, MedicineReminderLog, FollowUpReminder, TestReminder,
    ReminderStatus, FollowUpStatus, TestUploadStatus
)
from app.models.consent import (
    ConsentRecord, EmergencyAccessLog, DataErasureRequest, DoctorVerification,
    ConsentType, VerificationStatus, ErasureStatus, EmergencyReviewStatus
)
from app.models.ai import (
    AISession, AISuggestion,
    AISuggestionType, AIDoctorAction, AIStatus
)
from app.models.message import (
    Message, DoctorPatientConnection,
    MessageType, PatientRequestType, ConnectionMethod
)
from app.models.prescription_extras import (
    DigitalSignature, PrescriptionSignature, DoctorMedicineFavorite,
    PrescriptionTemplate, TestOrdered, NotificationPreference, DeviceToken,
    TestOrderStatus, NotificationChannel, DevicePlatform
)

__all__ = [
    # Existing
    "User", "RefreshToken", "UserRole",
    "Patient", "Gender",
    "Doctor",
    "Appointment",
    "MedicalRecord", "Prescription",
    "Report",
    "Bill", "BillItem", "ChargeType", "PaymentStatus",
    "Notification",
    # Reminders
    "MedicineReminder", "MedicineReminderLog", "FollowUpReminder", "TestReminder",
    "ReminderStatus", "FollowUpStatus", "TestUploadStatus",
    # Consent & Compliance
    "ConsentRecord", "EmergencyAccessLog", "DataErasureRequest", "DoctorVerification",
    "ConsentType", "VerificationStatus", "ErasureStatus", "EmergencyReviewStatus",
    # AI
    "AISession", "AISuggestion",
    "AISuggestionType", "AIDoctorAction", "AIStatus",
    # Messaging
    "Message", "DoctorPatientConnection",
    "MessageType", "PatientRequestType", "ConnectionMethod",
    # Prescription Extras
    "DigitalSignature", "PrescriptionSignature", "DoctorMedicineFavorite",
    "PrescriptionTemplate", "TestOrdered", "NotificationPreference", "DeviceToken",
    "TestOrderStatus", "NotificationChannel", "DevicePlatform",
]
