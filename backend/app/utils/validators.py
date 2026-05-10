# app/utils/validators.py
import re
from typing import Optional
from datetime import datetime

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate Tanzanian phone number"""
    # Remove any spaces or special characters
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    # Check format: 0712345678, +255712345678, 255712345678
    pattern = r'^(?:\+?255|0)[67]\d{8}$'
    return bool(re.match(pattern, phone))

def validate_password(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

def validate_amount(amount: float, min_amount: float = 5000, max_amount: float = 5000000) -> bool:
    """Validate payment amount"""
    return min_amount <= amount <= max_amount

def validate_date(date: datetime, allow_past: bool = False) -> bool:
    """Validate date"""
    if not allow_past and date < datetime.now():
        return False
    return True

def validate_time(time_str: str) -> bool:
    """Validate time format (HH:MM)"""
    pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(pattern, time_str))

def validate_license_number(license: str) -> bool:
    """Validate medical license number"""
    # Format depends on country, this is a basic check
    return len(license) >= 5 and license.isalnum()

def validate_blood_group(blood_group: str) -> bool:
    """Validate blood group"""
    valid_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    return blood_group in valid_groups

def validate_specialty(specialty: str) -> bool:
    """Validate medical specialty"""
    from .constants import SPECIALTIES
    return specialty in SPECIALTIES

def validate_consultation_type(consultation_type: str) -> bool:
    """Validate consultation type"""
    valid_types = ['chat', 'video', 'voice']
    return consultation_type in valid_types

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    # Remove any potentially dangerous characters
    return re.sub(r'[<>{}]', '', text).strip()

def validate_string_length(text: str, min_length: int = 1, max_length: int = 500) -> bool:
    """Validate string length"""
    return min_length <= len(text) <= max_length