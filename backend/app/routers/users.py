# app/routers/users.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from ..services.firebase_service import FirebaseService
from ..schemas.user import UserResponse, UserUpdate, PatientProfileUpdate, DoctorProfileUpdate
from ..dependencies import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    try:
        user_data = await FirebaseService.get_user(current_user['user_id'])
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            uid=user_data['uid'],
            full_name=user_data['fullName'],
            email=user_data['email'],
            phone=user_data['phone'],
            role=user_data['role'],
            language=user_data.get('language', 'en'),
            is_active=user_data.get('isActive', True),
            profile_image=user_data.get('profileImage'),
            created_at=user_data['createdAt']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/me")
async def update_current_user_profile(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        update_dict = {}
        if update_data.full_name:
            update_dict['fullName'] = update_data.full_name
        if update_data.phone:
            update_dict['phone'] = update_data.phone
        if update_data.language:
            update_dict['language'] = update_data.language
        if update_data.fcm_token:
            update_dict['fcmToken'] = update_data.fcm_token
        if update_data.profile_image:
            update_dict['profileImage'] = update_data.profile_image
        
        await FirebaseService.update_user(current_user['user_id'], update_dict)
        return {"message": "Profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me/patient")
async def get_patient_profile(current_user: dict = Depends(get_current_user)):
    """Get patient profile"""
    try:
        if current_user['role'] != 'patient':
            raise HTTPException(status_code=403, detail="Only patients can access this")
        
        patient_data = await FirebaseService.get_patient(current_user['user_id'])
        if not patient_data:
            raise HTTPException(status_code=404, detail="Patient data not found")
        
        return patient_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/me/patient")
async def update_patient_profile(
    update_data: PatientProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update patient profile"""
    try:
        if current_user['role'] != 'patient':
            raise HTTPException(status_code=403, detail="Only patients can access this")
        
        update_dict = update_data.dict(exclude_unset=True)
        await FirebaseService.update_patient(current_user['user_id'], update_dict)
        return {"message": "Patient profile updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me/doctor")
async def get_doctor_profile(current_user: dict = Depends(get_current_user)):
    """Get doctor profile"""
    try:
        if current_user['role'] != 'doctor':
            raise HTTPException(status_code=403, detail="Only doctors can access this")
        
        doctor_data = await FirebaseService.get_doctor(current_user['user_id'])
        if not doctor_data:
            raise HTTPException(status_code=404, detail="Doctor data not found")
        
        return doctor_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/me/doctor")
async def update_doctor_profile(
    update_data: DoctorProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update doctor profile"""
    try:
        if current_user['role'] != 'doctor':
            raise HTTPException(status_code=403, detail="Only doctors can access this")
        
        update_dict = update_data.dict(exclude_unset=True)
        await FirebaseService.update_doctor(current_user['user_id'], update_dict)
        return {"message": "Doctor profile updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))