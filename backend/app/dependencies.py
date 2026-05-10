# app/dependencies.py (Updated)
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional
from .config import settings
from .services.firebase_service import FirebaseService

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        user_id = payload.get("sub")
        role = payload.get("role")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Verify user exists and is active
        user = await FirebaseService.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.get('isActive', True):
            raise HTTPException(status_code=403, detail="Account is disabled")
        
        return {
            "user_id": user_id,
            "role": role or user.get('role')
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    """Check if current user is admin"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def get_current_doctor(current_user: dict = Depends(get_current_user)):
    """Check if current user is doctor"""
    if current_user['role'] != 'doctor':
        raise HTTPException(status_code=403, detail="Doctor access required")
    return current_user

async def get_current_patient(current_user: dict = Depends(get_current_user)):
    """Check if current user is patient"""
    if current_user['role'] != 'patient':
        raise HTTPException(status_code=403, detail="Patient access required")
    return current_user

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get current user if authenticated, else return None"""
    if not credentials:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None