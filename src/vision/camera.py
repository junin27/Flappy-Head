import cv2
import threading
import time
import numpy as np
from typing import Tuple, Optional

class CameraThread:
    def __init__(self, cap: cv2.VideoCapture) -> None:
        self._cap: cv2.VideoCapture = cap
        self._frame: Optional[np.ndarray] = None
        self._lock: threading.Lock = threading.Lock()
        self._running: bool = True
        self._thread: threading.Thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        while self._running:
            ok, frame = self._cap.read()
            if ok:
                frame = cv2.flip(frame, 1)
                with self._lock:
                    self._frame = frame
            else:
                time.sleep(0.01)

    @property
    def last_frame(self) -> Optional[np.ndarray]:
        with self._lock:
            return self._frame

    def stop(self) -> None:
        self._running = False
        self._thread.join(timeout=2.0)
        
def start_camera() -> Tuple[Optional[cv2.VideoCapture], Optional[CameraThread]]:
    cap: Optional[cv2.VideoCapture] = None
    for i in range(4):
        c = cv2.VideoCapture(i, cv2.CAP_MSMF)
        if not c.isOpened():
            c = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if not c.isOpened():
                c = cv2.VideoCapture(i)
        
        if c.isOpened():
            ok, f = c.read()
            if ok and f is not None and f.mean() > 5.0:
                cap = c
                break
            else:
                c.release()

    if cap is None:
        return None, None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    camera = CameraThread(cap)
    
    # Wait for frame
    for _ in range(50):
        if camera.last_frame is not None:
            return cap, camera
        time.sleep(0.1)
        
    camera.stop()
    cap.release()
    return None, None
