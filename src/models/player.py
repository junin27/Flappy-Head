from dataclasses import dataclass
from typing import Optional
import numpy as np
from src.config import PLAYER_X, FACE_RADIUS

@dataclass
class Player:
    y: float
    velocity_y: float = 0.0
    angle: float = 0.0
    name: str = "Player"
    mode: str = "mouth"  # "mouth" or "head"
    face_img: Optional[np.ndarray] = None
    mouth_open: bool = False
    webcam_available: bool = True
    
    @property
    def x(self) -> int:
        return PLAYER_X
    
    @property
    def radius(self) -> int:
        return FACE_RADIUS
