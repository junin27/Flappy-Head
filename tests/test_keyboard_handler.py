import unittest
from typing import List
from src.ui.keyboard_handler import handle_keys
from src.models.player import Player
from src.engine.game import GameEngine
from src.ui.input_handler import TextInputHandler
from src.data.leaderboard import LeaderboardRepository
from src.config import (
    STATE_MENU, STATE_PLAYING, STATE_GAME_OVER, STATE_LEADERBOARD,
    MODE_HEAD, MODE_MOUTH
)

class TestKeyboardHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.player = Player(y=300.0)
        self.engine = GameEngine()
        self.input_handler = TextInputHandler()
        self.search_handler = TextInputHandler()
        self.test_csv = "test_keyboard_leaderboard.csv"
        self.repo = LeaderboardRepository(self.test_csv)
        self.repo.clear()
        self.screen_mode_called = False
        self.screen_mode_value = ""

    def tearDown(self) -> None:
        import os
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)

    def mock_apply_screen_mode(self, mode: str) -> None:
        self.screen_mode_called = True
        self.screen_mode_value = mode

    def test_menu_to_playing_transition(self) -> None:
        state, pipes, pipe_counter, screen_idx, scroll = handle_keys(
            ord(' '), STATE_MENU, self.player, self.engine, self.input_handler,
            [], 0, 0, 0, self.search_handler, self.repo, self.mock_apply_screen_mode
        )
        self.assertEqual(state, STATE_PLAYING)
        self.assertEqual(self.player.velocity_y, 0.0)

    def test_menu_mode_toggle(self) -> None:
        self.player.mode = MODE_MOUTH
        state, _, _, _, _ = handle_keys(
            ord('m'), STATE_MENU, self.player, self.engine, self.input_handler,
            [], 0, 0, 0, self.search_handler, self.repo, self.mock_apply_screen_mode
        )
        self.assertEqual(self.player.mode, MODE_HEAD)

        handle_keys(
            ord('m'), STATE_MENU, self.player, self.engine, self.input_handler,
            [], 0, 0, 0, self.search_handler, self.repo, self.mock_apply_screen_mode
        )
        self.assertEqual(self.player.mode, MODE_MOUTH)

    def test_menu_to_leaderboard(self) -> None:
        state, _, _, _, _ = handle_keys(
            ord('l'), STATE_MENU, self.player, self.engine, self.input_handler,
            [], 0, 0, 0, self.search_handler, self.repo, self.mock_apply_screen_mode
        )
        self.assertEqual(state, STATE_LEADERBOARD)

    def test_menu_tab_activates_input(self) -> None:
        self.assertFalse(self.input_handler.active)
        state, _, _, _, _ = handle_keys(
            9, STATE_MENU, self.player, self.engine, self.input_handler,
            [], 0, 0, 0, self.search_handler, self.repo, self.mock_apply_screen_mode
        )
        self.assertTrue(self.input_handler.active)

    def test_fullscreen_toggle(self) -> None:
        # pressing 'f' toggles screen mode
        self.assertFalse(self.screen_mode_called)
        _, _, _, screen_idx, _ = handle_keys(
            ord('f'), STATE_MENU, self.player, self.engine, self.input_handler,
            [], 0, 0, 0, self.search_handler, self.repo, self.mock_apply_screen_mode
        )
        self.assertTrue(self.screen_mode_called)
        self.assertEqual(self.screen_mode_value, "windowed") # screen idx 1
        self.assertEqual(screen_idx, 1)

    def test_leaderboard_back_to_menu(self) -> None:
        state, _, _, _, _ = handle_keys(
            ord(' '), STATE_LEADERBOARD, self.player, self.engine, self.input_handler,
            [], 0, 0, 0, self.search_handler, self.repo, self.mock_apply_screen_mode
        )
        self.assertEqual(state, STATE_MENU)

    def test_game_over_back_to_menu(self) -> None:
        state, _, _, _, _ = handle_keys(
            ord(' '), STATE_GAME_OVER, self.player, self.engine, self.input_handler,
            [], 0, 0, 0, self.search_handler, self.repo, self.mock_apply_screen_mode
        )
        self.assertEqual(state, STATE_MENU)

if __name__ == "__main__":
    unittest.main()
