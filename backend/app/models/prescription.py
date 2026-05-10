# app/models/prescription.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class Medicine(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: str
    notes: Optional[str] = None

class Prescription(BaseModel):
    id: str
    appointmentId: str
    doctorId: str
    patientId: str
    medicines: List[Medicine]
    instructions: str
    pdfUrl: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)