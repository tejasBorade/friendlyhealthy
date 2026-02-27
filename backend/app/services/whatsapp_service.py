"""
WhatsApp Notification Service
Sprint 2.2: Notification Delivery
"""

from typing import Dict
from uuid import UUID

from twilio.rest import Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.user import User


class WhatsAppService:
    """Service for sending WhatsApp messages via Twilio."""
    
    _client = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Twilio client."""
        if cls._client is None:
            cls._client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
        return cls._client
    
    @staticmethod
    async def send_message(
        phone_number: str,
        message: str
    ) -> Dict:
        """
        Send WhatsApp message via Twilio.
        
        Args:
            phone_number: Recipient's phone number (with country code)
            message: Message text
            
        Returns:
            Dict with success status and message SID
        """
        if not settings.WHATSAPP_ENABLED:
            return {
                "success": False,
                "error": "WhatsApp not enabled"
            }
        
        try:
            client = WhatsAppService.get_client()
            
            # Twilio WhatsApp format: whatsapp:+country_code_phone
            from_number = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"
            to_number = f"whatsapp:{phone_number}"
            
            message_obj = client.messages.create(
                from_=from_number,
                body=message,
                to=to_number
            )
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "status": message_obj.status
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def send_medicine_reminder(
        phone_number: str,
        medicine_name: str,
        dosage: str,
        timing_label: str
    ) -> Dict:
        """
        Send medicine reminder via WhatsApp.
        
        Args:
            phone_number: Patient's phone number
            medicine_name: Medicine name
            dosage: Dosage information
            timing_label: Time label (Morning/Afternoon/Night)
            
        Returns:
            API response dict
        """
        message = f"""💊 *Medicine Reminder - {timing_label}*

Time to take: *{medicine_name}*
Dosage: {dosage}

Don't forget to take your medicine!

_SymptoTrack Health Reminder_"""
        
        return await WhatsAppService.send_message(phone_number, message)
    
    @staticmethod
    async def send_follow_up_reminder(
        phone_number: str,
        doctor_name: str,
        follow_up_date: str,
        days_remaining: int
    ) -> Dict:
        """
        Send follow-up appointment reminder via WhatsApp.
        
        Args:
            phone_number: Patient's phone number
            doctor_name: Doctor's name
            follow_up_date: Follow-up date string
            days_remaining: Days until follow-up
            
        Returns:
            API response dict
        """
        if days_remaining == 0:
            message = f"""📅 *Follow-up Reminder*

You have a follow-up appointment with *Dr. {doctor_name}* today!

Please ensure you arrive on time.

_SymptoTrack Health Reminder_"""
        elif days_remaining == 1:
            message = f"""📅 *Follow-up Reminder*

Reminder: You have a follow-up appointment with *Dr. {doctor_name}* tomorrow.

Date: {follow_up_date}

_SymptoTrack Health Reminder_"""
        else:
            message = f"""📅 *Follow-up Reminder*

You have a follow-up appointment with *Dr. {doctor_name}* in {days_remaining} days.

Date: {follow_up_date}

_SymptoTrack Health Reminder_"""
        
        return await WhatsAppService.send_message(phone_number, message)
    
    @staticmethod
    async def send_test_reminder(
        phone_number: str,
        test_name: str,
        due_date: str
    ) -> Dict:
        """
        Send test completion reminder via WhatsApp.
        
        Args:
            phone_number: Patient's phone number
            test_name: Test name
            due_date: Test due date
            
        Returns:
            API response dict
        """
        message = f"""🔬 *Test Reminder*

Reminder to complete: *{test_name}*

Please complete this test by: {due_date}

_SymptoTrack Health Reminder_"""
        
        return await WhatsAppService.send_message(phone_number, message)
    
    @staticmethod
    async def send_prescription_ready(
        phone_number: str,
        doctor_name: str,
        prescription_date: str
    ) -> Dict:
        """
        Notify patient that prescription is ready.
        
        Args:
            phone_number: Patient's phone number
            doctor_name: Doctor's name
            prescription_date: Prescription date
            
        Returns:
            API response dict
        """
        message = f"""📋 *New Prescription Available*

Dr. {doctor_name} has created a new prescription for you.

Date: {prescription_date}

Login to SymptoTrack to view details.

_SymptoTrack Health Platform_"""
        
        return await WhatsAppService.send_message(phone_number, message)
