# app/services/firebase_service.py
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from ..config import settings
from firebase_admin import credentials, firestore, initialize_app
from google.cloud import firestore as google_firestore
class FirebaseService:
    _initialized = False
    _db = None
    _bucket = None
    
    @classmethod
    async def initialize(cls):
        """Initialize Firebase Admin SDK"""
        if not cls._initialized:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred, {
                'storageBucket': settings.FIREBASE_STORAGE_BUCKET
            })
            cls._db = firestore.client()
            cls._bucket = storage.bucket()
            cls._initialized = True
    
    @classmethod
    def get_db(cls):
        """Get Firestore client"""
        if not cls._initialized:
            raise Exception("Firebase not initialized")
        return cls._db
    
    @classmethod
    def get_bucket(cls):
        """Get Storage bucket"""
        if not cls._initialized:
            raise Exception("Firebase not initialized")
        return cls._bucket
    
    # User Management
    @classmethod
    async def create_user(cls, email: str, password: str, user_data: Dict[str, Any]):
        """Create a new user in Firebase Auth and Firestore"""
        try:
            # Create user in Firebase Auth
            user = auth.create_user(
                email=email,
                password=password,
                email_verified=False,
                disabled=False
            )
            
            # Add user data to Firestore
            user_ref = cls._db.collection('users').document(user.uid)
            user_ref.set({
                'uid': user.uid,
                'email': email,
               'createdAt': google_firestore.SERVER_TIMESTAMP, # Use google_firestore here
    'updatedAt': google_firestore.SERVER_TIMESTAMP,
                **user_data
            })
            
            return user.uid
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")
    
    @classmethod
    async def get_user(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data from Firestore"""
        try:
            user_doc = cls._db.collection('users').document(user_id).get()
            if user_doc.exists:
                return user_doc.to_dict()
            return None
        except Exception as e:
            raise Exception(f"Failed to get user: {str(e)}")
    
    @classmethod
    async def update_user(cls, user_id: str, data: Dict[str, Any]):
        """Update user data in Firestore"""
        try:
            data['updatedAt'] = google_firestore.SERVER_TIMESTAMP
            cls._db.collection('users').document(user_id).update(data)
            return True
        except Exception as e:
            raise Exception(f"Failed to update user: {str(e)}")
    
    # Appointment Management
    @classmethod
    async def create_appointment(cls, appointment_data: Dict[str, Any]) -> str:
        """Create a new appointment"""
        try:
            appointment_ref = cls._db.collection('appointments').document()
            appointment_data.update({
                'id': appointment_ref.id,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'updatedAt': firestore.SERVER_TIMESTAMP,
                'status': 'pending'
            })
            appointment_ref.set(appointment_data)
            return appointment_ref.id
        except Exception as e:
            raise Exception(f"Failed to create appointment: {str(e)}")
    
    @classmethod
    async def get_appointment(cls, appointment_id: str) -> Optional[Dict[str, Any]]:
        """Get appointment details"""
        try:
            appointment_doc = cls._db.collection('appointments').document(appointment_id).get()
            if appointment_doc.exists:
                return appointment_doc.to_dict()
            return None
        except Exception as e:
            raise Exception(f"Failed to get appointment: {str(e)}")
    
    @classmethod
    async def update_appointment(cls, appointment_id: str, data: Dict[str, Any]):
        """Update appointment status or details"""
        try:
            data['updatedAt'] = google_firestore.SERVER_TIMESTAMP
            cls._db.collection('appointments').document(appointment_id).update(data)
            return True
        except Exception as e:
            raise Exception(f"Failed to update appointment: {str(e)}")
    
    @classmethod
    async def list_appointments(
        cls, 
        user_id: str, 
        role: str, 
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List appointments for a user"""
        try:
            collection = cls._db.collection('appointments')
            
            if role == 'patient':
                query = collection.where('patientId', '==', user_id)
            elif role == 'doctor':
                query = collection.where('doctorId', '==', user_id)
            else:
                query = collection
            
            if status:
                query = query.where('status', '==', status)
            
            appointments = query.order_by('appointmentDate', direction=firestore.Query.DESCENDING).get()
            
            return [doc.to_dict() for doc in appointments]
        except Exception as e:
            raise Exception(f"Failed to list appointments: {str(e)}")
    
    @classmethod
    async def update_doctor_profile(cls, user_id: str, update_data: Dict[str, Any]):
        try:
            # Ensure there is code indented here!
            update_dict = update_data.dict(exclude_unset=True)
            await cls._db.collection('doctors').document(user_id).update(update_dict)
        except Exception as e:
            raise Exception(f"Failed to update doctor: {str(e)}")
    
    
    
    # Chat Messages
    @classmethod
    async def send_message(cls, message_data: Dict[str, Any]) -> str:
        """Send a chat message"""
        try:
            message_ref = cls._db.collection('chat_messages').document()
            message_data.update({
                'id': message_ref.id,
                'sentAt': google_firestore.SERVER_TIMESTAMP,
                'isRead': False
            })
            message_ref.set(message_data)
            return message_ref.id
        except Exception as e:
            raise Exception(f"Failed to send message: {str(e)}")
    
    @classmethod
    async def get_messages(cls, appointment_id: str) -> List[Dict[str, Any]]:
        """Get all messages for an appointment"""
        try:
            messages = cls._db.collection('chat_messages')\
                .where('appointmentId', '==', appointment_id)\
                .order_by('sentAt')\
                .get()
            return [msg.to_dict() for msg in messages]
        except Exception as e:
            raise Exception(f"Failed to get messages: {str(e)}")
    
    @classmethod
    async def mark_messages_read(cls, appointment_id: str, user_id: str):
        """Mark messages as read"""
        try:
            messages = cls._db.collection('chat_messages')\
                .where('appointmentId', '==', appointment_id)\
                .where('receiverId', '==', user_id)\
                .where('isRead', '==', False)\
                .get()
            
            for msg in messages:
                msg.reference.update({'isRead': True})
            
            return len(messages)
        except Exception as e:
            raise Exception(f"Failed to mark messages: {str(e)}")
    
    # Payment Management
    @classmethod
    async def create_payment(cls, payment_data: Dict[str, Any]) -> str:
        """Create a payment record"""
        try:
            payment_ref = cls._db.collection('payments').document()
            payment_data.update({
                'id': payment_ref.id,
                'createdAt': google_firestore.SERVER_TIMESTAMP,
                'status': 'pending'
            })
            payment_ref.set(payment_data)
            return payment_ref.id
        except Exception as e:
            raise Exception(f"Failed to create payment: {str(e)}")
    
    @classmethod
    async def update_payment(cls, payment_id: str, data: Dict[str, Any]):
        """Update payment status"""
        try:
            data['updatedAt'] = google_firestore.SERVER_TIMESTAMP
            cls._db.collection('payments').document(payment_id).update(data)
            return True
        except Exception as e:
            raise Exception(f"Failed to update payment: {str(e)}")
    
    # File Upload
    @classmethod
    async def upload_file(cls, file_data: bytes, file_name: str, content_type: str) -> str:
        """Upload a file to Firebase Storage"""
        try:
            blob = cls._bucket.blob(f"uploads/{file_name}")
            blob.upload_from_string(file_data, content_type=content_type)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    # Notifications
    @classmethod
    async def create_notification(cls, user_id: str, title: str, message: str, notification_type: str):
        """Create a notification for a user"""
        try:
            notification_ref = cls._db.collection('notifications').document()
            notification_ref.set({
                'id': notification_ref.id,
                'userId': user_id,
                'title': title,
                'message': message,
                'type': notification_type,
                'isRead': False,
                'createdAt': google_firestore.SERVER_TIMESTAMP
            })
            return notification_ref.id
        except Exception as e:
            raise Exception(f"Failed to create notification: {str(e)}")
    
    @classmethod
    async def get_notifications(cls, user_id: str) -> List[Dict[str, Any]]:
        """Get user notifications"""
        try:
            notifications = cls._db.collection('notifications')\
                .where('userId', '==', user_id)\
                .order_by('createdAt', direction=google_firestore.Query.DESCENDING)\
                .limit(50)\
                .get()
            return [notif.to_dict() for notif in notifications]
        except Exception as e:
            raise Exception(f"Failed to get notifications: {str(e)}")