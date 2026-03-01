from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta, date
from typing import Dict
import asyncio

from app.core.config import settings
from app.services.email_service import EmailService

celery_app = Celery(
    "friendlyhealthy",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    broker_connection_retry_on_startup=False,  # Don't block FastAPI startup
    broker_connection_retry=True,  # Retry during task execution
    broker_connection_max_retries=10,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'check-appointment-reminders': {
        'task': 'check_appointment_reminders',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9 AM
    },
}


@celery_app.task(name="send_email")
def send_email_task(to_email: str, subject: str, html_body: str) -> Dict:
    """Send email notification using Gmail SMTP."""
    try:
        if not settings.EMAIL_ENABLED:
            print(f"Email disabled. Would send to {to_email}: {subject}")
            return {"status": "skipped", "to": to_email, "reason": "Email disabled"}
        
        success = EmailService.send_email(to_email, subject, html_body)
        return {"status": "sent" if success else "failed", "to": to_email}
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return {"status": "error", "to": to_email, "error": str(e)}


@celery_app.task(name="send_appointment_booking_email")
def send_appointment_booking_email(
    patient_email: str,
    patient_name: str,
    doctor_name: str,
    appointment_date: str,  # ISO format
    appointment_time: str,
    appointment_id: int
) -> Dict:
    """Send appointment booking confirmation email."""
    try:
        if not settings.EMAIL_ENABLED:
            return {"status": "skipped", "reason": "Email disabled"}
        
        # Parse date from ISO format
        appt_date = datetime.fromisoformat(appointment_date).date()
        
        success = EmailService.send_appointment_booking_notification(
            patient_email=patient_email,
            patient_name=patient_name,
            doctor_name=doctor_name,
            appointment_date=appt_date,
            appointment_time=appointment_time,
            appointment_id=appointment_id
        )
        return {"status": "sent" if success else "failed", "appointment_id": appointment_id}
    except Exception as e:
        print(f"Error sending appointment booking email: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="send_appointment_status_email")
def send_appointment_status_email(
    patient_email: str,
    patient_name: str,
    doctor_name: str,
    appointment_date: str,  # ISO format
    appointment_time: str,
    status: str,
    appointment_id: int
) -> Dict:
    """Send appointment status update email."""
    try:
        if not settings.EMAIL_ENABLED:
            return {"status": "skipped", "reason": "Email disabled"}
        
        # Parse date from ISO format
        appt_date = datetime.fromisoformat(appointment_date).date()
        
        success = EmailService.send_appointment_status_update(
            patient_email=patient_email,
            patient_name=patient_name,
            doctor_name=doctor_name,
            appointment_date=appt_date,
            appointment_time=appointment_time,
            status=status,
            appointment_id=appointment_id
        )
        return {"status": "sent" if success else "failed", "appointment_id": appointment_id}
    except Exception as e:
        print(f"Error sending appointment status email: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="send_appointment_reminder")
def send_appointment_reminder_task(
    patient_email: str,
    patient_name: str,
    doctor_name: str,
    appointment_date: str,  # ISO format
    appointment_time: str,
    appointment_id: int
) -> Dict:
    """Send appointment reminder email (24 hours before)."""
    try:
        if not settings.EMAIL_ENABLED:
            return {"status": "skipped", "reason": "Email disabled"}
        
        # Parse date from ISO format
        appt_date = datetime.fromisoformat(appointment_date).date()
        
        success = EmailService.send_appointment_reminder(
            patient_email=patient_email,
            patient_name=patient_name,
            doctor_name=doctor_name,
            appointment_date=appt_date,
            appointment_time=appointment_time,
            appointment_id=appointment_id
        )
        return {"status": "sent" if success else "failed", "appointment_id": appointment_id}
    except Exception as e:
        print(f"Error sending appointment reminder: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="send_prescription_notification_email")
def send_prescription_notification_email(
    patient_email: str,
    patient_name: str,
    doctor_name: str,
    prescription_date: str,  # ISO format
    prescription_id: int,
    medicines_count: int = 0
) -> Dict:
    """Send new prescription notification email."""
    try:
        if not settings.EMAIL_ENABLED:
            return {"status": "skipped", "reason": "Email disabled"}
        
        # Parse datetime from ISO format
        presc_date = datetime.fromisoformat(prescription_date)
        
        success = EmailService.send_prescription_notification(
            patient_email=patient_email,
            patient_name=patient_name,
            doctor_name=doctor_name,
            prescription_date=presc_date,
            prescription_id=prescription_id,
            medicines_count=medicines_count
        )
        return {"status": "sent" if success else "failed", "prescription_id": prescription_id}
    except Exception as e:
        print(f"Error sending prescription notification: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="check_appointment_reminders")
def check_appointment_reminders() -> Dict:
    """
    Periodic task to check for appointments tomorrow and send reminders.
    Runs daily at 9 AM.
    """
    try:
        from sqlalchemy import select, and_
        from app.models.appointment import Appointment
        from app.models.user import User
        from app.models.patient import Patient
        from app.models.doctor import Doctor
        from app.core.database import AsyncSessionLocal
        
        async def send_reminders():
            tomorrow = date.today() + timedelta(days=1)
            
            async with AsyncSessionLocal() as db:
                # Get appointments for tomorrow with status 'confirmed' or 'booked'
                result = await db.execute(
                    select(Appointment)
                    .where(
                        and_(
                            Appointment.appointment_date == tomorrow,
                            Appointment.status.in_(['confirmed', 'booked'])
                        )
                    )
                )
                appointments = result.scalars().all()
                
                sent_count = 0
                for appointment in appointments:
                    # Get patient details
                    patient_result = await db.execute(
                        select(Patient, User)
                        .join(User, Patient.user_id == User.id)
                        .where(Patient.id == appointment.patient_id)
                    )
                    patient_data = patient_result.first()
                    if not patient_data:
                        continue
                    
                    patient, patient_user = patient_data
                    
                    # Get doctor details
                    doctor_result = await db.execute(
                        select(Doctor, User)
                        .join(User, Doctor.user_id == User.id)
                        .where(Doctor.id == appointment.doctor_id)
                    )
                    doctor_data = doctor_result.first()
                    if not doctor_data:
                        continue
                    
                    doctor, doctor_user = doctor_data
                    
                    # Send reminder
                    send_appointment_reminder_task.delay(
                        patient_email=patient_user.email,
                        patient_name=patient.full_name,
                        doctor_name=doctor.full_name,
                        appointment_date=appointment.appointment_date.isoformat(),
                        appointment_time=str(appointment.appointment_time),
                        appointment_id=appointment.id
                    )
                    sent_count += 1
                
                return {"status": "completed", "reminders_sent": sent_count, "date": tomorrow.isoformat()}
        
        # Run async function
        return asyncio.run(send_reminders())
        
    except Exception as e:
        print(f"Error checking appointment reminders: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="send_sms")
def send_sms_task(to_phone: str, message: str) -> Dict:
    """Send SMS notification (Twilio integration needed)."""
    # TODO: Implement SMS sending using Twilio
    print(f"SMS would be sent to {to_phone}: {message}")
    return {"status": "not_implemented", "to": to_phone}


@celery_app.task(name="process_prescription_notification")
def process_prescription_notification_task(prescription_id: str, patient_email: str) -> Dict:
    """Legacy task - kept for compatibility."""
    subject = "New Prescription Available"
    body = f"<p>Your doctor has created a new prescription. Prescription ID: {prescription_id}</p>"
    return send_email_task(patient_email, subject, body)


@celery_app.task(name="process_bill_notification")
def process_bill_notification_task(bill_id: str, patient_email: str, amount: str) -> Dict:
    """Notify patient about new bill."""
    subject = "Medical Bill Generated"
    body = f"<p>A bill of {amount} has been generated. Bill ID: {bill_id}</p>"
    return send_email_task(patient_email, subject, body)
