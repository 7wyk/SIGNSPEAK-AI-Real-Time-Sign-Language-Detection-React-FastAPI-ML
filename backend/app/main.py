"""
SignSpeak AI - FastAPI Backend
Real-time sign language detection and translation API.

Migrated from Flask to FastAPI.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes import auth, detection, translation, feedback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="SignSpeak AI",
    description=(
        "Real-time sign language detection and translation API. "
        "Uses MediaPipe Holistic for hand tracking and a scikit-learn classifier "
        "for gesture recognition. Supports translation to Hindi, Kannada, and Malayalam."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - configured from environment variables
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(detection.router)
app.include_router(translation.router)
app.include_router(feedback.router)


@app.get(
    "/",
    summary="API root",
    description="Returns basic API information and status.",
    tags=["General"],
)
async def root():
    """API root endpoint - returns service information."""
    return {
        "message": "SignSpeak AI API",
        "version": "2.0.0",
        "framework": "FastAPI",
        "docs": "/docs",
        "redoc": "/redoc",
    }
