import unittest
from src.ui.input_handler import TextInputHandler

class TestTextInputHandler(unittest.TestCase):
    def setUp(self) -> None:
        self.handler = TextInputHandler()
        self.handler.active = True
        
    def test_type_letters(self) -> None:
        self.handler.process_key(ord('A'))
        self.handler.process_key(ord('b'))
        self.assertEqual(self.handler.text, "Ab")
        
    def test_backspace(self) -> None:
        self.handler.text = "Ana"
        self.handler.process_key(8) # ASCII backspace
        self.assertEqual(self.handler.text, "An")
        
    def test_size_limit(self) -> None:
        self.handler.text = "123456789012345"
        self.handler.process_key(ord('6')) # default limit 15
        self.assertEqual(self.handler.text, "123456789012345")

    def test_deactivate_with_tab(self) -> None:
        self.handler.process_key(9) # TAB
        self.assertFalse(self.handler.active)
        
if __name__ == "__main__":
    unittest.main()
