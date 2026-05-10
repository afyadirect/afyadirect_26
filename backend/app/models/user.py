# app/models/user.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"

class Language(str, Enum):
    ENGLISH = "en"
    SWAHILI = "sw"

class BloodGroup(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"

class User(BaseModel):
    uid: str
    fullName: str
    email: str
    phone: str
    role: UserRole
    language: Language = Language.ENGLISH
    isActive: bool = True
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    lastLogin: Optional[datetime] = None
    fcmToken: Optional[str] = None
    profileImage: Optional[str] = None

class Patient(BaseModel):
    userId: str
    dateOfBirth: Optional[datetime] = None
    address: Optional[str] = None
    bloodGroup: Optional[BloodGroup] = None
    allergies: Optional[str] = None
    medicalHistory: Optional[str] = None
    emergencyContact: Optional[str] = None
    insuranceInfo: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class Doctor(BaseModel):
    userId: str
    specialty: str
    licenseNumber: str
    consultationFee: float
    rating: float = 0.0
    totalPatients: int = 0
    isVerified: bool = False
    availableFrom: str = "09:00"
    availableTo: str = "17:00"
    experience: int = 0
    education: Optional[str] = None
    languages: List[str] = ["English", "Swahili"]
    verifiedAt: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class Admin(BaseModel):
    userId: str
    permissions: List[str] = ["all"]
    level: str = "super"
    lastLogin: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)