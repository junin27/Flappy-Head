from dataclasses import dataclass
from src.config import PIPE_WIDTH, PIPE_GAP

@dataclass
class Pipe:
    x: float
    gap_y: int
    passed: bool = False
    
    @property
    def width(self) -> int:
        return PIPE_WIDTH
    
    @property
    def gap(self) -> int:
        return PIPE_GAP
