# app/schemas/__init__.py
from .user import UserCreate, UserUpdate, UserResponse, UserLogin, TokenResponse
from .appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from .payment import PaymentCreate, PaymentResponse, PaymentCallback
from .common import ErrorResponse, SuccessResponse

__all__ = [
    'UserCreate', 'UserUpdate', 'UserResponse', 'UserLogin', 'TokenResponse',
    'AppointmentCreate', 'AppointmentUpdate', 'AppointmentResponse',
    'PaymentCreate', 'PaymentResponse', 'PaymentCallback',
    'ErrorResponse', 'SuccessResponse'
]