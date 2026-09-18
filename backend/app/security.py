"""
JWT token generation/verification and password hashing utilities.
"""

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from .config import settings

# Password hashing context - bcrypt with automatic plaintext detection
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    Verify a password against a stored hash or plaintext.

    Supports transparent migration from plaintext to bcrypt:
    - If stored_password is a bcrypt hash, verify against it.
    - If stored_password is plaintext, do a direct comparison.
    """
    # Check if stored password is a bcrypt hash (starts with $2b$ or $2a$)
    if stored_password.startswith(("$2b$", "$2a$", "$2y$")):
        return pwd_context.verify(plain_password, stored_password)
    else:
        # Plaintext comparison for legacy passwords
        return plain_password == stored_password


def needs_rehash(stored_password: str) -> bool:
    """Check if a stored password needs to be upgraded to bcrypt."""
    return not stored_password.startswith(("$2b$", "$2a$", "$2y$"))


def generate_token(username: str) -> str:
    """Generate a JWT token for the given username."""
    payload = {
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> str | None:
    """
    Verify a JWT token and return the username.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload["username"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
