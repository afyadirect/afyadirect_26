# app/models/appointment.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class ConsultationType(str, Enum):
    CHAT = "chat"
    VIDEO = "video"
    VOICE = "voice"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"

class Appointment(BaseModel):
    id: str
    patientId: str
    doctorId: str
    appointmentDate: datetime
    appointmentTime: str
    status: AppointmentStatus = AppointmentStatus.PENDING
    symptoms: Optional[str] = None
    consultationType: ConsultationType = ConsultationType.CHAT
    fee: float
    paymentStatus: PaymentStatus = PaymentStatus.PENDING
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    startedAt: Optional[datetime] = None
    endedAt: Optional[datetime] = None
    acceptedAt: Optional[datetime] = None
    cancelledAt: Optional[datetime] = None
    cancellationReason: Optional[str] = None