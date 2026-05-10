# app/main.py (Updated)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from .config import settings
from .routers import (
    auth_router, users_router, appointments_router,
    doctors_router, payments_router, chat_router,
    prescriptions_router, admin_router
)
from .services.websocket_manager import websocket_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info("Starting up AfyaDirect Backend...")
    await initialize_services()
    yield
    logger.info("Shutting down AfyaDirect Backend...")
    await cleanup_services()

async def initialize_services():
    """Initialize all services on startup"""
    from .services.firebase_service import FirebaseService
    await FirebaseService.initialize()
    logger.info("Firebase initialized successfully")

async def cleanup_services():
    """Cleanup services on shutdown"""
    pass

# Create FastAPI app
app = FastAPI(
    title="AfyaDirect API",
    description="Healthcare Telemedicine Platform API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(appointments_router, prefix="/api/v1/appointments", tags=["Appointments"])
app.include_router(doctors_router, prefix="/api/v1/doctors", tags=["Doctors"])
app.include_router(payments_router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(prescriptions_router, prefix="/api/v1/prescriptions", tags=["Prescriptions"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])

# WebSocket endpoint for real-time chat
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.handle_message(user_id, data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AfyaDirect API", "version": "1.0.0"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to AfyaDirect API",
        "version": "1.0.0",
        "documentation": "/api/docs",
        "redoc": "/api/redoc"
    }