# app/models/payment.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class PaymentMethod(str, Enum):
    MPESA = "mpesa"
    TIGO = "tigo"
    AIRTEL = "airtel"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class Payment(BaseModel):
    id: str
    userId: str
    appointmentId: str
    amount: float
    paymentMethod: PaymentMethod
    transactionId: Optional[str] = None
    status: PaymentStatus = PaymentStatus.PENDING
    mpesaCheckoutRequestID: Optional[str] = None
    failureReason: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    paidAt: Optional[datetime] = None