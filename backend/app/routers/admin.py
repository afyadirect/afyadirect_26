# app/routers/admin.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
from ..services.firebase_service import FirebaseService
from ..dependencies import get_current_admin

router = APIRouter()

@router.get("/dashboard/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_admin)):
    """Get platform statistics for admin dashboard"""
    try:
        # Get user counts
        users = await FirebaseService.get_all_users()
        total_users = len(users)
        patients = len([u for u in users if u.get('role') == 'patient'])
        doctors = len([u for u in users if u.get('role') == 'doctor'])
        admins = len([u for u in users if u.get('role') == 'admin'])
        
        # Get appointment stats
        appointments = await FirebaseService.get_all_appointments()
        total_appointments = len(appointments)
        completed = len([a for a in appointments if a.get('status') == 'completed'])
        pending = len([a for a in appointments if a.get('status') == 'pending'])
        cancelled = len([a for a in appointments if a.get('status') == 'cancelled'])
        
        # Calculate revenue
        total_revenue = sum([a.get('fee', 0) for a in appointments if a.get('paymentStatus') == 'paid'])
        
        # Get pending verifications
        unverified_doctors = len([d for d in await FirebaseService.get_all_doctors() if not d.get('isVerified')])
        
        return {
            "users": {
                "total": total_users,
                "patients": patients,
                "doctors": doctors,
                "admins": admins
            },
            "appointments": {
                "total": total_appointments,
                "completed": completed,
                "pending": pending,
                "cancelled": cancelled
            },
            "revenue": total_revenue,
            "pending_verifications": unverified_doctors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/recent-activity")
async def get_recent_activity(
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_admin)
):
    """Get recent platform activity"""
    try:
        appointments = await FirebaseService.get_recent_appointments(limit)
        activity = []
        
        for apt in appointments:
            patient = await FirebaseService.get_user(apt.get('patientId', ''))
            doctor = await FirebaseService.get_user(apt.get('doctorId', ''))
            
            activity.append({
                "id": apt.get('id'),
                "type": "appointment",
                "patient_name": patient.get('fullName') if patient else 'Unknown',
                "doctor_name": doctor.get('fullName') if doctor else 'Unknown',
                "status": apt.get('status'),
                "created_at": apt.get('createdAt'),
                "fee": apt.get('fee')
            })
        
        return {"activity": activity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/revenue")
async def get_revenue_analytics(
    period: str = Query("month", regex="^(week|month|year)$"),
    current_user: dict = Depends(get_current_admin)
):
    """Get revenue analytics data"""
    try:
        now = datetime.utcnow()
        
        if period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        else:
            start_date = now - timedelta(days=365)
        
        payments = await FirebaseService.get_payments_by_date_range(start_date, now)
        
        # Group by date
        revenue_by_date = {}
        for payment in payments:
            if payment.get('status') == 'completed':
                date = payment.get('paidAt', payment.get('createdAt')).date()
                revenue_by_date[date] = revenue_by_date.get(date, 0) + payment.get('amount', 0)
        
        return {
            "period": period,
            "total_revenue": sum(revenue_by_date.values()),
            "data": [{"date": str(k), "revenue": v} for k, v in revenue_by_date.items()]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/doctors")
async def get_doctor_analytics(
    current_user: dict = Depends(get_current_admin)
):
    """Get doctor performance analytics"""
    try:
        doctors = await FirebaseService.get_all_doctors()
        doctor_stats = []
        
        for doctor in doctors:
            appointments = await FirebaseService.get_doctor_appointments(doctor.get('userId'))
            completed = len([a for a in appointments if a.get('status') == 'completed'])
            revenue = sum([a.get('fee', 0) for a in appointments if a.get('paymentStatus') == 'paid'])
            
            doctor_stats.append({
                "doctor_id": doctor.get('userId'),
                "name": doctor.get('fullName', 'Unknown'),
                "specialty": doctor.get('specialty'),
                "rating": doctor.get('rating', 0),
                "total_patients": doctor.get('totalPatients', 0),
                "completed_appointments": completed,
                "revenue": revenue,
                "is_verified": doctor.get('isVerified', False)
            })
        
        # Sort by rating
        doctor_stats.sort(key=lambda x: x['rating'], reverse=True)
        
        return {"doctors": doctor_stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/platform-usage")
async def get_platform_usage(
    current_user: dict = Depends(get_current_admin)
):
    """Get platform usage statistics"""
    try:
        # Get user device distribution
        users = await FirebaseService.get_all_users()
        
        # Count active users (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = len([u for u in users if u.get('lastLogin') and u['lastLogin'] > thirty_days_ago])
        
        # Count appointments by consultation type
        appointments = await FirebaseService.get_all_appointments()
        consultation_types = {}
        for apt in appointments:
            ctype = apt.get('consultationType', 'chat')
            consultation_types[ctype] = consultation_types.get(ctype, 0) + 1
        
        return {
            "total_users": len(users),
            "active_users_last_30_days": active_users,
            "engagement_rate": (active_users / len(users) * 100) if users else 0,
            "consultation_types": consultation_types,
            "appointments_by_status": {
                "pending": len([a for a in appointments if a.get('status') == 'pending']),
                "confirmed": len([a for a in appointments if a.get('status') == 'confirmed']),
                "completed": len([a for a in appointments if a.get('status') == 'completed']),
                "cancelled": len([a for a in appointments if a.get('status') == 'cancelled'])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/doctors/{doctor_id}/verify")
async def verify_doctor(
    doctor_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """Verify a doctor's account"""
    try:
        await FirebaseService.verify_doctor(doctor_id)
        
        # Send notification
        await FirebaseService.create_notification(
            user_id=doctor_id,
            title="Account Verified",
            message="Your doctor account has been verified. You can now start accepting patients.",
            notification_type="verification"
        )
        
        return {"message": "Doctor verified successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """Delete a user (admin only)"""
    try:
        await FirebaseService.delete_user(user_id)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/block")
async def block_user(
    user_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """Block/unblock a user"""
    try:
        user = await FirebaseService.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_status = not user.get('isActive', True)
        await FirebaseService.update_user(user_id, {'isActive': new_status})
        
        return {"message": f"User {'blocked' if not new_status else 'unblocked'} successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))