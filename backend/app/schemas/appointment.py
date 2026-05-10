# app/schemas/appointment.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from ..models.appointment import AppointmentStatus, ConsultationType, PaymentStatus

class AppointmentCreate(BaseModel):
    doctor_id: str
    appointment_date: datetime
    symptoms: Optional[str] = None
    consultation_type: ConsultationType = ConsultationType.CHAT
    fee: Optional[float] = None
    
    @validator('appointment_date')
    def validate_appointment_date(cls, v):
        if v < datetime.utcnow():
            raise ValueError('Appointment date must be in the future')
        return v

class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    symptoms: Optional[str] = None
    cancellation_reason: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    appointment_date: datetime
    appointment_time: str
    status: str
    symptoms: Optional[str]
    consultation_type: str
    fee: float
    payment_status: str
    created_at: datetime
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None

class AppointmentListResponse(BaseModel):
    appointments: list[AppointmentResponse]
    total: int