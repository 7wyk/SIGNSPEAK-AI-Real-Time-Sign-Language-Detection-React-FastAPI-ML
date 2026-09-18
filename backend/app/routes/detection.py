"""
Detection routes: /start_detection, /stop_detection, /video_feed, /get_prediction.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ..schemas import DetectionResponse, PredictionResponse
from ..dependencies import get_current_user
from ..services import detection_service

router = APIRouter(tags=["Detection"])


@router.post(
    "/start_detection",
    response_model=DetectionResponse,
    summary="Start sign language detection",
    description="Starts the webcam and begins real-time sign language detection. Requires authentication.",
)
async def start_detection(username: str = Depends(get_current_user)):
    """Start the camera and detection pipeline. Protected endpoint."""
    success, message = detection_service.start_camera()
    return DetectionResponse(success=success, message=message)


@router.post(
    "/stop_detection",
    response_model=DetectionResponse,
    summary="Stop sign language detection",
    description="Stops the webcam and detection pipeline.",
)
async def stop_detection():
    """Stop the camera and detection pipeline."""
    success, message = detection_service.stop_camera()
    return DetectionResponse(success=success, message=message)


@router.get(
    "/video_feed",
    summary="MJPEG video stream",
    description="Returns an MJPEG video stream with real-time sign language detection overlay. "
    "Used by the frontend `<img>` tag for live camera feed.",
    responses={
        200: {
            "content": {"multipart/x-mixed-replace": {}},
            "description": "MJPEG video stream with detection overlay",
        }
    },
)
async def video_feed():
    """Stream processed video frames as MJPEG."""
    return StreamingResponse(
        detection_service.generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.get(
    "/get_prediction",
    response_model=PredictionResponse,
    summary="Get current prediction",
    description="Returns the current stable sign language prediction. "
    "Polled by the frontend every 100ms during active detection.",
)
async def get_prediction():
    """Return the current stable prediction."""
    return PredictionResponse(
        prediction=detection_service.get_current_prediction()
    )
