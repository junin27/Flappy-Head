import os

# Screen Configurations
WIDTH = 1920
HEIGHT = 1080
GROUND_HEIGHT = 130

# MediaPipe Detection
DETECTION_WIDTH = 320
DETECTION_HEIGHT = 240
MOUTH_OPEN_THRESHOLD = 0.045

# Physics
GRAVITY = 0.55
IMPULSE = -5.0
MAX_FALL_SPEED = 11
MAX_RISE_SPEED = -9

# Pipes
PIPE_WIDTH = 150
PIPE_GAP = 360
PIPE_SPEED = 7
PIPE_INTERVAL = 95

# Player
FACE_RADIUS = 95
PLAYER_X = 380

# Colors (BGR format for OpenCV)
COLOR_SKY_TOP = (235, 180, 100)
COLOR_SKY_BASE = (255, 230, 170)
COLOR_GROUND = (60, 165, 105)
COLOR_GROUND_DETAIL = (40, 120, 75)
COLOR_GROUND_LINE = (30, 90, 55)
COLOR_PIPE_BODY = (40, 190, 60)
COLOR_PIPE_BORDER = (20, 110, 30)
COLOR_PIPE_TOP = (60, 220, 80)
COLOR_CLOUD = (250, 250, 250)
COLOR_TEXT = (255, 255, 255)
COLOR_SHADOW = (20, 20, 20)
COLOR_PANEL = (35, 35, 45)

# File Paths
LEADERBOARD_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "leaderboard.csv"
)
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/1/face_landmarker.task"
)
MODEL_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "face_landmarker.task"
)

# Game States
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"
STATE_LEADERBOARD = "LEADERBOARD"

# Control Modes
MODE_MOUTH = "mouth"
MODE_HEAD = "head"

# Difficulty Parameters
DIFFICULTY_STEP_TIME = 20.0
DIFFICULTY_MAX_LEVEL = 6
PIPE_INTERVAL_MINIMUM = 35
DIFFICULTY_INTERVAL_DECREMENT = 10
DIFFICULTY_SPEED_INCREMENT = 1.5

# Menu Animation
MENU_FLOAT_FREQUENCY = 5e6
MENU_FLOAT_AMPLITUDE = 12.0
