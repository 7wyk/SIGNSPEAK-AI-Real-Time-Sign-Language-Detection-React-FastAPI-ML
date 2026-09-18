"""
Feedback route: /feedback.
"""

from fastapi import APIRouter

from ..schemas import FeedbackRequest, FeedbackResponse
from ..services import feedback_service

router = APIRouter(tags=["Feedback"])


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    summary="Submit user feedback",
    description="Submit feedback, feature requests, bug reports, or suggestions.",
)
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback."""
    try:
        feedback_service.add_feedback(request.feedback)
        return FeedbackResponse(
            success=True,
            message="Feedback submitted successfully",
        )
    except Exception as e:
        return FeedbackResponse(
            success=False,
            message=f"Failed to save feedback: {str(e)}",
        )
