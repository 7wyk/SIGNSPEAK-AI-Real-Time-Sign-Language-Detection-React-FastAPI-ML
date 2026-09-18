"""
User storage service - manages users.json CRUD operations.
"""

import json
import os
import logging

from ..config import settings
from ..security import hash_password, verify_password, needs_rehash

logger = logging.getLogger(__name__)


def load_users() -> dict:
    """Load users from the JSON file."""
    if os.path.exists(settings.USERS_FILE):
        with open(settings.USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users: dict) -> None:
    """Save users to the JSON file."""
    with open(settings.USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def user_exists(username: str) -> bool:
    """Check if a user already exists."""
    users = load_users()
    return username in users


def create_user(username: str, password: str) -> bool:
    """
    Create a new user with bcrypt-hashed password.
    Returns True if created, False if username already exists.
    """
    users = load_users()
    if username in users:
        return False

    users[username] = hash_password(password)
    save_users(users)
    logger.info(f"New user registered: {username}")
    return True


def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate a user. Supports both plaintext (legacy) and bcrypt passwords.
    If a legacy plaintext password is found and matches, it is transparently
    upgraded to bcrypt.
    """
    users = load_users()
    if username not in users:
        return False

    stored_password = users[username]

    if not verify_password(password, stored_password):
        return False

    # Transparent password upgrade: rehash plaintext to bcrypt
    if needs_rehash(stored_password):
        users[username] = hash_password(password)
        save_users(users)
        logger.info(f"Password upgraded to bcrypt for user: {username}")

    return True
