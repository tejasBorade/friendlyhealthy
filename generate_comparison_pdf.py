"""
Generate SymptoTrack PRD vs Current Implementation Comparison PDF
"""
from fpdf import FPDF

class ComparisonPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'SymptoTrack PRD v1.0 vs FriendlyHealthy - Gap Analysis', align='C')
        self.ln(4)
        self.set_draw_color(0, 120, 200)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(0, 80, 160)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 80, 160)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def sub_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(40, 40, 40)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text):
        self.set_font('Helvetica', '', 9)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def check_item(self, text, done=True):
        self.set_font('Helvetica', '', 9)
        if done:
            self.set_text_color(0, 140, 60)
            mark = "[Y] "
        else:
            self.set_text_color(200, 40, 40)
            mark = "[X] "
        self.cell(10, 5, mark)
        self.set_text_color(50, 50, 50)
        self.cell(0, 5, text, new_x="LMARGIN", new_y="NEXT")

    def add_table(self, headers, data, col_widths=None):
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)
        # Header
        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(0, 80, 160)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True, align='C')
        self.ln()
        # Data
        self.set_font('Helvetica', '', 8)
        self.set_text_color(40, 40, 40)
        fill = False
        for row in data:
            if self.get_y() > 260:
                self.add_page()
                self.set_font('Helvetica', 'B', 8)
                self.set_fill_color(0, 80, 160)
                self.set_text_color(255, 255, 255)
                for i, h in enumerate(headers):
                    self.cell(col_widths[i], 7, h, border=1, fill=True, align='C')
                self.ln()
                self.set_font('Helvetica', '', 8)
                self.set_text_color(40, 40, 40)
                fill = False
            if fill:
                self.set_fill_color(240, 245, 255)
            else:
                self.set_fill_color(255, 255, 255)
            for i, cell_text in enumerate(row):
                self.cell(col_widths[i], 6, str(cell_text), border=1, fill=True, align='C' if i > 0 else 'L')
            self.ln()
            fill = not fill
        self.ln(4)


def generate():
    pdf = ComparisonPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ====== COVER PAGE ======
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(0, 80, 160)
    pdf.cell(0, 15, 'SymptoTrack PRD v1.0', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 16)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, 'vs', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(0, 140, 60)
    pdf.cell(0, 15, 'Current Implementation', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)
    pdf.set_draw_color(0, 80, 160)
    pdf.set_line_width(1)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(15)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 12, 'Gap Analysis Report', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, 'Platform: FriendlyHealthy Healthcare Management', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, 'Date: February 26, 2026', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, 'Version: 1.0', align='C', new_x="LMARGIN", new_y="NEXT")

    # ====== OVERALL ASSESSMENT ======
    pdf.add_page()
    pdf.section_title('1. Overall Assessment')
    pdf.body_text(
        'The current "FriendlyHealthy" platform is a traditional healthcare management system, '
        'while the SymptoTrack PRD describes a modern, ABDM-compliant, India-specific prescription '
        'and reminder-focused platform. There is approximately 30-40% feature overlap, but significant '
        'gaps exist in compliance, mobile-first design, AI capabilities, and the smart reminder system.'
    )
    pdf.body_text(
        'Current Stack: React 18 + Material-UI + Redux Toolkit (Frontend), '
        'Python FastAPI + PostgreSQL + Redis (Backend), Cloudflare Workers + D1 (Edge Backend), '
        'Docker + Nginx (Infrastructure).'
    )
    pdf.body_text(
        'SymptoTrack Target: Mobile apps (Android + iOS) + Web Admin, ABDM/ABHA integration, '
        'FHIR R4 compliance, AI-assisted prescriptions, multi-channel notifications (Push/SMS/WhatsApp), '
        'DPDP Act compliance.'
    )

    # ====== FEATURE COMPLETION MATRIX ======
    pdf.section_title('2. Feature Completion Matrix')
    pdf.add_table(
        ['Module', 'PRD Priority', 'Current %', 'Gap Level'],
        [
            ['Digital Prescription Engine', 'P0 (Core)', '60%', 'Medium-High'],
            ['Smart Reminder System', 'P0 (Core)', '5%', 'CRITICAL'],
            ['Lab Report Linking', 'P1 (High)', '40%', 'High'],
            ['Patient Health Timeline', 'P1 (High)', '30%', 'High'],
            ['Doctor AI Assistant', 'P1 (High)', '0%', 'CRITICAL'],
            ['Login & Onboarding', 'P0 (Core)', '70%', 'Medium'],
            ['Notifications & Communication', 'P0 (Core)', '50%', 'High'],
            ['Admin Panel & Compliance', 'P1 (High)', '40%', 'High'],
            ['ABDM Compliance', 'P0 (Core)', '0%', 'CRITICAL'],
            ['Mobile Apps', 'P0 (Core)', '0%', 'CRITICAL'],
        ],
        col_widths=[65, 30, 25, 70]
    )

    # ====== MODULE 1 ======
    pdf.add_page()
    pdf.section_title('3. Module 1: Digital Prescription Engine (60%)')
    pdf.sub_title('Implemented')
    pdf.check_item('Prescription creation by doctors', True)
    pdf.check_item('Medicine management with prescriptions', True)
    pdf.check_item('Prescription versioning and history', True)
    pdf.check_item('Prescription number auto-generation', True)
    pdf.check_item('Patient-doctor prescription linking', True)
    pdf.ln(3)
    pdf.sub_title('Missing')
    pdf.check_item('Voice input with speech-to-text', False)
    pdf.check_item('AI-powered diagnosis structuring (ICD-10 coding)', False)
    pdf.check_item("Doctor's personal medicine favorites list", False)
    pdf.check_item('Template-based entry for common diagnoses', False)
    pdf.check_item('PDF generation with clinic letterhead and digital signature', False)
    pdf.check_item('Patient-friendly diagnosis language toggle', False)
    pdf.check_item('Tests ordered tracking with due dates', False)
    pdf.check_item('Follow-up date with AI suggestions', False)
    pdf.check_item('Prescription locking after digital signature (immutable)', False)
    pdf.check_item('PIN-protected digital signature panel', False)

    # ====== MODULE 2 ======
    pdf.ln(4)
    pdf.section_title('4. Module 2: Smart Reminder System (5%) - CRITICAL GAP')
    pdf.sub_title('Implemented')
    pdf.check_item('Basic appointment reminders toggle in settings UI', True)
    pdf.ln(3)
    pdf.sub_title('Missing')
    pdf.check_item('Medicine reminders (auto-generated from prescriptions)', False)
    pdf.check_item('Follow-up reminders (7 days, 1 day, morning of visit)', False)
    pdf.check_item('Test/investigation reminders', False)
    pdf.check_item('Auto-duration control (stops when prescription ends)', False)
    pdf.check_item('Lock screen privacy (no medicine names shown)', False)
    pdf.check_item('Snooze functionality (15 min max)', False)
    pdf.check_item('Color-coded reminder dashboard (Green/Blue/Yellow)', False)
    pdf.check_item('Critical medicine handling during quiet hours', False)
    pdf.check_item('Multi-channel delivery (Push > SMS > WhatsApp fallback)', False)
    pdf.check_item('Custom reminder notes by doctor during prescription', False)

    # ====== MODULE 3 ======
    pdf.add_page()
    pdf.section_title('5. Module 3: Lab Report Linking (40%)')
    pdf.sub_title('Implemented')
    pdf.check_item('Medical reports table and upload functionality', True)
    pdf.check_item('Report types (blood_test, xray, mri, ct_scan, etc.)', True)
    pdf.check_item('Doctor remarks on reports', True)
    pdf.check_item('File download with access control', True)
    pdf.ln(3)
    pdf.sub_title('Missing')
    pdf.check_item('Report linking to specific prescriptions and test orders', False)
    pdf.check_item('Upload status tracking (Ordered / Uploaded / Missing)', False)
    pdf.check_item('Doctor nudges for missing reports', False)
    pdf.check_item('Pre-visit summary showing ordered vs uploaded reports', False)
    pdf.check_item('Lab direct upload feature (partner lab logins)', False)
    pdf.check_item('ABDM / DigiLocker integration for record pull', False)
    pdf.check_item('Smart linking logic (prescription + test order + follow-up)', False)

    # ====== MODULE 4 ======
    pdf.ln(4)
    pdf.section_title('6. Module 4: Patient Health Timeline (30%)')
    pdf.sub_title('Implemented')
    pdf.check_item('Medical history tracking', True)
    pdf.check_item('Patient profile with demographics', True)
    pdf.check_item('Prescription history viewing', True)
    pdf.check_item('PatientJourney page exists in frontend', True)
    pdf.ln(3)
    pdf.sub_title('Missing')
    pdf.check_item('Chronological timeline view with visit cards', False)
    pdf.check_item('Visit completion status (Visited / Upcoming / Missed)', False)
    pdf.check_item('Health summary stats dashboard', False)
    pdf.check_item('Trend view for repeated tests (HbA1c, BP, Cholesterol)', False)
    pdf.check_item('Cross-doctor visibility of active medicines', False)
    pdf.check_item('Allergy and chronic condition flagging at top of chart', False)
    pdf.check_item('Health summary export as PDF', False)
    pdf.check_item('QR code sharing with 24-hour temporary access', False)
    pdf.check_item('Caregiver / family member limited access', False)

    # ====== MODULE 5 ======
    pdf.add_page()
    pdf.section_title('7. Module 5: Doctor AI Assistant (0%) - CRITICAL GAP')
    pdf.sub_title('Implemented')
    pdf.body_text('No AI assistant features have been implemented.')
    pdf.sub_title('Missing (Entire Module)')
    pdf.check_item('Drug interaction flagging in real-time', False)
    pdf.check_item('Dosage reference showing usual adult dose range', False)
    pdf.check_item('Diagnosis guidance per Indian clinical guidelines', False)
    pdf.check_item('Follow-up duration suggestions based on diagnosis', False)
    pdf.check_item('Test suggestion with check for recently done tests', False)
    pdf.check_item('Free chat for clinical questions with references', False)
    pdf.check_item('AI audit trail (all suggestions + doctor actions logged)', False)
    pdf.check_item('PHI protection (no patient data sent to AI models)', False)
    pdf.check_item('Side panel UI with collapse/expand', False)
    pdf.check_item('Persistent "Suggestive Only" label', False)
    pdf.check_item('AI never auto-fills prescriptions or suggests brand names', False)

    # ====== MODULE 6 ======
    pdf.ln(4)
    pdf.section_title('8. Module 6: Login & Onboarding (70%)')
    pdf.sub_title('Implemented')
    pdf.check_item('JWT authentication with refresh tokens', True)
    pdf.check_item('Role-based access control (Patient / Doctor / Admin)', True)
    pdf.check_item('User registration and login', True)
    pdf.check_item('Basic patient and doctor profiles', True)
    pdf.check_item('Doctor verification flag in database', True)
    pdf.ln(3)
    pdf.sub_title('Missing')
    pdf.check_item('OTP-based login (no passwords per PRD)', False)
    pdf.check_item('NMC / State Medical Council API verification', False)
    pdf.check_item('Digital signature setup (PIN protected)', False)
    pdf.check_item('ABHA ID creation / linking workflow', False)
    pdf.check_item('5-step structured onboarding flow', False)
    pdf.check_item('6-digit doctor-patient connect codes', False)
    pdf.check_item('QR code scan to connect to doctor', False)
    pdf.check_item('Biometric login option', False)
    pdf.check_item('Device tracking with new device alerts', False)
    pdf.check_item('HFR (Health Facility Registry) linking', False)
    pdf.check_item('Session timeout (10 min doctor / 30 min patient)', False)

    # ====== MODULE 7 ======
    pdf.add_page()
    pdf.section_title('9. Module 7: Notifications & Communication (50%)')
    pdf.sub_title('Implemented')
    pdf.check_item('Notification table and basic system', True)
    pdf.check_item('Celery background tasks for async processing', True)
    pdf.check_item('SendGrid (email) and Twilio (SMS) integration setup', True)
    pdf.check_item('Notification types and priorities (low/normal/high/urgent)', True)
    pdf.check_item('Read/unread tracking with badge count', True)
    pdf.ln(3)
    pdf.sub_title('Missing')
    pdf.check_item('Multi-channel fallback (Push > SMS > WhatsApp)', False)
    pdf.check_item('Medicine reminders from prescription data', False)
    pdf.check_item('Test reminders linked to follow-up dates', False)
    pdf.check_item('Quiet hours with critical medicine handling', False)
    pdf.check_item('In-app doctor-patient messaging', False)
    pdf.check_item('Pre-defined patient request templates', False)
    pdf.check_item('AI-drafted doctor messages (doctor approves before send)', False)
    pdf.check_item('Notification preferences per category', False)
    pdf.check_item('WhatsApp Business API integration', False)
    pdf.check_item('Push notification service (FCM / APNS)', False)

    # ====== MODULE 8 ======
    pdf.ln(4)
    pdf.section_title('10. Module 8: Admin Panel & Compliance (40%)')
    pdf.sub_title('Implemented')
    pdf.check_item('Admin role and dashboard', True)
    pdf.check_item('Audit logs table in database', True)
    pdf.check_item('Basic user management', True)
    pdf.ln(3)
    pdf.sub_title('Missing')
    pdf.check_item('Doctor verification queue with NMC API integration', False)
    pdf.check_item('Consent audit log viewer (immutable)', False)
    pdf.check_item('Emergency access (Break-the-Glass) tracking and review', False)
    pdf.check_item('DPDP data erasure request workflow (30-day deadline)', False)
    pdf.check_item('AI audit trail viewer', False)
    pdf.check_item('One-click regulatory reports (6 report types, PDF/CSV)', False)
    pdf.check_item('Sub-admin roles (Verification / Compliance / Support)', False)
    pdf.check_item('48-hour emergency access mandatory review system', False)

    # ====== COMPLIANCE GAPS ======
    pdf.add_page()
    pdf.section_title('11. Critical Compliance Gaps')

    pdf.sub_title('ABDM Compliance (0% Complete)')
    pdf.check_item('ABHA ID integration', False)
    pdf.check_item('FHIR R4 India profile mapping', False)
    pdf.check_item('Consent artefacts', False)
    pdf.check_item('Health locker integration', False)
    pdf.check_item('PHR (Personal Health Record) linking', False)

    pdf.ln(3)
    pdf.sub_title('DPDP Act 2023 Compliance (20% Complete)')
    pdf.check_item('Basic audit logging', True)
    pdf.check_item('Explicit consent flows with purpose and duration', False)
    pdf.check_item('Consent revocation mechanism', False)
    pdf.check_item('30-day data erasure processing workflow', False)
    pdf.check_item('Data retention policy (7-year prescriptions)', False)
    pdf.check_item('Right to be forgotten workflow', False)

    pdf.ln(3)
    pdf.sub_title('NMC Telemedicine Guidelines (10% Complete)')
    pdf.check_item('Doctor registration number field exists', True)
    pdf.check_item('NMC / State Council API verification', False)
    pdf.check_item('AI disclosure to patients', False)
    pdf.check_item('Doctor full control over AI suggestions', False)

    pdf.ln(3)
    pdf.sub_title('Security & Privacy (60% Complete)')
    pdf.check_item('TLS encryption (in transit)', True)
    pdf.check_item('JWT authentication', True)
    pdf.check_item('Password hashing (bcrypt)', True)
    pdf.check_item('Role-based access control', True)
    pdf.check_item('AES-256 encryption at rest', False)
    pdf.check_item('PHI protection from external AI models', False)
    pdf.check_item('Session timeout enforcement (10/30 min)', False)
    pdf.check_item('Failed OTP lockout mechanism', False)
    pdf.check_item('Penetration testing', False)

    # ====== ARCHITECTURE GAPS ======
    pdf.add_page()
    pdf.section_title('12. Architecture Gaps')
    pdf.sub_title('Current Architecture')
    pdf.body_text(
        '- Frontend: React 18 + Material-UI + Redux Toolkit (Web only)\n'
        '- Backend: Python FastAPI + PostgreSQL + Redis\n'
        '- Edge Backend: Cloudflare Workers + D1 (SQLite)\n'
        '- Background Jobs: Celery + Redis\n'
        '- Deployment: Docker + Nginx + Cloudflare Pages'
    )
    pdf.sub_title('SymptoTrack PRD Requirements')
    pdf.body_text(
        '- Mobile apps (Android + iOS) - NOT IMPLEMENTED\n'
        '- WhatsApp Business API - NOT IMPLEMENTED\n'
        '- ABDM Sandbox integration - NOT IMPLEMENTED\n'
        '- FHIR R4 transformation layer - NOT IMPLEMENTED\n'
        '- OCR for prescription/report scanning - NOT IMPLEMENTED\n'
        '- Push notification service (FCM/APNS) - NOT IMPLEMENTED\n'
        '- AI/ML service for doctor assistant - NOT IMPLEMENTED\n'
        '- Speech-to-text engine - NOT IMPLEMENTED'
    )

    # ====== KEY INSIGHTS ======
    pdf.section_title('13. Key Insights')
    pdf.body_text(
        '1. Your platform is MORE COMPREHENSIVE (billing, appointments, multi-role dashboards) '
        'than what SymptoTrack PRD describes.'
    )
    pdf.body_text(
        '2. SymptoTrack is MORE FOCUSED on the prescription > reminder > follow-up workflow, '
        'which is the core patient-doctor loop.'
    )
    pdf.body_text(
        '3. SymptoTrack is INDIA-SPECIFIC (ABDM, DPDP, NMC compliance), while your current '
        'platform is built as a generic healthcare solution.'
    )
    pdf.body_text(
        '4. Your existing FOUNDATION IS STRONG (database, auth, RBAC) and can be extended, '
        'but mobile-first features and AI are completely absent.'
    )
    pdf.body_text(
        '5. SymptoTrack emphasizes AUTOMATION (AI suggestions, auto-reminders), while your '
        'platform is primarily a manual workflow system.'
    )

    # ====== PRIORITY ROADMAP ======
    pdf.add_page()
    pdf.section_title('14. Priority Roadmap')

    pdf.sub_title('Phase 1: Critical Gaps for MVP (8-10 weeks)')
    pdf.add_table(
        ['#', 'Task', 'Effort', 'Impact'],
        [
            ['1', 'Smart Reminder System (auto from Rx)', '3 weeks', 'CRITICAL'],
            ['2', 'Mobile Apps (Flutter / React Native)', '4 weeks', 'CRITICAL'],
            ['3', 'Basic ABHA / ABDM Linking', '2 weeks', 'CRITICAL'],
            ['4', 'Digital Signature (PIN-protected)', '1 week', 'HIGH'],
            ['5', 'Prescription PDF with Letterhead', '1 week', 'HIGH'],
        ],
        col_widths=[10, 85, 30, 65]
    )

    pdf.sub_title('Phase 2: Compliance & AI (6-8 weeks)')
    pdf.add_table(
        ['#', 'Task', 'Effort', 'Impact'],
        [
            ['6', 'FHIR R4 Mapping for Rx and Reports', '2 weeks', 'HIGH'],
            ['7', 'Doctor AI Assistant (Drug Interactions)', '3 weeks', 'HIGH'],
            ['8', 'DPDP Consent Management Flows', '2 weeks', 'HIGH'],
            ['9', 'NMC Auto-Verification', '1 week', 'MEDIUM'],
            ['10', 'Data Erasure Request Workflow', '1 week', 'MEDIUM'],
        ],
        col_widths=[10, 85, 30, 65]
    )

    pdf.sub_title('Phase 3: Enhancement (4-6 weeks)')
    pdf.add_table(
        ['#', 'Task', 'Effort', 'Impact'],
        [
            ['11', 'Patient Health Timeline UI', '2 weeks', 'MEDIUM'],
            ['12', 'Lab Report Linking to Prescriptions', '1 week', 'MEDIUM'],
            ['13', 'Multi-Channel Notifications + WhatsApp', '2 weeks', 'MEDIUM'],
            ['14', 'Trend Analysis for Repeated Tests', '1 week', 'LOW'],
            ['15', 'Admin Compliance Dashboard + Reports', '2 weeks', 'MEDIUM'],
        ],
        col_widths=[10, 85, 30, 65]
    )

    # ====== RECOMMENDATION ======
    pdf.ln(6)
    pdf.section_title('15. Final Recommendation')
    pdf.body_text(
        'OPTION A: Pivot fully to SymptoTrack vision - rebuild as a mobile-first, '
        'prescription-centric, ABDM-compliant platform. This requires significant rework '
        'but aligns with the Indian healthcare ecosystem requirements.\n\n'
        'OPTION B (Recommended): Integrate the missing critical features (reminders, AI, ABDM, '
        'mobile apps) into the existing comprehensive platform. Your current foundation in '
        'authentication, RBAC, billing, appointments, and database design is solid and can be '
        'extended. This approach preserves existing work while closing the gaps identified in '
        'the SymptoTrack PRD.\n\n'
        'Estimated total effort to reach SymptoTrack PRD parity: 18-24 weeks with a team of '
        '2-3 developers + 1 mobile developer.'
    )

    # Save
    output_path = r'c:\Users\tejas\friendlyhealthy\friendlyhealthy\SymptoTrack_vs_Current_Implementation_Gap_Analysis.pdf'
    pdf.output(output_path)
    print(f'PDF saved to: {output_path}')


if __name__ == '__main__':
    generate()
