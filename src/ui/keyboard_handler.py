import logging
from typing import List, Tuple, Callable
from src.config import (
    HEIGHT, STATE_MENU, STATE_PLAYING, STATE_GAME_OVER, STATE_LEADERBOARD,
    MODE_HEAD, MODE_MOUTH
)
from src.models.player import Player
from src.models.pipe import Pipe
from src.engine.game import GameEngine
from src.ui.input_handler import TextInputHandler
from src.data.leaderboard import LeaderboardRepository

logger = logging.getLogger(__name__)
SCREEN_MODES = ["fullscreen", "windowed", "borderless"]

def _handle_menu_keys(
    key: int,
    char: str,
    player: Player,
    engine: GameEngine,
    input_handler: TextInputHandler
) -> Tuple[str, List[Pipe], int]:
    """Handles key inputs specifically for the menu screen."""
    if input_handler.active:
        input_handler.process_key(key)
        return STATE_MENU, [], 0
        
    if key == 9:  # TAB
        input_handler.active = True
    elif char == 'm':
        player.mode = MODE_HEAD if player.mode == MODE_MOUTH else MODE_MOUTH
    elif char == 'l':
        return STATE_LEADERBOARD, [], 0
    elif key == ord(' '):
        engine.survival_time = 0.0
        player.y = HEIGHT // 2
        player.velocity_y = 0.0
        player.angle = 0.0
        logger.info(f"Match started in mode: {player.mode}")
        return STATE_PLAYING, [], 0
        
    return STATE_MENU, [], 0

def _handle_leaderboard_keys(
    key: int,
    char: str,
    scroll_offset: int,
    search_handler: TextInputHandler,
    repo: LeaderboardRepository
) -> Tuple[str, int]:
    """Handles key inputs specifically for the leaderboard screen."""
    if search_handler.active:
        search_handler.process_key(key)
        records_len = len(repo.filter_by_name(search_handler.text))
        scroll_offset = min(scroll_offset, max(0, records_len - 10))
        return STATE_LEADERBOARD, scroll_offset
        
    if key == 9:  # TAB
        search_handler.active = True
    elif char == 'w' or key == 82:  # W or UP arrow
        scroll_offset = max(0, scroll_offset - 1)
    elif char == 's' or key == 84:  # S or DOWN arrow
        records_len = len(repo.filter_by_name(search_handler.text))
        scroll_offset = min(scroll_offset + 1, max(0, records_len - 10))
    elif char == 'r':
        repo.clear()
        scroll_offset = 0
        search_handler.text = ""
        logger.info("Leaderboard data cleared!")
    elif key == ord(' '):
        search_handler.text = ""
        return STATE_MENU, 0
        
    return STATE_LEADERBOARD, scroll_offset

def handle_keys(
    key: int,
    state: str,
    player: Player,
    engine: GameEngine,
    input_handler: TextInputHandler,
    pipes: List[Pipe],
    pipe_counter: int,
    screen_mode_idx: int,
    scroll_offset: int,
    search_handler: TextInputHandler,
    repo: LeaderboardRepository,
    apply_screen_mode_fn: Callable[[str], None]
) -> Tuple[str, List[Pipe], int, int, int]:
    """
    Main keyboard input handler for Flappy Head.
    Dispatches key handling to subfunctions based on active state.
    """
    char = ""
    try:
        if 32 <= key <= 126:
            char = chr(key).lower()
    except Exception:
        pass

    if not input_handler.active and not search_handler.active and char == 'f':
        screen_mode_idx = (screen_mode_idx + 1) % len(SCREEN_MODES)
        apply_screen_mode_fn(SCREEN_MODES[screen_mode_idx])
        logger.info(f"Screen mode changed to: {SCREEN_MODES[screen_mode_idx]}")

    if state == STATE_MENU:
        state, pipes, pipe_counter = _handle_menu_keys(key, char, player, engine, input_handler)
    elif state == STATE_GAME_OVER:
        if key == ord(' '):
            state = STATE_MENU
    elif state == STATE_LEADERBOARD:
        state, scroll_offset = _handle_leaderboard_keys(key, char, scroll_offset, search_handler, repo)

    return state, pipes, pipe_counter, screen_mode_idx, scroll_offset
