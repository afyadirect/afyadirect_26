# app/schemas/payment.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..models.payment import PaymentMethod, PaymentStatus

class PaymentCreate(BaseModel):
    appointment_id: str
    amount: float
    payment_method: PaymentMethod
    phone_number: str

class PaymentResponse(BaseModel):
    id: str
    appointment_id: str
    amount: float
    payment_method: str
    status: str
    transaction_id: Optional[str]
    created_at: datetime
    paid_at: Optional[datetime]

class PaymentCallback(BaseModel):
    Body: dict

class MpesaCallbackData(BaseModel):
    ResultCode: str
    ResultDesc: str
    CheckoutRequestID: str
    CallbackMetadata: Optional[dict]