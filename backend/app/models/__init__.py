# Import all models for Alembic migrations
from app.models.user import User, RefreshToken, UserRole
from app.models.patient import Patient, Gender
from app.models.doctor import (
    Doctor, Specialization, DoctorSpecialization, Clinic,
    DoctorAvailability, DoctorLeave, DayOfWeek
)
from app.models.appointment import Appointment, AppointmentStatus
from app.models.medical import (
    PatientMedicalHistory, Consultation, Prescription,
    PrescriptionMedicine, PrescriptionHistory
)
from app.models.report import MedicalReport, ReportType
from app.models.billing import Bill, BillItem, ChargeType, PaymentStatus
from app.models.notification import Notification, AuditLog, NotificationType, NotificationStatus

__all__ = [
    "User", "RefreshToken", "UserRole",
    "Patient", "Gender",
    "Doctor", "Specialization", "DoctorSpecialization", "Clinic",
    "DoctorAvailability", "DoctorLeave", "DayOfWeek",
    "Appointment", "AppointmentStatus",
    "PatientMedicalHistory", "Consultation", "Prescription",
    "PrescriptionMedicine", "PrescriptionHistory",
    "MedicalReport", "ReportType",
    "Bill", "BillItem", "ChargeType", "PaymentStatus",
    "Notification", "AuditLog", "NotificationType", "NotificationStatus",
]
