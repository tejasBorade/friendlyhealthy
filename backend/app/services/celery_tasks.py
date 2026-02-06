from celery import Celery
from app.core.config import settings

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
)


@celery_app.task(name="send_email")
def send_email_task(to_email: str, subject: str, body: str):
    """Send email notification."""
    # TODO: Implement email sending using SendGrid or similar service
    # For now, just log the email
    print(f"Sending email to {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    return {"status": "sent", "to": to_email}


@celery_app.task(name="send_sms")
def send_sms_task(to_phone: str, message: str):
    """Send SMS notification."""
    # TODO: Implement SMS sending using Twilio or similar service
    # For now, just log the SMS
    print(f"Sending SMS to {to_phone}")
    print(f"Message: {message}")
    return {"status": "sent", "to": to_phone}


@celery_app.task(name="send_appointment_reminder")
def send_appointment_reminder_task(appointment_id: str):
    """Send appointment reminder 24 hours before appointment."""
    # TODO: Implement appointment reminder logic
    print(f"Sending appointment reminder for {appointment_id}")
    return {"status": "sent", "appointment_id": appointment_id}


@celery_app.task(name="process_prescription_notification")
def process_prescription_notification_task(prescription_id: str, patient_email: str):
    """Notify patient about new prescription."""
    subject = "New Prescription Available"
    body = f"Your doctor has created a new prescription. Prescription ID: {prescription_id}"
    send_email_task.delay(patient_email, subject, body)
    return {"status": "processed", "prescription_id": prescription_id}


@celery_app.task(name="process_bill_notification")
def process_bill_notification_task(bill_id: str, patient_email: str, amount: str):
    """Notify patient about new bill."""
    subject = "Medical Bill Generated"
    body = f"A bill of {amount} has been generated. Bill ID: {bill_id}"
    send_email_task.delay(patient_email, subject, body)
    return {"status": "processed", "bill_id": bill_id}
