import unittest
from src.vision.face_tracker import FaceTracker

class TestFaceMath(unittest.TestCase):
    # Simulating a mock landmark
    class MockLandmark:
        def __init__(self, x: float, y: float) -> None:
            self.x = x
            self.y = y

    def test_calculate_metrics_closed_mouth(self) -> None:
        # 0 to 152 to have indexes (we need 10, 13, 14, 152)
        lm = {i: self.MockLandmark(0.0, 0.0) for i in range(153)}
        
        lm[10] = self.MockLandmark(0.5, 0.1)  # forehead 
        lm[152] = self.MockLandmark(0.5, 0.9) # chin 
        lm[4] = self.MockLandmark(0.5, 0.5)   # nose in middle
        
        lm[13] = self.MockLandmark(0.5, 0.50)
        lm[14] = self.MockLandmark(0.5, 0.51)

        ratio, pitch_ratio = FaceTracker.calculate_metrics(lm)
        self.assertAlmostEqual(ratio, 0.01 / 0.8)
        self.assertAlmostEqual(pitch_ratio, 1.0) # 0.4 / 0.4 = 1.0

    def test_calculate_metrics_open_mouth(self) -> None:
        lm = {i: self.MockLandmark(0.0, 0.0) for i in range(153)}
        
        lm[10] = self.MockLandmark(0.5, 0.1) 
        lm[152] = self.MockLandmark(0.5, 0.9) 
        lm[4] = self.MockLandmark(0.5, 0.7) # nose closer to chin (head tilted down)
        
        lm[13] = self.MockLandmark(0.5, 0.45) 
        lm[14] = self.MockLandmark(0.5, 0.55)

        ratio, pitch = FaceTracker.calculate_metrics(lm)
        self.assertAlmostEqual(ratio, 0.10 / 0.8)
        self.assertAlmostEqual(pitch, 0.2 / 0.6) # head tilted down has pitch < 1.0

if __name__ == "__main__":
    unittest.main()
