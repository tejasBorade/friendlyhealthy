"""
PDF Generator Service for SymptoTrack
Generates prescription PDFs with doctor letterhead and digital signature.
"""

from typing import Optional
from datetime import datetime
from uuid import UUID
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.core.config import settings
from app.models.medical import Prescription, PrescriptionMedicine, Consultation
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.prescription_extras import DigitalSignature, PrescriptionSignature

logger = logging.getLogger(__name__)

# Try to import reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch, cm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    logger.warning("reportlab not installed. PDF generation will not work. Install with: pip install reportlab")
    REPORTLAB_AVAILABLE = False


class PDFGenerator:
    """Service for generating prescription PDFs."""

    def __init__(self):
        """Initialize PDF generator."""
        # Create upload directory if it doesn't exist
        self.upload_dir = Path(settings.UPLOAD_DIR) / "prescriptions"
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def generate_prescription_pdf(
        self,
        db: AsyncSession,
        prescription_id: UUID
    ) -> str:
        """
        Generate a prescription PDF with letterhead and signature.
        
        Args:
            db: Database session
            prescription_id: Prescription UUID
            
        Returns:
            str: Path to generated PDF file
            
        Raises:
            Exception: If PDF generation fails
        """
        if not REPORTLAB_AVAILABLE:
            raise Exception("PDF generation not available. Install reportlab: pip install reportlab")
        
        # Get prescription with all details
        result = await db.execute(
            select(Prescription).where(Prescription.id == prescription_id)
        )
        prescription = result.scalar_one_or_none()
        if not prescription:
            raise Exception("Prescription not found")
        
        # Get related data
        result = await db.execute(
            select(Doctor).where(Doctor.id == prescription.doctor_id)
        )
        doctor = result.scalar_one_or_none()
        
        result = await db.execute(
            select(Patient).where(Patient.id == prescription.patient_id)
        )
        patient = result.scalar_one_or_none()
        
        result = await db.execute(
            select(Consultation).where(Consultation.id == prescription.consultation_id)
        )
        consultation = result.scalar_one_or_none()
        
        result = await db.execute(
            select(PrescriptionMedicine).where(
                PrescriptionMedicine.prescription_id == prescription_id
            )
        )
        medicines = result.scalars().all()
        
        # Get digital signature if prescription is signed
        signature_image_path = None
        if prescription.is_signed:
            result = await db.execute(
                select(PrescriptionSignature).where(
                    PrescriptionSignature.prescription_id == prescription_id
                )
            )
            prescription_signature = result.scalar_one_or_none()
            if prescription_signature:
                result = await db.execute(
                    select(DigitalSignature).where(
                        DigitalSignature.id == prescription_signature.signature_id
                    )
                )
                signature = result.scalar_one_or_none()
                if signature:
                    signature_image_path = signature.signature_image_path
        
        # Generate PDF
        filename = f"prescription_{prescription.prescription_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = self.upload_dir / filename
        
        self._create_pdf(
            filepath=str(filepath),
            prescription=prescription,
            doctor=doctor,
            patient=patient,
            consultation=consultation,
            medicines=medicines,
            signature_image_path=signature_image_path
        )
        
        # Return relative path
        return str(filepath.relative_to(Path(settings.UPLOAD_DIR).parent))

    def _create_pdf(
        self,
        filepath: str,
        prescription,
        doctor,
        patient,
        consultation,
        medicines,
        signature_image_path: Optional[str] = None
    ):
        """
        Create the PDF file with prescription details.
        
        Args:
            filepath: Path to save PDF
            prescription: Prescription model
            doctor: Doctor model
            patient: Patient model
            consultation: Consultation model
            medicines: List of PrescriptionMedicine models
            signature_image_path: Optional path to signature image
        """
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )
        
        # Container for PDF elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=12,
            alignment=1  # Center
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#424242'),
            spaceAfter=6
        )
        normal_style = styles['Normal']
        
        # ===== HEADER / LETTERHEAD =====
        # Doctor name and clinic
        doctor_name = f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else "Unknown Doctor"
        elements.append(Paragraph(doctor_name, title_style))
        
        if doctor and doctor.qualification:
            elements.append(Paragraph(f"<b>{doctor.qualification}</b>", normal_style))
        
        if doctor and doctor.registration_number:
            elements.append(Paragraph(f"Reg. No: {doctor.registration_number}", normal_style))
        
        if doctor and doctor.clinic_name:
            elements.append(Paragraph(f"<b>{doctor.clinic_name}</b>", normal_style))
        
        if doctor and doctor.clinic_address:
            elements.append(Paragraph(doctor.clinic_address, normal_style))
        
        if doctor and doctor.phone:
            elements.append(Paragraph(f"Phone: {doctor.phone}", normal_style))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Horizontal line
        elements.append(Spacer(1, 0.1*inch))
        
        # ===== PATIENT INFORMATION =====
        patient_info_data = []
        if patient:
            patient_name = f"{patient.first_name} {patient.last_name}"
            patient_info_data = [
                ['Patient Name:', patient_name, 'Date:', prescription.prescription_date.strftime('%d %b %Y')],
                ['Age/Gender:', f"{self._calculate_age(patient.date_of_birth)} yrs / {patient.gender.value.title()}", 'Rx No:', prescription.prescription_number],
            ]
        
        if patient_info_data:
            patient_table = Table(patient_info_data, colWidths=[2*cm, 7*cm, 2*cm, 5*cm])
            patient_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(patient_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # ===== DIAGNOSIS =====
        if consultation and consultation.diagnosis:
            elements.append(Paragraph("<b>Diagnosis:</b>", heading_style))
            
            # Show both ICD-10 and patient-friendly diagnosis if available
            if prescription.diagnosis_patient_friendly:
                elements.append(Paragraph(prescription.diagnosis_patient_friendly, normal_style))
            else:
                elements.append(Paragraph(consultation.diagnosis, normal_style))
            
            if prescription.diagnosis_icd10_code:
                elements.append(Paragraph(f"<i>(ICD-10: {prescription.diagnosis_icd10_code})</i>", normal_style))
            
            elements.append(Spacer(1, 0.2*inch))
        
        # ===== MEDICINES (Rx) =====
        elements.append(Paragraph("<b>℞ Prescription:</b>", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        if medicines:
            medicine_data = [['S.No', 'Medicine', 'Dosage', 'Frequency', 'Duration']]
            for idx, med in enumerate(medicines, 1):
                medicine_data.append([
                    str(idx),
                    med.medicine_name,
                    med.dosage,
                    med.frequency,
                    f"{med.duration_days} days"
                ])
            
            medicine_table = Table(medicine_data, colWidths=[1*cm, 7*cm, 3*cm, 3*cm, 2.5*cm])
            medicine_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E3F2FD')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
            ]))
            elements.append(medicine_table)
        else:
            elements.append(Paragraph("<i>No medicines prescribed</i>", normal_style))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # ===== INSTRUCTIONS =====
        if prescription.patient_instructions:
            elements.append(Paragraph("<b>Instructions for Patient:</b>", heading_style))
            elements.append(Paragraph(prescription.patient_instructions, normal_style))
            elements.append(Spacer(1, 0.1*inch))
        
        if prescription.special_instructions:
            elements.append(Paragraph("<b>Special Instructions:</b>", heading_style))
            elements.append(Paragraph(prescription.special_instructions, normal_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # ===== FOLLOW-UP =====
        if prescription.follow_up_date:
            elements.append(Paragraph(
                f"<b>Follow-up Date:</b> {prescription.follow_up_date.strftime('%d %b %Y')}", 
                heading_style
            ))
            elements.append(Spacer(1, 0.2*inch))
        
        # ===== SIGNATURE =====
        elements.append(Spacer(1, 0.3*inch))
        
        # If signature image exists, add it
        if signature_image_path and os.path.exists(signature_image_path):
            try:
                sig_img = Image(signature_image_path, width=2*inch, height=1*inch)
                elements.append(sig_img)
            except Exception as e:
                logger.warning(f"Could not add signature image: {e}")
        
        elements.append(Paragraph(f"<b>{doctor_name}</b>", normal_style))
        if doctor and doctor.registration_number:
            elements.append(Paragraph(f"Reg. No: {doctor.registration_number}", normal_style))
        
        if prescription.signed_at:
            elements.append(Paragraph(
                f"<i>Digitally signed on {prescription.signed_at.strftime('%d %b %Y, %I:%M %p')}</i>",
                normal_style
            ))
        
        # ===== FOOTER =====
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(
            "<i>This is a digitally generated prescription. Please consult your doctor if you have any questions.</i>",
            ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey, alignment=1)
        ))
        
        # Build PDF
        doc.build(elements)
        logger.info(f"Generated prescription PDF: {filepath}")

    def _calculate_age(self, dob) -> int:
        """Calculate age from date of birth."""
        if not dob:
            return 0
        today = datetime.now().date()
        age = today.year - dob.year
        if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
            age -= 1
        return age


# Singleton instance
pdf_generator = PDFGenerator()
