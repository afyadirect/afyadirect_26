# app/services/payment_service.py
import requests
import base64
import json
from datetime import datetime
from typing import Dict, Any, Optional
from ..config import settings
from .firebase_service import FirebaseService

class PaymentService:
    
    @classmethod
    async def process_mpesa_payment(
        cls, 
        phone_number: str, 
        amount: float, 
        appointment_id: str,
        patient_id: str
    ) -> Dict[str, Any]:
        """Process M-Pesa payment using STK Push"""
        try:
            # Format phone number (remove leading 0 or +255)
            if phone_number.startswith('0'):
                phone_number = '255' + phone_number[1:]
            elif phone_number.startswith('+'):
                phone_number = phone_number[1:]
            
            # Generate password
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password_str = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
            password = base64.b64encode(password_str.encode()).decode()
            
            # Prepare STK push request
            headers = {
                'Authorization': f'Bearer {await cls._get_mpesa_token()}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'BusinessShortCode': settings.MPESA_SHORTCODE,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': int(amount),
                'PartyA': phone_number,
                'PartyB': settings.MPESA_SHORTCODE,
                'PhoneNumber': phone_number,
                'CallBackURL': f"{settings.APP_URL}/api/v1/payments/mpesa-callback",
                'AccountReference': f"AFYA{appointment_id[:8]}",
                'TransactionDesc': f'AfyaDirect Consultation Payment'
            }
            
            # Make API request
            response = requests.post(
                'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
                headers=headers,
                json=payload
            )
            
            result = response.json()
            
            if result.get('ResponseCode') == '0':
                # Create payment record
                payment_id = await FirebaseService.create_payment({
                    'userId': patient_id,
                    'appointmentId': appointment_id,
                    'amount': amount,
                    'paymentMethod': 'mpesa',
                    'mpesaCheckoutRequestID': result.get('CheckoutRequestID'),
                    'status': 'pending'
                })
                
                return {
                    'success': True,
                    'payment_id': payment_id,
                    'checkout_request_id': result.get('CheckoutRequestID'),
                    'message': 'STK Push sent successfully'
                }
            else:
                return {
                    'success': False,
                    'message': result.get('ResponseDescription', 'Payment failed')
                }
                
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @classmethod
    async def _get_mpesa_token(cls) -> str:
        """Get M-Pesa OAuth token"""
        try:
            auth_str = f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}"
            auth_b64 = base64.b64encode(auth_str.encode()).decode()
            
            headers = {'Authorization': f'Basic {auth_b64}'}
            
            response = requests.get(
                'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials',
                headers=headers
            )
            
            result = response.json()
            return result.get('access_token')
            
        except Exception as e:
            raise Exception(f"Failed to get M-Pesa token: {str(e)}")
    
    @classmethod
    async def handle_mpesa_callback(cls, callback_data: Dict[str, Any]):
        """Handle M-Pesa STK Push callback"""
        try:
            body = callback_data.get('Body', {})
            stk_callback = body.get('stkCallback', {})
            
            result_code = stk_callback.get('ResultCode')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            
            # Find payment by checkout request ID
            payments = FirebaseService.get_db().collection('payments')\
                .where('mpesaCheckoutRequestID', '==', checkout_request_id)\
                .get()
            
            if not payments:
                return {'success': False, 'message': 'Payment not found'}
            
            payment = payments[0]
            payment_id = payment.id
            
            if result_code == '0':
                # Payment successful
                metadata = stk_callback.get('CallbackMetadata', {})
                items = metadata.get('Item', [])
                
                transaction_id = None
                amount = None
                
                for item in items:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        transaction_id = item.get('Value')
                    elif item.get('Name') == 'Amount':
                        amount = item.get('Value')
                
                # Update payment record
                await FirebaseService.update_payment(payment_id, {
                    'status': 'completed',
                    'transactionId': transaction_id,
                    'paidAt': firestore.SERVER_TIMESTAMP
                })
                
                # Update appointment payment status
                payment_data = payment.to_dict()
                await FirebaseService.update_appointment(
                    payment_data['appointmentId'],
                    {'paymentStatus': 'paid'}
                )
                
                # Send confirmation notification
                from .notification_service import NotificationService
                await NotificationService.send_payment_confirmation(
                    user_id=payment_data['userId'],
                    amount=amount,
                    transaction_id=transaction_id
                )
                
            else:
                # Payment failed
                await FirebaseService.update_payment(payment_id, {
                    'status': 'failed',
                    'failureReason': stk_callback.get('ResultDesc')
                })
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @classmethod
    async def process_tigo_payment(cls, phone_number: str, amount: float, appointment_id: str):
        """Process Tigo Pesa payment"""
        # Implement Tigo Pesa API integration
        # Similar to M-Pesa implementation
        pass
    
    @classmethod
    async def process_airtel_payment(cls, phone_number: str, amount: float, appointment_id: str):
        """Process Airtel Money payment"""
        # Implement Airtel Money API integration
        pass