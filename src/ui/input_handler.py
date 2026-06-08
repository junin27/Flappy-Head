class TextInputHandler:
    def __init__(self, limit: int = 15) -> None:
        self.text: str = ""
        self.limit: int = limit
        self.active: bool = False

    def process_key(self, key: int) -> bool:
        """
        Processes keys from cv2.waitKey.
        Returns True if Enter (submit), otherwise False.
        """
        if not self.active:
            return False
            
        if key in (13, 9): # Enter or TAB
            self.active = False
            return True
        elif key == 8: # Backspace
            self.text = self.text[:-1]
        elif 32 <= key <= 126: # Printable characters
            if len(self.text) < self.limit:
                self.text += chr(key)
        return False
