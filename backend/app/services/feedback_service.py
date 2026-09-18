"""
Feedback storage service - manages feedback.json CRUD operations.
"""

import json
import os
import logging
from datetime import datetime

from ..config import settings

logger = logging.getLogger(__name__)


def load_feedback() -> list:
    """Load feedback entries from the JSON file."""
    if os.path.exists(settings.FEEDBACK_FILE):
        with open(settings.FEEDBACK_FILE, "r") as f:
            return json.load(f)
    return []


def save_feedback(feedback_list: list) -> None:
    """Save feedback entries to the JSON file."""
    with open(settings.FEEDBACK_FILE, "w") as f:
        json.dump(feedback_list, f, indent=2)


def add_feedback(feedback_text: str) -> None:
    """Add a new feedback entry with timestamp."""
    feedback_list = load_feedback()
    feedback_entry = {
        "feedback": feedback_text,
        "timestamp": datetime.now().isoformat(),
    }
    feedback_list.append(feedback_entry)
    save_feedback(feedback_list)
    logger.info("New feedback submitted")
