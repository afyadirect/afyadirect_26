# app/routers/doctors.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from ..services.firebase_service import FirebaseService
from ..schemas.user import UserResponse
from ..dependencies import get_current_user, get_current_patient

router = APIRouter()

@router.get("/")
async def get_all_doctors(
    specialty: Optional[str] = None,
    verified_only: bool = True,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all doctors with optional filters"""
    try:
        doctors = await FirebaseService.get_all_doctors(
            specialty=specialty,
            verified_only=verified_only,
            limit=limit,
            offset=offset
        )
        return {"doctors": doctors, "total": len(doctors)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{doctor_id}")
async def get_doctor_details(doctor_id: str):
    """Get doctor details by ID"""
    try:
        doctor = await FirebaseService.get_doctor(doctor_id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return doctor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{doctor_id}/availability")
async def get_doctor_availability(doctor_id: str):
    """Get doctor's availability schedule"""
    try:
        availability = await FirebaseService.get_doctor_schedules(doctor_id)
        return {"availability": availability}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{doctor_id}/availability")
async def update_doctor_availability(
    doctor_id: str,
    schedule: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update doctor availability (doctor only)"""
    try:
        if current_user['role'] != 'doctor' and current_user['role'] != 'admin':
            raise HTTPException(status_code=403, detail="Not authorized")
        
        if current_user['role'] == 'doctor' and current_user['user_id'] != doctor_id:
            raise HTTPException(status_code=403, detail="Can only update own schedule")
        
        await FirebaseService.update_doctor_schedule(doctor_id, schedule)
        return {"message": "Availability updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{doctor_id}/reviews")
async def get_doctor_reviews(
    doctor_id: str,
    limit: int = Query(20, ge=1, le=100)
):
    """Get doctor reviews"""
    try:
        reviews = await FirebaseService.get_doctor_reviews(doctor_id, limit)
        return {"reviews": reviews, "total": len(reviews)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{doctor_id}/reviews")
async def submit_doctor_review(
    doctor_id: str,
    review_data: dict,
    current_user: dict = Depends(get_current_patient)
):
    """Submit a review for a doctor"""
    try:
        review = await FirebaseService.submit_review(
            doctor_id=doctor_id,
            patient_id=current_user['user_id'],
            rating=review_data.get('rating'),
            comment=review_data.get('comment'),
            appointment_id=review_data.get('appointment_id')
        )
        return {"message": "Review submitted successfully", "review": review}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))