"""
Sign language detection service.
Manages the ML model, MediaPipe, OpenCV camera, and detection state.

Uses the MediaPipe Tasks Vision API (HandLandmarker) since mediapipe 0.10.35
on Python 3.12 no longer ships the legacy mp.solutions module.

The ML pipeline is identical to the original Flask implementation:
- 21 landmarks per hand × 4 values (x, y, z, visibility) = 84 features per hand
- 168 total features (right hand + left hand)
- Same stability threshold of 5 consecutive identical predictions

All detection state is process-level (global) - same architecture as the Flask version.
This is appropriate for single-worker deployment (uvicorn with 1 worker).
"""

import logging
import os
import pickle
import time
import threading

import cv2
import numpy as np
import pandas as pd
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    HandLandmarksConnections,
    RunningMode,
)

from ..config import settings

logger = logging.getLogger(__name__)

# --- Hand connections for drawing ---
HAND_CONNECTIONS = HandLandmarksConnections.HAND_CONNECTIONS

# --- Resolve the hand landmarker model path ---
_HAND_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "hand_landmarker.task",
)

# --- Load the trained ML model (once at import time) ---
model = None
try:
    with open(settings.MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    logger.info("ML model loaded successfully from %s", settings.MODEL_PATH)
except Exception as e:
    logger.error("Model not found at %s: %s", settings.MODEL_PATH, e)
    print(f"Model not found. Please ensure body_language.pkl is in the project directory: {e}")

# --- Process-level detection state ---
camera = None
detection_active = False
current_prediction = ""
_state_lock = threading.Lock()


def _draw_hand_landmarks_on_image(image, hand_landmarks_list):
    """Draw hand landmarks and connections on the image using OpenCV."""
    h, w, _ = image.shape

    for hand_landmarks in hand_landmarks_list:
        # Draw connections
        for connection in HAND_CONNECTIONS:
            start = hand_landmarks[connection.start]
            end = hand_landmarks[connection.end]
            start_point = (int(start.x * w), int(start.y * h))
            end_point = (int(end.x * w), int(end.y * h))
            cv2.line(image, start_point, end_point, (0, 255, 0), 2)

        # Draw landmarks
        for landmark in hand_landmarks:
            cx, cy = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(image, (cx, cy), 4, (255, 0, 0), -1)

    return image


class SignLanguageDetector:
    """
    Sign language detection using MediaPipe HandLandmarker and a scikit-learn classifier.

    Extracts 168 features (84 per hand: 21 landmarks × 4 values [x, y, z, visibility]).
    Uses a stability threshold of 5 consecutive identical predictions to reduce noise.
    """

    def __init__(self):
        self.prev_prediction = ""
        self.stable_counter = 0
        self.STABILITY_THRESHOLD = 5

        # Initialize HandLandmarker with Tasks API
        if os.path.exists(_HAND_MODEL_PATH):
            options = HandLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=_HAND_MODEL_PATH),
                running_mode=RunningMode.IMAGE,
                num_hands=2,
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self.hand_landmarker = HandLandmarker.create_from_options(options)
            logger.info("HandLandmarker initialized from %s", _HAND_MODEL_PATH)
        else:
            self.hand_landmarker = None
            logger.error(
                "hand_landmarker.task not found at %s. "
                "Download it from: https://storage.googleapis.com/mediapipe-models/"
                "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task",
                _HAND_MODEL_PATH,
            )

    def detect_sign(self, frame):
        """Process a frame through the ML pipeline and return the annotated image."""
        global current_prediction

        if model is None or self.hand_landmarker is None:
            return frame

        # Convert BGR to RGB for MediaPipe
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

        # Detect hands
        result = self.hand_landmarker.detect(mp_image)

        # Work on a copy of the frame for drawing
        image = frame.copy()

        # Draw landmarks on the image
        if result.hand_landmarks:
            _draw_hand_landmarks_on_image(image, result.hand_landmarks)

        try:
            if result.hand_landmarks:
                right_row = [0] * 84
                left_row = [0] * 84

                # Classify hands by handedness
                for i, (hand_landmarks, handedness) in enumerate(
                    zip(result.hand_landmarks, result.handedness)
                ):
                    # Extract landmarks: x, y, z, visibility
                    # The Tasks API may return NaN for visibility, so we
                    # replace NaN with 0.0 to match the original training data.
                    landmarks_flat = []
                    for lm in hand_landmarks:
                        x = lm.x if not np.isnan(lm.x) else 0.0
                        y = lm.y if not np.isnan(lm.y) else 0.0
                        z = lm.z if not np.isnan(lm.z) else 0.0
                        # visibility may be NaN in the Tasks API
                        vis = 0.0
                        if hasattr(lm, 'visibility') and lm.visibility is not None:
                            vis = lm.visibility if not np.isnan(lm.visibility) else 0.0
                        elif hasattr(lm, 'presence') and lm.presence is not None:
                            vis = lm.presence if not np.isnan(lm.presence) else 0.0
                        landmarks_flat.extend([x, y, z, vis])

                    hand_label = handedness[0].category_name.lower()

                    # Note: MediaPipe reports handedness from the camera's perspective
                    # which is mirrored. "Right" from camera = user's left hand.
                    # The original Flask code used Holistic which also uses camera perspective.
                    if hand_label == "right":
                        right_row = landmarks_flat[:84]
                    elif hand_label == "left":
                        left_row = landmarks_flat[:84]

                # Build the 168-feature vector (same order as training data)
                row = right_row + left_row
                # Replace any remaining NaN values with 0.0 as a safety net
                row = [0.0 if np.isnan(v) else v for v in row]
                X = pd.DataFrame([row])
                prediction = model.predict(X)[0]
                proba = model.predict_proba(X)[0]
                confidence = proba[np.argmax(proba)]

                if prediction == self.prev_prediction:
                    self.stable_counter += 1
                else:
                    self.stable_counter = 0
                    self.prev_prediction = prediction

                if self.stable_counter > self.STABILITY_THRESHOLD:
                    current_prediction = prediction
                    cv2.rectangle(image, (10, 10), (400, 60), (0, 0, 0), -1)
                    cv2.putText(
                        image,
                        f"Sign: {prediction}",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2,
                    )

        except Exception as e:
            logger.error("Detection error: %s", e)

        return image


# Singleton detector instance (same as Flask's module-level instantiation)
detector = SignLanguageDetector()


def start_camera() -> tuple[bool, str]:
    """Start the camera and enable detection."""
    global camera, detection_active

    with _state_lock:
        try:
            camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, settings.CAMERA_WIDTH)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.CAMERA_HEIGHT)
            detection_active = True
            logger.info("Camera started successfully")
            return True, "Detection started"
        except Exception as e:
            logger.error("Failed to start camera: %s", e)
            return False, str(e)


def stop_camera() -> tuple[bool, str]:
    """Stop the camera and disable detection."""
    global camera, detection_active

    with _state_lock:
        detection_active = False
        if camera:
            camera.release()
            camera = None
        logger.info("Camera stopped")
        return True, "Detection stopped"


def generate_frames():
    """
    Generator that yields MJPEG frames for streaming.
    Each frame is processed through the sign language detection pipeline.
    """
    global camera, detection_active

    while detection_active and camera and camera.isOpened():
        success, frame = camera.read()
        if not success:
            break

        processed_frame = detector.detect_sign(frame)

        try:
            ret, buffer = cv2.imencode(".jpg", processed_frame)
            frame_bytes = buffer.tobytes()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
        except Exception as e:
            logger.error("Encoding error: %s", e)
            continue

        time.sleep(settings.FRAME_DELAY)  # ~30 FPS


def get_current_prediction() -> str:
    """Return the current stable prediction."""
    return current_prediction
