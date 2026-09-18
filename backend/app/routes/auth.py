"""
Authentication routes: /register and /login.
"""

from fastapi import APIRouter, HTTPException, status

from ..schemas import RegisterRequest, LoginRequest, AuthResponse
from ..security import generate_token
from ..services import user_service

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    summary="Register a new user",
    description="Create a new user account with email and password. Passwords are hashed with bcrypt.",
)
async def register(request: RegisterRequest):
    """Register a new user account."""
    if not user_service.create_user(request.username, request.password):
        return AuthResponse(
            success=False,
            message="Username already exists",
        )

    return AuthResponse(
        success=True,
        message="Registration successful",
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login with credentials",
    description="Authenticate with email and password. Returns a JWT token valid for 24 hours.",
)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token."""
    if not user_service.authenticate_user(request.username, request.password):
        return AuthResponse(
            success=False,
            message="Invalid credentials",
        )

    token = generate_token(request.username)
    return AuthResponse(
        success=True,
        token=token,
    )
