# app/services/sms_service.py
import requests
from typing import Dict, Any
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class SMSService:
    @classmethod
    async def send_sms(cls, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS using Africa's Talking"""
        try:
            # Format phone number
            if not phone_number.startswith('+'):
                phone_number = f"+{phone_number}"
            
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
                },
                timeout=10
            )
            
            result = response.json()
            logger.info(f"SMS sent to {phone_number}: {result}")
            
            return {
                'success': True,
                'message': 'SMS sent successfully',
                'data': result
            }
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    @classmethod
    async def send_appointment_reminder(cls, phone_number: str, patient_name: str, 
                                         doctor_name: str, appointment_date: str):
        """Send appointment reminder SMS"""
        message = f"AfyaDirect: Reminder - Your appointment with Dr. {doctor_name} on {appointment_date}. Please be on time. Thank you!"
        return await cls.send_sms(phone_number, message)
    
    @classmethod
    async def send_payment_confirmation(cls, phone_number: str, amount: float, 
                                        transaction_id: str):
        """Send payment confirmation SMS"""
        message = f"AfyaDirect: Payment of TZS {amount:,.0f} received. Transaction ID: {transaction_id}. Thank you for using AfyaDirect!"
        return await cls.send_sms(phone_number, message)
    
    @classmethod
    async def send_verification_code(cls, phone_number: str, code: str):
        """Send verification code SMS"""
        message = f"AfyaDirect: Your verification code is {code}. Valid for 10 minutes."
        return await cls.send_sms(phone_number, message)