# app/utils/helpers.py
import random
import re
from datetime import datetime
from typing import Optional

def format_phone_number(phone: str) -> str:
    """Format phone number to international format"""
    # Remove any non-digit characters
    phone = re.sub(r'\D', '', phone)
    
    # If starts with 0, replace with +255
    if phone.startswith('0'):
        phone = '+255' + phone[1:]
    # If starts with 255, add +
    elif phone.startswith('255'):
        phone = '+' + phone
    # If doesn't start with +, add +255
    elif not phone.startswith('+'):
        phone = '+255' + phone
    
    return phone

def generate_otp(length: int = 6) -> str:
    """Generate OTP code"""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def calculate_age(birth_date: datetime) -> int:
    """Calculate age from birth date"""
    today = datetime.now()
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    return age

def format_currency(amount: float) -> str:
    """Format currency in TZS"""
    return f"TZS {amount:,.0f}"

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def get_time_ago(timestamp: datetime) -> str:
    """Get human-readable time ago string"""
    now = datetime.utcnow()
    diff = now - timestamp
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    else:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days > 1 else ''} ago"

def generate_appointment_id() -> str:
    """Generate unique appointment ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_num = random.randint(1000, 9999)
    return f"APT{timestamp}{random_num}"

def generate_transaction_id() -> str:
    """Generate unique transaction ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_num = random.randint(100000, 999999)
    return f"TXN{timestamp}{random_num}"