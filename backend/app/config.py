"""
Application configuration using Pydantic Settings.
Loads from environment variables and .env file.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # JWT Configuration
    JWT_SECRET_KEY: str = "your-secret-key-here"
    JWT_EXPIRATION_HOURS: int = 24

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # File Paths (relative to project root)
    MODEL_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "body_language.pkl",
    )
    USERS_FILE: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "users.json",
    )
    FEEDBACK_FILE: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "feedback.json",
    )

    # Camera Configuration
    CAMERA_WIDTH: int = 640
    CAMERA_HEIGHT: int = 480
    FRAME_DELAY: float = 0.03  # ~30 FPS

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {
        "env_file": os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
        ),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Singleton settings instance
settings = Settings()
