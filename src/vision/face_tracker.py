import os
import urllib.request
import math
import logging
from typing import Tuple, Optional, Any
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import FaceLandmarker, FaceLandmarkerOptions, RunningMode
from src.config import MODEL_FILE, MODEL_URL, MOUTH_OPEN_THRESHOLD

logger = logging.getLogger(__name__)

def ensure_model() -> None:
    if os.path.exists(MODEL_FILE):
        return
    logger.info("Downloading MediaPipe FaceLandmarker model...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_FILE)

class FaceTracker:
    def __init__(self) -> None:
        ensure_model()
        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_FILE),
            running_mode=RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.1,
            min_face_presence_confidence=0.1,
            min_tracking_confidence=0.1,
        )
        self.landmarker: FaceLandmarker = FaceLandmarker.create_from_options(options)

    def close(self) -> None:
        if self.landmarker:
            self.landmarker.close()

    def process_frame(
        self, frame: np.ndarray, face_radius: int
    ) -> Tuple[bool, float, bool, Optional[np.ndarray], float]:
        rgb = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = self.landmarker.detect(mp_image)
        
        if not results.face_landmarks:
            return False, 0.0, False, None, 0.5
            
        landmarks = results.face_landmarks[0]
        mouth_ratio, head_y_ratio = FaceTracker.calculate_metrics(landmarks)
        mouth_open = mouth_ratio > MOUTH_OPEN_THRESHOLD
        cropped_face = self._crop_face(frame, landmarks, face_radius)
        
        return True, mouth_ratio, mouth_open, cropped_face, head_y_ratio

    @staticmethod
    def calculate_metrics(landmarks: Any) -> Tuple[float, float]:
        lip_upper = landmarks[13]
        lip_lower = landmarks[14]
        forehead = landmarks[10]
        chin = landmarks[152]
        nose = landmarks[4]

        mouth_dist = math.hypot(lip_upper.x - lip_lower.x, lip_upper.y - lip_lower.y)
        face_dist = math.hypot(forehead.x - chin.x, forehead.y - chin.y)

        if face_dist <= 0:
            return 0.0, 1.0
            
        ratio = mouth_dist / face_dist
        
        nose_chin_dist = math.hypot(nose.x - chin.x, nose.y - chin.y)
        nose_forehead_dist = math.hypot(nose.x - forehead.x, nose.y - forehead.y)
        
        if nose_forehead_dist <= 0:
            pitch_ratio = 1.0
        else:
            pitch_ratio = nose_chin_dist / nose_forehead_dist
        
        return ratio, pitch_ratio

    def _crop_face(self, frame: np.ndarray, landmarks: Any, radius: int) -> Optional[np.ndarray]:
        h, w = frame.shape[:2]
        xs = [lm.x * w for lm in landmarks]
        ys = [lm.y * h for lm in landmarks]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        cx = int((x_min + x_max) / 2)
        cy = int((y_min + y_max) / 2)

        face_width = x_max - x_min
        face_height = y_max - y_min
        side = int(max(face_width, face_height) * 1.35)

        x1 = max(0, cx - side // 2)
        y1 = max(0, cy - side // 2)
        x2 = min(w, x1 + side)
        y2 = min(h, y1 + side)

        x1 = max(0, x2 - side)
        y1 = max(0, y2 - side)

        face = frame[y1:y2, x1:x2]
        if face.size == 0:
            return None

        return cv2.resize(face, (radius * 2, radius * 2))
