# app/routers/prescriptions.py
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List
from ..services.firebase_service import FirebaseService
from ..services.prescription_generator import PrescriptionGenerator
from ..schemas.common import SuccessResponse
from ..dependencies import get_current_user, get_current_doctor

router = APIRouter()

@router.post("/generate")
async def generate_prescription(
    prescription_data: dict,
    current_user: dict = Depends(get_current_doctor)
):
    """Generate a prescription PDF"""
    try:
        pdf_url = await PrescriptionGenerator.generate_pdf(prescription_data)
        
        # Save to Firestore
        prescription_id = await FirebaseService.create_prescription({
            'appointmentId': prescription_data.get('appointment_id'),
            'doctorId': current_user['user_id'],
            'patientId': prescription_data.get('patient_id'),
            'medicines': prescription_data.get('medicines'),
            'instructions': prescription_data.get('instructions'),
            'pdfUrl': pdf_url
        })
        
        return SuccessResponse(
            message="Prescription generated successfully",
            data={"prescription_id": prescription_id, "pdf_url": pdf_url}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/appointment/{appointment_id}")
async def get_prescriptions_for_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get prescriptions for an appointment"""
    try:
        prescriptions = await FirebaseService.get_prescriptions_by_appointment(appointment_id)
        
        # Verify authorization
        if prescriptions:
            apt = await FirebaseService.get_appointment(appointment_id)
            if apt and current_user['user_id'] not in [apt['patientId'], apt['doctorId']] and current_user['role'] != 'admin':
                raise HTTPException(status_code=403, detail="Not authorized")
        
        return {"prescriptions": prescriptions}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient/{patient_id}")
async def get_patient_prescriptions(
    patient_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all prescriptions for a patient"""
    try:
        if current_user['user_id'] != patient_id and current_user['role'] != 'admin':
            raise HTTPException(status_code=403, detail="Not authorized")
        
        prescriptions = await FirebaseService.get_prescriptions_by_patient(patient_id)
        return {"prescriptions": prescriptions}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))