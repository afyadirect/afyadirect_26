# app/services/notification_service.py
import requests
from typing import Dict, Any
from firebase_admin import messaging
from ..config import settings
from .firebase_service import FirebaseService
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    
    @classmethod
    async def send_push_notification(cls, user_id: str, title: str, body: str, data: Dict = None):
        """Send push notification to user using FCM"""
        try:
            # Get user's FCM token
            user_data = await FirebaseService.get_user(user_id)
            fcm_token = user_data.get('fcmToken')
            
            if not fcm_token:
                logger.warning(f"No FCM token for user {user_id}")
                return
            
            # Create message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=fcm_token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        channel_id='afyadirect_channel'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default'
                        )
                    )
                )
            )
            
            # Send message
            response = messaging.send(message)
            logger.info(f"Push notification sent: {response}")
            
            # Store notification in Firestore
            await FirebaseService.create_notification(
                user_id=user_id,
                title=title,
                message=body,
                notification_type=data.get('type', 'general') if data else 'general'
            )
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
    
    @classmethod
    async def send_sms(cls, phone_number: str, message: str):
        """Send SMS using Africa's Talking"""
        try:
            # Format phone number
            if not phone_number.startswith('+'):
                phone_number = f"+{phone_number}"
            
            # Make API request to Africa's Talking
            response = requests.post(
                'https://api.africastalking.com/version1/messaging',
                headers={
                    'apiKey': settings.AT_API_KEY,
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                },
                data={
                    'username': settings.AT_USERNAME,
                    'to': phone_number,
                    'message': message,
                    'from': settings.AT_SENDER_ID
                }
            )
            
            result = response.json()
            logger.info(f"SMS sent to {phone_number}: {result}")
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
    
    @classmethod
    async def send_email(cls, to_email: str, subject: str, html_content: str):
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
                    'from': {'email': settings.SENDGRID_FROM_EMAIL},
                    'subject': subject,
                    'content': [{'type': 'text/html', 'value': html_content}]
                }
            )
            
            if response.status_code == 202:
                logger.info(f"Email sent to {to_email}")
            else:
                logger.error(f"Failed to send email: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
    
    @classmethod
    async def send_appointment_created(cls, patient_id: str, doctor_id: str, appointment_id: str):
        """Send notifications when appointment is created"""
        # Get user details
        patient = await FirebaseService.get_user(patient_id)
        doctor = await FirebaseService.get_user(doctor_id)
        
        # Send push notification to doctor
        await cls.send_push_notification(
            user_id=doctor_id,
            title="New Appointment Request",
            body=f"Dr. {doctor.get('fullName')}, you have a new appointment request from {patient.get('fullName')}",
            data={'type': 'appointment', 'appointment_id': appointment_id}
        )
        
        # Send SMS to patient
        await cls.send_sms(
            phone_number=patient.get('phone'),
            message=f"AfyaDirect: Your appointment request has been sent to Dr. {doctor.get('fullName')}. We'll notify you once confirmed."
        )
    
    @classmethod
    async def send_appointment_accepted(cls, patient_id: str, doctor_id: str, appointment_id: str):
        """Send notifications when appointment is accepted"""
        patient = await FirebaseService.get_user(patient_id)
        doctor = await FirebaseService.get_user(doctor_id)
        
        # Send push notification to patient
        await cls.send_push_notification(
            user_id=patient_id,
            title="Appointment Confirmed",
            body=f"Your appointment with Dr. {doctor.get('fullName')} has been confirmed",
            data={'type': 'appointment', 'appointment_id': appointment_id}
        )
        
        # Send email confirmation
        await cls.send_email(
            to_email=patient.get('email'),
            subject="Appointment Confirmation - AfyaDirect",
            html_content=f"""
            <h2>Appointment Confirmed</h2>
            <p>Dear {patient.get('fullName')},</p>
            <p>Your appointment with Dr. {doctor.get('fullName')} has been confirmed.</p>
            <p>You can now proceed to the chat section to start your consultation.</p>
            <br>
            <p>Best regards,<br>AfyaDirect Team</p>
            """
        )
    
    @classmethod
    async def send_payment_confirmation(cls, user_id: str, amount: float, transaction_id: str):
        """Send payment confirmation notification"""
        user = await FirebaseService.get_user(user_id)
        
        # Send push notification
        await cls.send_push_notification(
            user_id=user_id,
            title="Payment Successful",
            body=f"Your payment of TZS {amount:,.0f} has been processed successfully. Transaction ID: {transaction_id}",
            data={'type': 'payment', 'transaction_id': transaction_id}
        )
        
        # Send SMS receipt
        await cls.send_sms(
            phone_number=user.get('phone'),
            message=f"AfyaDirect: Payment of TZS {amount:,.0f} received. Transaction ID: {transaction_id}. Thank you for using AfyaDirect!"
        )