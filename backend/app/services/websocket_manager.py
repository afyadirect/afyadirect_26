# app/services/websocket_manager.py
from fastapi import WebSocket
from typing import Dict, Set
import json
import asyncio
from datetime import datetime
from .firebase_service import FirebaseService
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_rooms: Dict[str, Set[str]] = {}  # user_id -> set of room_ids
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected")
        
        # Send pending offline messages
        await self._send_offline_messages(user_id)
    
    def disconnect(self, user_id: str):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected")
    
    async def join_room(self, user_id: str, room_id: str):
        """Join a chat room (appointment room)"""
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()
        self.user_rooms[user_id].add(room_id)
    
    async def leave_room(self, user_id: str, room_id: str):
        """Leave a chat room"""
        if user_id in self.user_rooms:
            self.user_rooms[user_id].discard(room_id)
    
    async def send_to_user(self, user_id: str, data: dict):
        """Send message to specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(data)
                return True
            except Exception as e:
                logger.error(f"Failed to send to user {user_id}: {e}")
                # Store message for offline delivery
                await self._store_offline_message(user_id, data)
        else:
            # Store message for offline delivery
            await self._store_offline_message(user_id, data)
        return False
    
    async def send_to_room(self, room_id: str, data: dict, exclude_user: str = None):
        """Send message to all users in a room"""
        for user_id, rooms in self.user_rooms.items():
            if room_id in rooms and user_id != exclude_user:
                await self.send_to_user(user_id, data)
    
    async def handle_message(self, user_id: str, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'chat':
                await self._handle_chat_message(user_id, data)
            elif message_type == 'typing':
                await self._handle_typing_indicator(user_id, data)
            elif message_type == 'join_room':
                await self.join_room(user_id, data.get('room_id'))
            elif message_type == 'leave_room':
                await self.leave_room(user_id, data.get('room_id'))
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from user {user_id}: {message}")
        except Exception as e:
            logger.error(f"Error handling message from {user_id}: {e}")
    
    async def _handle_chat_message(self, user_id: str, data: dict):
        """Save and broadcast chat message"""
        room_id = data.get('room_id')
        message_text = data.get('message')
        
        if not room_id or not message_text:
            return
        
        # Get appointment details
        appointment = await FirebaseService.get_appointment(room_id)
        if not appointment:
            return
        
        # Determine receiver
        if user_id == appointment['patientId']:
            receiver_id = appointment['doctorId']
        else:
            receiver_id = appointment['patientId']
        
        # Save message to Firestore
        message_data = {
            'appointmentId': room_id,
            'senderId': user_id,
            'receiverId': receiver_id,
            'message': message_text,
            'type': 'text',
            'sentAt': firestore.SERVER_TIMESTAMP,
            'isRead': False
        }
        
        await FirebaseService.send_message(message_data)
        
        # Broadcast to room
        await self.send_to_room(room_id, {
            'type': 'chat',
            'message': message_text,
            'sender_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Send push notification to receiver
        if receiver_id not in self.active_connections:
            from .notification_service import NotificationService
            await NotificationService.send_push_notification(
                user_id=receiver_id,
                title="New Message",
                body=f"You have a new message from your doctor/patient"
            )
    
    async def _handle_typing_indicator(self, user_id: str, data: dict):
        """Handle typing indicator"""
        room_id = data.get('room_id')
        is_typing = data.get('is_typing', False)
        
        await self.send_to_room(room_id, {
            'type': 'typing',
            'user_id': user_id,
            'is_typing': is_typing
        }, exclude_user=user_id)
    
    async def _store_offline_message(self, user_id: str, data: dict):
        """Store message for offline delivery"""
        # Store in Redis or Firestore for offline delivery
        offline_ref = FirebaseService.get_db().collection('offline_messages').document()
        offline_ref.set({
            'userId': user_id,
            'data': data,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
    
    async def _send_offline_messages(self, user_id: str):
        """Send pending offline messages to user"""
        offline_messages = FirebaseService.get_db().collection('offline_messages')\
            .where('userId', '==', user_id)\
            .get()
        
        for msg in offline_messages:
            data = msg.to_dict().get('data')
            await self.send_to_user(user_id, data)
            # Delete after sending
            msg.reference.delete()

# Global instance
websocket_manager = WebSocketManager()