# app/dependencies.py (Updated)
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional
from .config import settings
from .services.firebase_service import FirebaseService
from firebase_admin import auth  # CRITICAL: Use Firebase Admin SDK
from .services.firebase_service import FirebaseService

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user via Firebase"""
    try:
        id_token = credentials.credentials
        # Verify the Firebase token directly with Firebase servers
        decoded_token = auth.verify_id_token(id_token)
        
        user_id = decoded_token.get("uid")
        
        # Fetch user profile from Firestore to get their Role
        user = await FirebaseService.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return {
            "user_id": user_id,
            "role": user.get('role'), # 'doctor', 'patient', or 'admin'
            "email": decoded_token.get("email")
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
    
    
    
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