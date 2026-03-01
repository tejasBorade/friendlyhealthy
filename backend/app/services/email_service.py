"""
Email Service using Gmail SMTP
Handles sending email notifications for appointments, prescriptions, and reminders.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime, date
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via Gmail SMTP."""
    
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_body: str,
        plain_body: Optional[str] = None
    ) -> bool:
        """
        Send an email using Gmail SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            plain_body: Plain text alternative (auto-generated from HTML if not provided)
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text part
            if plain_body:
                msg.attach(MIMEText(plain_body, 'plain'))
            
            # Add HTML part
            msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to Gmail SMTP server
            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls()
                server.login(settings.EMAIL_FROM, settings.EMAIL_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error(f"SMTP Authentication failed. Check Gmail credentials and App Password.")
            return False
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def send_appointment_booking_notification(
        patient_email: str,
        patient_name: str,
        doctor_name: str,
        appointment_date: date,
        appointment_time: str,
        appointment_id: int
    ) -> bool:
        """Send appointment booking confirmation email."""
        subject = "Appointment Booked Successfully"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Appointment Confirmed</h2>
                <p>Dear {patient_name},</p>
                <p>Your appointment has been successfully booked.</p>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Appointment Details:</strong></p>
                    <ul style="list-style: none; padding: 0;">
                        <li>📅 <strong>Date:</strong> {appointment_date.strftime('%B %d, %Y')}</li>
                        <li>⏰ <strong>Time:</strong> {appointment_time}</li>
                        <li>👨‍⚕️ <strong>Doctor:</strong> Dr. {doctor_name}</li>
                        <li>🔖 <strong>Appointment ID:</strong> #{appointment_id}</li>
                    </ul>
                </div>
                
                <p>Please arrive 15 minutes before your scheduled time.</p>
                
                <p>If you need to reschedule or cancel, please contact us as soon as possible.</p>
                
                <p style="margin-top: 30px;">Best regards,<br>
                <strong>{settings.EMAIL_FROM_NAME}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(patient_email, subject, html_body)
    
    @staticmethod
    def send_appointment_status_update(
        patient_email: str,
        patient_name: str,
        doctor_name: str,
        appointment_date: date,
        appointment_time: str,
        status: str,
        appointment_id: int
    ) -> bool:
        """Send appointment status update email."""
        status_messages = {
            'confirmed': {
                'title': 'Appointment Confirmed',
                'message': 'Your appointment has been confirmed by the doctor.',
                'color': '#10b981'
            },
            'cancelled': {
                'title': 'Appointment Cancelled',
                'message': 'Your appointment has been cancelled.',
                'color': '#ef4444'
            },
            'completed': {
                'title': 'Appointment Completed',
                'message': 'Your appointment has been completed. Thank you for visiting.',
                'color': '#6366f1'
            },
            'rejected': {
                'title': 'Appointment Rejected',
                'message': 'Unfortunately, your appointment request has been rejected. Please book another slot.',
                'color': '#f59e0b'
            }
        }
        
        status_info = status_messages.get(status, {
            'title': 'Appointment Update',
            'message': f'Your appointment status has been updated to: {status}',
            'color': '#6366f1'
        })
        
        subject = f"Appointment {status_info['title']} - #{appointment_id}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: {status_info['color']};">{status_info['title']}</h2>
                <p>Dear {patient_name},</p>
                <p>{status_info['message']}</p>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Appointment Details:</strong></p>
                    <ul style="list-style: none; padding: 0;">
                        <li>📅 <strong>Date:</strong> {appointment_date.strftime('%B %d, %Y')}</li>
                        <li>⏰ <strong>Time:</strong> {appointment_time}</li>
                        <li>👨‍⚕️ <strong>Doctor:</strong> Dr. {doctor_name}</li>
                        <li>🔖 <strong>Appointment ID:</strong> #{appointment_id}</li>
                        <li>📊 <strong>Status:</strong> <span style="color: {status_info['color']}; text-transform: uppercase;">{status}</span></li>
                    </ul>
                </div>
                
                <p style="margin-top: 30px;">Best regards,<br>
                <strong>{settings.EMAIL_FROM_NAME}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(patient_email, subject, html_body)
    
    @staticmethod
    def send_appointment_reminder(
        patient_email: str,
        patient_name: str,
        doctor_name: str,
        appointment_date: date,
        appointment_time: str,
        appointment_id: int
    ) -> bool:
        """Send appointment reminder email (24 hours before)."""
        subject = f"Reminder: Appointment Tomorrow with Dr. {doctor_name}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #f59e0b;">⏰ Appointment Reminder</h2>
                <p>Dear {patient_name},</p>
                <p>This is a friendly reminder about your upcoming appointment tomorrow.</p>
                
                <div style="background-color: #fef3c7; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                    <p><strong>📅 Tomorrow's Appointment:</strong></p>
                    <ul style="list-style: none; padding: 0;">
                        <li>⏰ <strong>Time:</strong> {appointment_time}</li>
                        <li>👨‍⚕️ <strong>Doctor:</strong> Dr. {doctor_name}</li>
                        <li>🔖 <strong>Appointment ID:</strong> #{appointment_id}</li>
                    </ul>
                </div>
                
                <p>📋 <strong>Things to remember:</strong></p>
                <ul>
                    <li>Arrive 15 minutes before your appointment time</li>
                    <li>Bring any relevant medical records or test results</li>
                    <li>Bring a list of current medications if applicable</li>
                </ul>
                
                <p>If you need to cancel or reschedule, please contact us as soon as possible.</p>
                
                <p style="margin-top: 30px;">Best regards,<br>
                <strong>{settings.EMAIL_FROM_NAME}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(patient_email, subject, html_body)
    
    @staticmethod
    def send_prescription_notification(
        patient_email: str,
        patient_name: str,
        doctor_name: str,
        prescription_date: datetime,
        prescription_id: int,
        medicines_count: int = 0
    ) -> bool:
        """Send new prescription notification email."""
        subject = "New Prescription Available"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #10b981;">💊 New Prescription</h2>
                <p>Dear {patient_name},</p>
                <p>Dr. {doctor_name} has issued a new prescription for you.</p>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Prescription Details:</strong></p>
                    <ul style="list-style: none; padding: 0;">
                        <li>📅 <strong>Date:</strong> {prescription_date.strftime('%B %d, %Y')}</li>
                        <li>👨‍⚕️ <strong>Prescribed by:</strong> Dr. {doctor_name}</li>
                        <li>🔖 <strong>Prescription ID:</strong> #{prescription_id}</li>
                        {f'<li>💊 <strong>Medicines:</strong> {medicines_count} items</li>' if medicines_count > 0 else ''}
                    </ul>
                </div>
                
                <p>Please login to your account to view the complete prescription details and follow the instructions carefully.</p>
                
                <p>⚠️ <strong>Important:</strong> Take medicines as prescribed and complete the full course.</p>
                
                <p style="margin-top: 30px;">Best regards,<br>
                <strong>{settings.EMAIL_FROM_NAME}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(patient_email, subject, html_body)
    
    @staticmethod
    def send_routine_checkup_reminder(
        patient_email: str,
        patient_name: str,
        checkup_type: str,
        due_date: date
    ) -> bool:
        """Send routine check-up reminder email."""
        subject = f"Reminder: {checkup_type} Due Soon"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #6366f1;">🏥 Routine Check-up Reminder</h2>
                <p>Dear {patient_name},</p>
                <p>This is a reminder that your routine check-up is due soon.</p>
                
                <div style="background-color: #ede9fe; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #6366f1;">
                    <p><strong>Check-up Information:</strong></p>
                    <ul style="list-style: none; padding: 0;">
                        <li>🔬 <strong>Type:</strong> {checkup_type}</li>
                        <li>📅 <strong>Due Date:</strong> {due_date.strftime('%B %d, %Y')}</li>
                    </ul>
                </div>
                
                <p>Regular check-ups are important for maintaining your health. Please schedule an appointment at your earliest convenience.</p>
                
                <p>📞 You can book an appointment by logging into your account or contacting our clinic directly.</p>
                
                <p style="margin-top: 30px;">Best regards,<br>
                <strong>{settings.EMAIL_FROM_NAME}</strong></p>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(patient_email, subject, html_body)
