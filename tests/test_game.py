import unittest
from src.engine.game import GameEngine
from src.models.player import Player
from src.models.pipe import Pipe
from src.config import (
    HEIGHT, GROUND_HEIGHT, MODE_MOUTH, MODE_HEAD,
    MAX_RISE_SPEED, MAX_FALL_SPEED, PLAYER_X, FACE_RADIUS
)

class TestGameEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = GameEngine()

    def test_state_initialization(self) -> None:
        self.assertEqual(self.engine.survival_time, 0.0)
        self.assertFalse(self.engine.collided)

    def test_update_physics_mouth(self) -> None:
        # Test gravity when mouth closed
        player = Player(y=500.0, mode=MODE_MOUTH, mouth_open=False)
        self.engine.update_physics(player, head_y_ratio=0.5)
        self.assertTrue(player.velocity_y > 0)
        self.assertTrue(player.y > 500.0)

        # Test jump when mouth open
        player = Player(y=500.0, mode=MODE_MOUTH, mouth_open=True)
        self.engine.update_physics(player, head_y_ratio=0.5)
        self.assertTrue(player.velocity_y < 0)
        self.assertTrue(player.y < 500.0)

    def test_update_physics_head(self) -> None:
        # pitch_ratio > 1.25 -> rising
        player = Player(y=500.0, mode=MODE_HEAD)
        self.engine.update_physics(player, head_y_ratio=1.3)
        self.assertTrue(player.velocity_y < 0) # rising

        # pitch_ratio < 0.85 -> falling
        player = Player(y=500.0, mode=MODE_HEAD)
        self.engine.update_physics(player, head_y_ratio=0.8)
        self.assertTrue(player.velocity_y > 0) # falling

    def test_difficulty_scales_with_time(self) -> None:
        # Level 0 (0 to 19s)
        self.engine.survival_time = 10.0
        interval_0, speed_0 = self.engine.get_difficulty_parameters()
        
        # Level 1 (20 to 39s)
        self.engine.survival_time = 25.0
        interval_1, speed_1 = self.engine.get_difficulty_parameters()
        
        # Interval must decrease (spawns faster)
        self.assertTrue(interval_1 < interval_0)
        # Speed must increase
        self.assertTrue(speed_1 > speed_0)

    def test_collision_ceiling_floor(self) -> None:
        player_ceiling = Player(y=0.0) # radius is 95, so it hits ceiling
        player_floor = Player(y=HEIGHT)
        player_middle = Player(y=HEIGHT / 2)

        self.assertTrue(self.engine.check_collision(player_ceiling, []))
        self.assertTrue(self.engine.check_collision(player_floor, []))
        self.assertFalse(self.engine.check_collision(player_middle, []))

    def test_collision_pipes(self) -> None:
        player = Player(y=500.0) # x = 380, radius = 95
        # Pipe far ahead, no collision
        safe_pipe = Pipe(x=1000.0, gap_y=400)
        self.assertFalse(self.engine.check_collision(player, [safe_pipe]))

        # Pipe directly overlapping player, hitting top tube
        colliding_pipe = Pipe(x=380.0, gap_y=600)
        self.assertTrue(self.engine.check_collision(player, [colliding_pipe]))

    def test_increment_time(self) -> None:
        self.engine.update_time(0.1) # delta = 0.1s
        self.assertAlmostEqual(self.engine.survival_time, 0.1)

if __name__ == "__main__":
    unittest.main()
