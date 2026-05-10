# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from ..models.user import UserRole, Language

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r'^(?:\+?255|0)[67]\d{8}$')
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.PATIENT
    language: Language = Language.ENGLISH
    date_of_birth: Optional[datetime] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    specialty: Optional[str] = None
    license_number: Optional[str] = None
    consultation_fee: Optional[float] = None
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    language: Optional[Language] = None
    fcm_token: Optional[str] = None
    profile_image: Optional[str] = None

class UserResponse(BaseModel):
    uid: str
    full_name: str
    email: str
    phone: str
    role: str
    language: str
    is_active: bool
    profile_image: Optional[str]
    created_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class PatientProfileUpdate(BaseModel):
    date_of_birth: Optional[datetime] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    medical_history: Optional[str] = None
    emergency_contact: Optional[str] = None
    insurance_info: Optional[str] = None

class DoctorProfileUpdate(BaseModel):
    specialty: Optional[str] = None
    consultation_fee: Optional[float] = None
    available_from: Optional[str] = None
    available_to: Optional[str] = None
    education: Optional[str] = None
    languages: Optional[list] = None