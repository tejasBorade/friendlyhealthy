"""
Reminder Service
Sprint 2.1: Reminder Engine Core

Auto-generates reminders for:
- Medicine intake based on frequency
- Follow-up appointments
- Test completions
"""

from typing import List, Dict, Tuple
from uuid import UUID
from datetime import datetime, date, time, timedelta
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.medical import Prescription
from app.models.reminder import (
    MedicineReminder,
    FollowUpReminder,
    TestReminder,
    ReminderStatus,
    FollowUpStatus,
    TestUploadStatus
)
from app.models.prescription_extras import TestOrdered


class ReminderService:
    """Service for auto-generating and managing reminders."""
    
    # Default medicine timing slots
    DEFAULT_TIMINGS = {
        "morning": "08:00",
        "afternoon": "13:00",
        "evening": "18:00",
        "night": "21:00"
    }
    
    @staticmethod
    def parse_frequency_code(frequency: str) -> List[Dict[str, str]]:
        """
        Parse frequency code into timing slots.
        
        Examples:
        - "1-0-1" → [{"time": "08:00", "label": "Morning"}, {"time": "21:00", "label": "Night"}]
        - "1-1-1" → [{"time": "08:00", "label": "Morning"}, {"time": "13:00", "label": "Afternoon"}, {"time": "21:00", "label": "Night"}]
        - "1-1-1-1" → Morning, Afternoon, Evening, Night
        - "BD" → Morning, Night
        - "TDS" → Morning, Afternoon, Night
        - "QDS" → Morning, Afternoon, Evening, Night
        
        Args:
            frequency: Frequency code string
            
        Returns:
            List of timing slots with time and label
        """
        timing_slots = []
        
        # Handle common abbreviations
        frequency_upper = frequency.upper().strip()
        
        if frequency_upper == "BD" or frequency_upper == "BID":
            timing_slots = [
                {"time": ReminderService.DEFAULT_TIMINGS["morning"], "label": "Morning"},
                {"time": ReminderService.DEFAULT_TIMINGS["night"], "label": "Night"}
            ]
        elif frequency_upper == "TDS" or frequency_upper == "TID":
            timing_slots = [
                {"time": ReminderService.DEFAULT_TIMINGS["morning"], "label": "Morning"},
                {"time": ReminderService.DEFAULT_TIMINGS["afternoon"], "label": "Afternoon"},
                {"time": ReminderService.DEFAULT_TIMINGS["night"], "label": "Night"}
            ]
        elif frequency_upper == "QDS" or frequency_upper == "QID":
            timing_slots = [
                {"time": ReminderService.DEFAULT_TIMINGS["morning"], "label": "Morning"},
                {"time": ReminderService.DEFAULT_TIMINGS["afternoon"], "label": "Afternoon"},
                {"time": ReminderService.DEFAULT_TIMINGS["evening"], "label": "Evening"},
                {"time": ReminderService.DEFAULT_TIMINGS["night"], "label": "Night"}
            ]
        elif frequency_upper == "OD" or frequency_upper == "ONCE":
            timing_slots = [
                {"time": ReminderService.DEFAULT_TIMINGS["morning"], "label": "Morning"}
            ]
        else:
            # Try to parse as "N-N-N" format
            parts = frequency.split("-")
            
            if len(parts) >= 1 and parts[0].strip() != "0":
                timing_slots.append({
                    "time": ReminderService.DEFAULT_TIMINGS["morning"],
                    "label": "Morning"
                })
            
            if len(parts) >= 2 and parts[1].strip() != "0":
                timing_slots.append({
                    "time": ReminderService.DEFAULT_TIMINGS["afternoon"],
                    "label": "Afternoon"
                })
            
            if len(parts) >= 3 and parts[2].strip() != "0":
                timing_slots.append({
                    "time": ReminderService.DEFAULT_TIMINGS["night"],
                    "label": "Night"
                })
            
            # Handle 4-part frequency (morning-afternoon-evening-night)
            if len(parts) >= 4 and parts[3].strip() != "0":
                # Insert evening before night
                if len(timing_slots) > 0 and timing_slots[-1]["label"] == "Night":
                    timing_slots.insert(-1, {
                        "time": ReminderService.DEFAULT_TIMINGS["evening"],
                        "label": "Evening"
                    })
                else:
                    timing_slots.append({
                        "time": ReminderService.DEFAULT_TIMINGS["evening"],
                        "label": "Evening"
                    })
        
        # Default to once daily if no valid pattern found
        if not timing_slots:
            timing_slots = [
                {"time": ReminderService.DEFAULT_TIMINGS["morning"], "label": "Morning"}
            ]
        
        return timing_slots
    
    @staticmethod
    async def create_medicine_reminders(
        prescription_id: UUID,
        patient_id: UUID,
        medicines: List[Dict],
        start_date: date,
        db: AsyncSession
    ) -> List[MedicineReminder]:
        """
        Create medicine reminders for a prescription.
        
        Args:
            prescription_id: Prescription ID
            patient_id: Patient ID
            medicines: List of medicine dictionaries with name, dosage, frequency, duration_days
            start_date: Start date for reminders
            db: Database session
            
        Returns:
            List of created MedicineReminder objects
        """
        reminders = []
        
        for medicine in medicines:
            medicine_name = medicine.get("medicine_name", "Unknown")
            dosage = medicine.get("dosage", "")
            frequency = medicine.get("frequency", "OD")
            duration_days = medicine.get("duration_days", 7)
            
            # Parse frequency to timing slots
            timing_slots = ReminderService.parse_frequency_code(frequency)
            
            # Calculate end date
            end_date = start_date + timedelta(days=duration_days)
            
            # Create reminder
            reminder = MedicineReminder(
                prescription_id=prescription_id,
                prescription_medicine_id=medicine.get("id"),  # May be None
                patient_id=patient_id,
                medicine_name=medicine_name,
                dosage=dosage,
                frequency_code=frequency,
                timing_slots=timing_slots,
                start_date=start_date,
                end_date=end_date,
                status=ReminderStatus.ACTIVE,
                is_active=True,
                is_critical=medicine.get("is_critical", False)
            )
            
            db.add(reminder)
            reminders.append(reminder)
        
        await db.commit()
        return reminders
    
    @staticmethod
    async def create_follow_up_reminder(
        prescription_id: UUID,
        patient_id: UUID,
        doctor_id: UUID,
        follow_up_date: date,
        db: AsyncSession
    ) ->FollowUpReminder:
        """
        Create follow-up reminder for a prescription.
        
        Args:
            prescription_id: Prescription ID
            patient_id: Patient ID
            doctor_id: Doctor ID
            follow_up_date: Follow-up date
            db: Database session
            
        Returns:
            Created FollowUpReminder
        """
        reminder = FollowUpReminder(
            prescription_id=prescription_id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            follow_up_date=follow_up_date,
            status=FollowUpStatus.UPCOMING
        )
        
        db.add(reminder)
        await db.commit()
        await db.refresh(reminder)
        
        return reminder
    
    @staticmethod
    async def create_test_reminders(
        prescription_id: UUID,
        patient_id: UUID,
        test_orders: List[TestOrdered],
        follow_up_date: date = None,
        db: AsyncSession = None
    ) -> List[TestReminder]:
        """
        Create test reminders for ordered tests.
        
        Args:
            prescription_id: Prescription ID
            patient_id: Patient ID
            test_orders: List of TestOrdered objects
            follow_up_date: Optional follow-up date (tests should be done before this)
            db: Database session
            
        Returns:
            List of created TestReminder objects
        """
        reminders = []
        
        for test in test_orders:
            reminder = TestReminder(
                prescription_id=prescription_id,
                test_order_id=test.id,
                patient_id=patient_id,
                test_name=test.test_name,
                follow_up_date=follow_up_date,
                upload_status=TestUploadStatus.ORDERED
            )
            
            db.add(reminder)
            reminders.append(reminder)
        
        await db.commit()
        return reminders
    
    @staticmethod
    async def auto_generate_all_reminders(
        prescription_id: UUID,
        db: AsyncSession
    ) -> Dict[str, any]:
        """
        Auto-generate all applicable reminders for a prescription.
        
        Called after prescription is created/signed.
        
        Args:
            prescription_id: Prescription ID
            db: Database session
            
        Returns:
            Dictionary with counts of created reminders
        """
        # Get prescription with details
        result = await db.execute(
            select(Prescription).where(Prescription.id == prescription_id)
        )
        prescription = result.scalar_one_or_none()
        
        if not prescription:
            return {
                "error": "Prescription not found",
                "medicine_reminders": 0,
                "follow_up_reminder": False,
                "test_reminders": 0
            }
        
        start_date = prescription.prescribed_date.date() if prescription.prescribed_date else date.today()
        
        # 1. Create medicine reminders
        medicine_reminders = []
        if prescription.medicines:
            medicines_data = json.loads(prescription.medicines) if isinstance(prescription.medicines, str) else prescription.medicines
            medicine_reminders = await ReminderService.create_medicine_reminders(
                prescription_id=prescription_id,
                patient_id=prescription.patient_id,
                medicines=medicines_data,
                start_date=start_date,
                db=db
            )
        
        # 2. Create follow-up reminder
        follow_up_reminder = None
        if prescription.follow_up_date:
            follow_up_reminder = await ReminderService.create_follow_up_reminder(
                prescription_id=prescription_id,
                patient_id=prescription.patient_id,
                doctor_id=prescription.doctor_id,
                follow_up_date=prescription.follow_up_date,
                db=db
            )
        
        # 3. Create test reminders
        test_reminders = []
        result = await db.execute(
            select(TestOrdered).where(TestOrdered.prescription_id == prescription_id)
        )
        test_orders = result.scalars().all()
        
        if test_orders:
            test_reminders = await ReminderService.create_test_reminders(
                prescription_id=prescription_id,
                patient_id=prescription.patient_id,
                test_orders=test_orders,
                follow_up_date=prescription.follow_up_date,
                db=db
            )
        
        return {
            "success": True,
            "medicine_reminders": len(medicine_reminders),
            "follow_up_reminder": follow_up_reminder is not None,
            "test_reminders": len(test_reminders)
        }
