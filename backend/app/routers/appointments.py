# app/routers/appointments.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
from ..services.firebase_service import FirebaseService
from ..services.notification_service import NotificationService
from ..schemas.appointment import (
    AppointmentCreate, AppointmentUpdate, 
    AppointmentResponse, AppointmentListResponse
)
from ..dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new appointment"""
    try:
        # Verify patient role
        if current_user['role'] != 'patient':
            raise HTTPException(status_code=403, detail="Only patients can create appointments")
        
        # Get doctor details
        doctor_data = await FirebaseService.get_user(appointment_data.doctor_id)
        if not doctor_data or doctor_data.get('role') != 'doctor':
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        # Create appointment
        appointment_dict = appointment_data.dict()
        appointment_dict['patientId'] = current_user['user_id']
        appointment_dict['fee'] = appointment_data.fee or 25000  # Default fee
        
        appointment_id = await FirebaseService.create_appointment(appointment_dict)
        
        # Send notifications
        await NotificationService.send_appointment_created(
            patient_id=current_user['user_id'],
            doctor_id=appointment_data.doctor_id,
            appointment_id=appointment_id
        )
        
        # Get created appointment
        appointment = await FirebaseService.get_appointment(appointment_id)
        
        return AppointmentResponse(**appointment)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[AppointmentResponse])
async def get_user_appointments(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get appointments for current user"""
    try:
        appointments = await FirebaseService.list_appointments(
            user_id=current_user['user_id'],
            role=current_user['role'],
            status=status
        )
        
        return [AppointmentResponse(**apt) for apt in appointments]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific appointment details"""
    try:
        appointment = await FirebaseService.get_appointment(appointment_id)
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Check authorization
        if (current_user['role'] == 'patient' and appointment['patientId'] != current_user['user_id']) or \
           (current_user['role'] == 'doctor' and appointment['doctorId'] != current_user['user_id']) and \
           current_user['role'] != 'admin':
            raise HTTPException(status_code=403, detail="Not authorized")
        
        return AppointmentResponse(**appointment)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{appointment_id}")
async def update_appointment_status(
    appointment_id: str,
    update_data: AppointmentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update appointment status"""
    try:
        appointment = await FirebaseService.get_appointment(appointment_id)
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Check authorization
        if current_user['role'] == 'patient' and appointment['patientId'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Not authorized")
        elif current_user['role'] == 'doctor' and appointment['doctorId'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Update appointment
        update_dict = update_data.dict(exclude_unset=True)
        
        # Add additional fields for specific status changes
        if update_dict.get('status') == 'accepted':
            update_dict['acceptedAt'] = firestore.SERVER_TIMESTAMP
            await NotificationService.send_appointment_accepted(
                patient_id=appointment['patientId'],
                doctor_id=appointment['doctorId'],
                appointment_id=appointment_id
            )
        elif update_dict.get('status') == 'completed':
            update_dict['completedAt'] = firestore.SERVER_TIMESTAMP
        elif update_dict.get('status') == 'cancelled':
            update_dict['cancelledAt'] = firestore.SERVER_TIMESTAMP
        
        await FirebaseService.update_appointment(appointment_id, update_dict)
        
        return {"message": "Appointment updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{appointment_id}/start")
async def start_consultation(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Start a consultation (video/chat)"""
    try:
        appointment = await FirebaseService.get_appointment(appointment_id)
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Verify user is part of the appointment
        if current_user['user_id'] not in [appointment['patientId'], appointment['doctorId']]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Check if appointment is ready
        if appointment['status'] != 'confirmed':
            raise HTTPException(status_code=400, detail="Appointment not confirmed yet")
        
        # Update started time
        await FirebaseService.update_appointment(appointment_id, {
            'startedAt': firestore.SERVER_TIMESTAMP,
            'status': 'in_progress'
        })
        
        # Generate video call token if needed
        video_token = None
        if appointment.get('consultationType') == 'video':
            from ..services.video_service import VideoService
            video_token = VideoService.generate_token(appointment_id, current_user['user_id'])
        
        return {
            "message": "Consultation started",
            "consultation_type": appointment.get('consultationType'),
            "video_token": video_token
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))