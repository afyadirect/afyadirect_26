# app/utils/constants.py
# Medical Specialties
SPECIALTIES = [
    "Cardiologist",
    "Dermatologist",
    "Neurologist",
    "Pediatrician",
    "Psychiatrist",
    "General Physician",
    "Gynecologist",
    "Orthopedic",
    "Ophthalmologist",
    "ENT Specialist",
    "Dentist",
    "Urologist",
    "Endocrinologist",
    "Gastroenterologist",
    "Pulmonologist",
    "Rheumatologist",
    "Oncologist",
    "Nephrologist",
    "Hematologist",
    "Infectious Disease Specialist"
]

# Blood Groups
BLOOD_GROUPS = [
    "A+", "A-", "B+", "B-", 
    "O+", "O-", "AB+", "AB-"
]

# Consultation Types
CONSULTATION_TYPES = [
    {"value": "chat", "label": "Chat Consultation", "price": 15000},
    {"value": "video", "label": "Video Consultation", "price": 25000},
    {"value": "voice", "label": "Voice Consultation", "price": 20000}
]

# Payment Methods
PAYMENT_METHODS = [
    {"value": "mpesa", "label": "M-Pesa", "icon": "mpesa.png"},
    {"value": "tigo", "label": "Tigo Pesa", "icon": "tigo.png"},
    {"value": "airtel", "label": "Airtel Money", "icon": "airtel.png"}
]

# Appointment Statuses
APPOINTMENT_STATUSES = [
    {"value": "pending", "label": "Pending", "color": "orange"},
    {"value": "confirmed", "label": "Confirmed", "color": "green"},
    {"value": "in_progress", "label": "In Progress", "color": "blue"},
    {"value": "completed", "label": "Completed", "color": "teal"},
    {"value": "cancelled", "label": "Cancelled", "color": "red"},
    {"value": "rejected", "label": "Rejected", "color": "red"}
]

# Notification Types
NOTIFICATION_TYPES = [
    "appointment_created",
    "appointment_confirmed",
    "appointment_reminder",
    "payment_received",
    "prescription_issued",
    "account_verified",
    "general"
]

# Time Slots (30-minute intervals)
TIME_SLOTS = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
    "15:00", "15:30", "16:00", "16:30", "17:00"
]

# Days of Week
DAYS_OF_WEEK = [
    {"value": 0, "name": "Monday"},
    {"value": 1, "name": "Tuesday"},
    {"value": 2, "name": "Wednesday"},
    {"value": 3, "name": "Thursday"},
    {"value": 4, "name": "Friday"},
    {"value": 5, "name": "Saturday"},
    {"value": 6, "name": "Sunday"}
]

# Consultation Durations (in minutes)
CONSULTATION_DURATIONS = {
    "chat": 30,
    "video": 30,
    "voice": 20
}

# Platform Fees
PLATFORM_FEE_PERCENTAGE = 0.10  # 10% platform fee
MINIMUM_CONSULTATION_FEE = 10000
MAXIMUM_CONSULTATION_FEE = 100000

# Cache Keys
CACHE_KEYS = {
    "USER_PREFIX": "user:",
    "DOCTOR_LIST": "doctors:list",
    "APPOINTMENT_PREFIX": "appointment:",
    "VERIFICATION_CODE": "verification:"
}

# Cache TTL (seconds)
CACHE_TTL = {
    "USER": 3600,  # 1 hour
    "DOCTOR_LIST": 300,  # 5 minutes
    "APPOINTMENT": 1800,  # 30 minutes
    "VERIFICATION_CODE": 600  # 10 minutes
}