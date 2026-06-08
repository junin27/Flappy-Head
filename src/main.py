import cv2
import time
import random
import math
import logging
import ctypes
import threading
from typing import List, Tuple, Optional
import numpy as np

from src.config import (
    WIDTH, HEIGHT, STATE_MENU, STATE_PLAYING, STATE_GAME_OVER, STATE_LEADERBOARD,
    MODE_MOUTH, MODE_HEAD, PIPE_INTERVAL, PIPE_SPEED, GROUND_HEIGHT,
    MENU_FLOAT_FREQUENCY, MENU_FLOAT_AMPLITUDE, LEADERBOARD_FILE
)
from src.models.player import Player
from src.models.pipe import Pipe
from src.engine.game import GameEngine
from src.data.leaderboard import LeaderboardRepository
from src.vision.camera import start_camera, CameraThread
from src.vision.face_tracker import FaceTracker
from src.ui.renderer import Renderer
from src.ui.screens import Screens
from src.ui.input_handler import TextInputHandler
from src.ui.keyboard_handler import handle_keys

# Professional Logger Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Screen Modes
SCREEN_MODES = ["fullscreen", "windowed", "borderless"]

def configure_window() -> None:
    """Initializes the game's OpenCV window."""
    cv2.namedWindow("Flappy Head", cv2.WINDOW_NORMAL)

def apply_screen_mode(mode: str) -> None:
    """Applies the specified screen mode to the OpenCV window."""
    if mode == "fullscreen":
        cv2.setWindowProperty("Flappy Head", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    elif mode == "windowed":
        cv2.setWindowProperty("Flappy Head", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Flappy Head", WIDTH, HEIGHT)
    elif mode == "borderless":
        try:
            user32 = ctypes.windll.user32
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
        except Exception:
            screen_width, screen_height = WIDTH, HEIGHT
        cv2.setWindowProperty("Flappy Head", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        cv2.moveWindow("Flappy Head", 0, 0)
        cv2.resizeWindow("Flappy Head", screen_width, screen_height)

def process_tracking(tracker: FaceTracker, player: Player, frame: np.ndarray) -> float:
    """Tracks facial landmarks and updates player state. Returns head_y_ratio."""
    detected, _, mouth_open, face_img, head_y_ratio = tracker.process_frame(frame, player.radius)
    if detected:
        player.face_img = face_img
        player.mouth_open = mouth_open
    else:
        player.face_img = None
        player.mouth_open = False
    return head_y_ratio

def update_logic(
    engine: GameEngine,
    player: Player,
    pipes: List[Pipe],
    pipe_counter: int,
    repo: LeaderboardRepository,
    delta: float,
    head_y_ratio: float
) -> Tuple[str, List[Pipe], int]:
    """Processes game physics, pipe movement, spawning, and collisions."""
    engine.update_time(delta)
    engine.update_physics(player, head_y_ratio)
    
    interval_curr, speed_curr = engine.get_difficulty_parameters()
    
    pipe_counter += 1
    if pipe_counter >= interval_curr:
        pipe_counter = 0
        gap_y = random.randint(70, HEIGHT - GROUND_HEIGHT - 360 - 70)
        pipes.append(Pipe(x=WIDTH + 10, gap_y=gap_y))

    for pipe in pipes:
        pipe.x -= speed_curr
    pipes_filtered = [p for p in pipes if (p.x + p.width) > -10]

    state = STATE_PLAYING
    if engine.check_collision(player, pipes_filtered):
        state = STATE_GAME_OVER
        repo.save_record(player.name or "Anonymous", player.mode, engine.survival_time)
        logger.info(f"Game Over! Survival time: {engine.survival_time:.1f}s")
        
    return state, pipes_filtered, pipe_counter

def render_game(
    renderer: Renderer,
    screens: Screens,
    player: Player,
    pipes: List[Pipe],
    engine: GameEngine,
    repo: LeaderboardRepository,
    input_handler: TextInputHandler,
    state: str,
    ground_offset: float,
    screen_mode: str,
    scroll_offset: int,
    search_handler: TextInputHandler
) -> Tuple[float, np.ndarray]:
    """Creates and draws the entire game visual interface on the canvas."""
    renderer.update_clouds()
    
    if state == STATE_PLAYING:
        _, speed_curr = engine.get_difficulty_parameters()
        ground_offset = (ground_offset + speed_curr) % 28
    else:
        ground_offset = (ground_offset + 1.0) % 28
        
    canvas = renderer.create_base_canvas()
    renderer.draw_scenario(canvas, ground_offset)
    
    if state in (STATE_PLAYING, STATE_GAME_OVER):
        renderer.draw_pipes(canvas, pipes)
        
    if state == STATE_MENU:
        player.y = HEIGHT // 2 + int(math.sin(cv2.getTickCount() / MENU_FLOAT_FREQUENCY) * MENU_FLOAT_AMPLITUDE)
        player.angle = 0.0
        
    if state != STATE_LEADERBOARD:
        renderer.draw_face(canvas, player)

    if state == STATE_MENU:
        screens.draw_menu(canvas, input_handler.text, player.mode, screen_mode, input_handler.active)
        player.name = input_handler.text
    elif state == STATE_PLAYING:
        screens.draw_hud(canvas, engine.survival_time)
    elif state == STATE_GAME_OVER:
        screens.draw_game_over(canvas, engine.survival_time)
    elif state == STATE_LEADERBOARD:
        records = repo.filter_by_name(search_handler.text)
        screens.draw_leaderboard(canvas, records, scroll_offset, search_handler.text, search_handler.active)
        
    return ground_offset, canvas

def _attempt_reconnect(camera_state: dict, on_connected) -> None:
    """Helper to start asynchronous camera reconnect thread."""
    if camera_state["reconnecting"]:
        return
    camera_state["reconnecting"] = True
    
    def reconnect_thread() -> None:
        try:
            new_cap, new_camera = start_camera()
            if new_cap is not None and new_camera is not None:
                on_connected(new_cap, new_camera)
        except Exception:
            pass
        finally:
            camera_state["reconnecting"] = False

    t = threading.Thread(target=reconnect_thread, daemon=True)
    t.start()

def _handle_reconnection(camera: Optional[CameraThread], camera_state: dict, on_camera_connected) -> None:
    """Triggers asynchronous camera reconnection if necessary."""
    if camera is None:
        current_time = time.time()
        if current_time - camera_state["last_reconnect_time"] > 3.0:
            camera_state["last_reconnect_time"] = current_time
            _attempt_reconnect(camera_state, on_camera_connected)

def _setup_game() -> Tuple[Player, dict, int]:
    """Helper to initialize window, player and screen mode index."""
    configure_window()
    apply_screen_mode(SCREEN_MODES[0])
    player = Player(y=HEIGHT // 2)
    camera_state = {"reconnecting": False, "last_reconnect_time": time.time()}
    return player, camera_state, 0

def _cleanup_resources(camera: Optional[CameraThread], cap: Optional[cv2.VideoCapture], tracker: FaceTracker) -> None:
    """Closes and releases all resources."""
    if camera is not None:
        camera.stop()
    if cap is not None:
        cap.release()
    tracker.close()
    cv2.destroyAllWindows()
    logger.info("Resources cleaned up and released.")

def run_game() -> None:
    """Entry point of the main game loop."""
    repo = LeaderboardRepository(LEADERBOARD_FILE)
    engine = GameEngine()
    renderer = Renderer()
    screens = Screens(renderer)
    tracker = FaceTracker()
    input_handler, search_handler = TextInputHandler(limit=15), TextInputHandler(limit=15)
    
    cap, camera = start_camera()
    player, camera_state, screen_mode_idx = _setup_game()
    player.webcam_available = (camera is not None)

    def on_camera_connected(new_cap: cv2.VideoCapture, new_camera: CameraThread) -> None:
        nonlocal cap, camera
        cap, camera = new_cap, new_camera
        player.webcam_available = True
        logger.info("Webcam connected and initialized in real-time!")

    state, pipes, pipe_counter, ground_offset, scroll_offset = STATE_MENU, [], 0, 0.0, 0
    prev_tick = cv2.getTickCount()
    logger.info("Flappy Head successfully initialized!")

    frame_count = 0
    try:
        while True:
            if cv2.getWindowProperty("Flappy Head", cv2.WND_PROP_VISIBLE) < 1:
                break
            delta = (cv2.getTickCount() - prev_tick) / cv2.getTickFrequency()
            prev_tick = cv2.getTickCount()

            _handle_reconnection(camera, camera_state, on_camera_connected)

            frame = camera.last_frame if camera is not None else None
            player.webcam_available = (camera is not None and frame is not None)
            
            if frame is None:
                head_y_ratio = 0.5
                player.face_img = None
                player.mouth_open = False
                cv2.waitKey(1)
            else:
                head_y_ratio = process_tracking(tracker, player, frame)

            if state == STATE_PLAYING:
                state, pipes, pipe_counter = update_logic(
                    engine, player, pipes, pipe_counter, repo, delta, head_y_ratio
                )

            ground_offset, canvas = render_game(
                renderer, screens, player, pipes, engine, repo, input_handler, state,
                ground_offset, SCREEN_MODES[screen_mode_idx], scroll_offset, search_handler
            )

            cv2.imshow("Flappy Head", canvas)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
                
            state, pipes, pipe_counter, screen_mode_idx, scroll_offset = handle_keys(
                key, state, player, engine, input_handler, pipes, pipe_counter,
                screen_mode_idx, scroll_offset, search_handler, repo, apply_screen_mode
            )
    except KeyboardInterrupt:
        pass
    finally:
        _cleanup_resources(camera, cap, tracker)

if __name__ == "__main__":
    run_game()
