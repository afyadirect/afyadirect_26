# app/routers/chat.py
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import List
from ..services.firebase_service import FirebaseService
from ..services.websocket_manager import websocket_manager
from ..schemas.common import SuccessResponse
from ..dependencies import get_current_user

router = APIRouter()

@router.get("/messages/{appointment_id}")
async def get_chat_messages(
    appointment_id: str,
    current_user: dict = Depends(get_current_user),
    limit: int = 100
):
    """Get chat messages for an appointment"""
    try:
        # Verify user is part of the appointment
        appointment = await FirebaseService.get_appointment(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        if (current_user['user_id'] not in [appointment['patientId'], appointment['doctorId']] 
            and current_user['role'] != 'admin'):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        messages = await FirebaseService.get_messages(appointment_id, limit)
        return {"messages": messages}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages/{appointment_id}/read")
async def mark_messages_read(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark all messages as read for an appointment"""
    try:
        count = await FirebaseService.mark_messages_read(
            appointment_id,
            current_user['user_id']
        )
        return SuccessResponse(message=f"Marked {count} messages as read")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages/{appointment_id}/typing")
async def send_typing_indicator(
    appointment_id: str,
    is_typing: bool,
    current_user: dict = Depends(get_current_user)
):
    """Send typing indicator via WebSocket"""
    try:
        appointment = await FirebaseService.get_appointment(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Determine receiver
        receiver_id = appointment['doctorId'] if current_user['user_id'] == appointment['patientId'] else appointment['patientId']
        
        await websocket_manager.send_to_user(receiver_id, {
            'type': 'typing',
            'sender_id': current_user['user_id'],
            'is_typing': is_typing,
            'appointment_id': appointment_id
        })
        
        return SuccessResponse(message="Typing indicator sent")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.handle_message(user_id, data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id)