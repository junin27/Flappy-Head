from typing import List, Tuple
from src.models.player import Player
from src.models.pipe import Pipe
from src.config import (
    GRAVITY, IMPULSE, MAX_FALL_SPEED, MAX_RISE_SPEED,
    HEIGHT, GROUND_HEIGHT, MODE_MOUTH, MODE_HEAD,
    PIPE_INTERVAL, PIPE_SPEED,
    DIFFICULTY_STEP_TIME, DIFFICULTY_MAX_LEVEL,
    PIPE_INTERVAL_MINIMUM, DIFFICULTY_INTERVAL_DECREMENT,
    DIFFICULTY_SPEED_INCREMENT
)

def circle_rectangle_collision(cx: float, cy: float, radius: float, rx: float, ry: float, rw: float, rh: float) -> bool:
    """Returns True if the circle intersects the rectangle."""
    px = max(rx, min(cx, rx + rw))
    py = max(ry, min(cy, ry + rh))
    dx = cx - px
    dy = cy - py
    return (dx * dx + dy * dy) < (radius * radius)

class GameEngine:
    def __init__(self) -> None:
        self.survival_time: float = 0.0
        self.collided: bool = False

    def update_time(self, delta_time: float) -> None:
        """Increments survival time in seconds."""
        self.survival_time += delta_time

    def get_difficulty_parameters(self) -> Tuple[int, float]:
        """
        Returns (pipe_interval_frames, pipe_speed).
        Difficulty escalates every step time.
        """
        level = int(self.survival_time // DIFFICULTY_STEP_TIME)
        level = min(level, DIFFICULTY_MAX_LEVEL)
        
        interval = max(PIPE_INTERVAL_MINIMUM, PIPE_INTERVAL - (level * DIFFICULTY_INTERVAL_DECREMENT))
        speed = PIPE_SPEED + (level * DIFFICULTY_SPEED_INCREMENT)
        return interval, speed

    def update_physics(self, player: Player, head_y_ratio: float = 0.5) -> None:
        """
        Updates y-velocity and position of the player based on control mode.
        head_y_ratio: Ratio of the face height on screen (0.0=top, 1.0=ground).
        """
        if player.mode == MODE_MOUTH:
            if player.mouth_open:
                player.velocity_y += IMPULSE * 0.25
                if player.velocity_y < MAX_RISE_SPEED:
                    player.velocity_y = MAX_RISE_SPEED
            else:
                if player.velocity_y < 0:
                    player.velocity_y = 0.0
                player.velocity_y += GRAVITY
                if player.velocity_y > MAX_FALL_SPEED:
                    player.velocity_y = MAX_FALL_SPEED
        
        elif player.mode == MODE_HEAD:
            deadzone_low = 0.85
            deadzone_high = 1.25
            
            if head_y_ratio > deadzone_high:
                target_v = MAX_RISE_SPEED * 0.8
            elif head_y_ratio < deadzone_low:
                target_v = MAX_FALL_SPEED * 0.8
            else:
                target_v = 0.0
                
            player.velocity_y += (target_v - player.velocity_y) * 0.15

        player.y += player.velocity_y

        # Visual tilt of the face based on velocity
        player.angle = max(-30.0, min(70.0, player.velocity_y * 5.0))

    def check_collision(self, player: Player, pipes: List[Pipe]) -> bool:
        """Verifies collision with ceiling, floor, or any pipe."""
        # 1. Ceiling and floor
        if (player.y - player.radius) < 0:
            return True
        if (player.y + player.radius) > (HEIGHT - GROUND_HEIGHT):
            return True

        # 2. Pipes
        for pipe in pipes:
            rx = pipe.x
            # Upper pipe
            if circle_rectangle_collision(player.x, player.y, player.radius,
                                          rx, 0, pipe.width, pipe.gap_y):
                return True
            # Lower pipe
            y_lower_start = pipe.gap_y + pipe.gap
            lower_height = (HEIGHT - GROUND_HEIGHT) - y_lower_start
            if circle_rectangle_collision(player.x, player.y, player.radius,
                                          rx, y_lower_start, pipe.width, lower_height):
                return True
                
        return False
