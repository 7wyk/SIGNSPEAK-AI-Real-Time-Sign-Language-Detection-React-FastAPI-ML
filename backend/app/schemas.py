"""
Pydantic models for API request/response validation.
All schemas preserve the exact API contracts expected by the React frontend.
"""

from pydantic import BaseModel, Field


# --- Auth Schemas ---

class RegisterRequest(BaseModel):
    """POST /register request body."""
    username: str = Field(..., min_length=1, description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class LoginRequest(BaseModel):
    """POST /login request body."""
    username: str = Field(..., min_length=1, description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class AuthResponse(BaseModel):
    """Response for auth endpoints."""
    success: bool
    message: str | None = None
    token: str | None = None


# --- Feedback Schemas ---

class FeedbackRequest(BaseModel):
    """POST /feedback request body."""
    feedback: str = Field(..., min_length=1, description="Feedback text content")


class FeedbackResponse(BaseModel):
    """Response for feedback submission."""
    success: bool
    message: str


# --- Translation Schemas ---

class TranslationRequest(BaseModel):
    """POST /translate request body."""
    text: str = Field(..., min_length=1, description="Text to translate")
    language: str = Field(..., min_length=1, description="Target language name (hindi, kannada, malayalam)")


class TranslationResponse(BaseModel):
    """Response for translation endpoint."""
    success: bool
    translated_text: str | None = None
    original_text: str | None = None
    message: str | None = None


# --- Detection Schemas ---

class DetectionResponse(BaseModel):
    """Response for start/stop detection endpoints."""
    success: bool
    message: str


class PredictionResponse(BaseModel):
    """Response for get_prediction endpoint."""
    prediction: str
