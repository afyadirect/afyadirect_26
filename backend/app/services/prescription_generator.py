# app/services/prescription_generator.py
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from ..services.firebase_service import FirebaseService
import os

class PrescriptionGenerator:
    @classmethod
    async def generate_pdf(cls, prescription_data: dict) -> str:
        """Generate a PDF prescription and upload to Firebase Storage"""
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0EA5E9'),
            alignment=1,
            spaceAfter=30
        )
        
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12
        )
        
        # Header
        story.append(Paragraph("AfyaDirect Medical Prescription", title_style))
        story.append(Spacer(1, 12))
        
        # Date
        story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Doctor and Patient Information
        doctor = await FirebaseService.get_user(prescription_data.get('doctor_id'))
        patient = await FirebaseService.get_user(prescription_data.get('patient_id'))
        
        doctor_name = doctor.get('fullName', 'Unknown') if doctor else 'Unknown'
        patient_name = patient.get('fullName', 'Unknown') if patient else 'Unknown'
        
        info_data = [
            ['Doctor:', doctor_name],
            ['Specialty:', prescription_data.get('doctor_specialty', 'N/A')],
            ['Patient:', patient_name],
            ['Patient ID:', prescription_data.get('patient_id', 'N/A')],
        ]
        
        info_table = Table(info_data, colWidths=[1.5*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Medicines Table
        story.append(Paragraph("Medication", header_style))
        
        medicines = prescription_data.get('medicines', [])
        medicine_data = [['Medicine', 'Dosage', 'Frequency', 'Duration']]
        
        for med in medicines:
            medicine_data.append([
                med.get('name', ''),
                med.get('dosage', ''),
                med.get('frequency', ''),
                med.get('duration', '')
            ])
        
        medicine_table = Table(medicine_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        medicine_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0EA5E9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(medicine_table)
        story.append(Spacer(1, 20))
        
        # Instructions
        story.append(Paragraph("Instructions", header_style))
        story.append(Paragraph(prescription_data.get('instructions', 'Take as prescribed'), styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Notes
        if prescription_data.get('notes'):
            story.append(Paragraph("Additional Notes", header_style))
            story.append(Paragraph(prescription_data.get('notes'), styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Footer
        story.append(Spacer(1, 40))
        story.append(Paragraph("Doctor's Signature: ___________________", styles['Normal']))
        story.append(Spacer(1, 10))
        story.append(Paragraph("This is a computer-generated prescription. No signature required.", 
                              ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray)))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Upload to Firebase Storage
        file_name = f"prescriptions/{prescription_data.get('appointment_id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_url = await FirebaseService.upload_file(
            buffer.getvalue(),
            file_name,
            'application/pdf'
        )
        
        return pdf_url