import sys
import os

# Adds the current directory to the system path to allow importing src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import run_game

if __name__ == "__main__":
    run_game()
