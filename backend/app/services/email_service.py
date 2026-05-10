# app/services/email_service.py
import requests
from typing import Dict, Any, List
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    @classmethod
    async def send_email(cls, to_email: str, subject: str, html_content: str, 
                         from_email: str = None) -> Dict[str, Any]:
        """Send email using SendGrid"""
        try:
            response = requests.post(
                'https://api.sendgrid.com/v3/mail/send',
                headers={
                    'Authorization': f'Bearer {settings.SENDGRID_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'personalizations': [{'to': [{'email': to_email}]}],
                    'from': {'email': from_email or settings.SENDGRID_FROM_EMAIL},
                    'subject': subject,
                    'content': [{'type': 'text/html', 'value': html_content}]
                },
                timeout=10
            )
            
            if response.status_code == 202:
                logger.info(f"Email sent to {to_email}")
                return {'success': True, 'message': 'Email sent successfully'}
            else:
                logger.error(f"Failed to send email: {response.text}")
                return {'success': False, 'message': response.text}
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {'success': False, 'message': str(e)}
    
    @classmethod
    async def send_welcome_email(cls, to_email: str, name: str, role: str):
        """Send welcome email to new user"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0EA5E9; padding: 20px; text-align: center; color: white; }}
                .content {{ padding: 20px; }}
                .button {{ background-color: #0EA5E9; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to AfyaDirect!</h1>
                </div>
                <div class="content">
                    <h2>Hello {name},</h2>
                    <p>Thank you for joining AfyaDirect! We're excited to have you on board.</p>
                    <p>You have registered as a <strong>{role}</strong> on our platform.</p>
                    
                    {"<p>As a patient, you can:</p><ul><li>Book consultations with top doctors</li><li>Chat with your doctor in real-time</li><li>View your medical history and prescriptions</li><li>Make secure payments</li></ul>" if role == "patient" else ""}
                    
                    {"<p>As a doctor, you can:</p><ul><li>Manage your appointments</li><li>Chat with patients</li><li>Write prescriptions</li><li>Track your earnings</li></ul>" if role == "doctor" else ""}
                    
                    <p>Get started by logging into your account and exploring the platform.</p>
                    
                    <a href="https://afyadirect.com/login" class="button">Login to Your Account</a>
                </div>
                <div class="footer">
                    <p>&copy; 2024 AfyaDirect. All rights reserved.</p>
                    <p>Your Health, Our Priority</p>
                </div>
            </div>
        </body>
        </html>
        """
        return await cls.send_email(to_email, f"Welcome to AfyaDirect, {name}!", html_content)
    
    @classmethod
    async def send_appointment_confirmation(cls, to_email: str, patient_name: str,
                                            doctor_name: str, appointment_date: str):
        """Send appointment confirmation email"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0EA5E9; padding: 20px; text-align: center; color: white; }}
                .content {{ padding: 20px; }}
                .appointment-details {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Appointment Confirmed!</h1>
                </div>
                <div class="content">
                    <h2>Dear {patient_name},</h2>
                    <p>Your appointment has been confirmed. Here are the details:</p>
                    
                    <div class="appointment-details">
                        <p><strong>Doctor:</strong> Dr. {doctor_name}</p>
                        <p><strong>Date & Time:</strong> {appointment_date}</p>
                        <p><strong>Platform:</strong> AfyaDirect</p>
                    </div>
                    
                    <p>Please log in to your account before the appointment time to start your consultation.</p>
                    
                    <a href="https://afyadirect.com/login" class="button">Go to Dashboard</a>
                </div>
                <div class="footer">
                    <p>&copy; 2024 AfyaDirect. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return await cls.send_email(to_email, "Appointment Confirmed - AfyaDirect", html_content)