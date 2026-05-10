# app/routers/__init__.py
from .auth import router as auth_router
from .users import router as users_router
from .appointments import router as appointments_router
from .doctors import router as doctors_router
from .payments import router as payments_router
from .chat import router as chat_router
from .prescriptions import router as prescriptions_router
from .admin import router as admin_router

__all__ = [
    'auth_router',
    'users_router',
    'appointments_router',
    'doctors_router',
    'payments_router',
    'chat_router',
    'prescriptions_router',
    'admin_router'
]