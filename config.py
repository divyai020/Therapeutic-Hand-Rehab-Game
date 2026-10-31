"""
Configuration and constants for Therapeutic Hand Coordination & Rehabilitation Game.
"""

# Window geometry
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
FPS = 60

# Camera capture resolution
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Visual Palette
COLOR_BG = (18, 24, 38)
COLOR_PANEL = (28, 36, 54)
COLOR_PANEL_BORDER = (48, 60, 84)
COLOR_CARD = (24, 32, 48)
COLOR_TEXT_PRIMARY = (250, 250, 252)
COLOR_TEXT_MUTED = (160, 172, 192)
COLOR_ACCENT_TEAL = (20, 184, 166)
COLOR_ACCENT_EMERALD = (16, 185, 129)

# Simple, clear color palette: Red, Green, Blue, Yellow, Orange, Purple
TOKEN_PALETTE = [
    {
        "name": "Red",
        "color": (235, 65, 65),
        "glow": (255, 110, 110),
        "target_color": (150, 25, 25)
    },
    {
        "name": "Green",
        "color": (40, 185, 105),
        "glow": (80, 220, 145),
        "target_color": (15, 100, 50)
    },
    {
        "name": "Blue",
        "color": (45, 140, 240),
        "glow": (100, 180, 255),
        "target_color": (15, 75, 150)
    },
    {
        "name": "Yellow",
        "color": (245, 185, 25),
        "glow": (255, 215, 80),
        "target_color": (150, 105, 10)
    },
    {
        "name": "Orange",
        "color": (245, 130, 35),
        "glow": (255, 170, 80),
        "target_color": (160, 75, 15)
    },
    {
        "name": "Purple",
        "color": (165, 80, 235),
        "glow": (205, 130, 255),
        "target_color": (100, 35, 160)
    }
]

# Rehabilitation Sensitivity Presets
DIFFICULTY_PRESETS = {
    "Easy": {
        "description": "Easy: 3 Large Balls • Flexible Grasp • Low Strain",
        "pinch_threshold_grab": 75,
        "pinch_threshold_release": 105,
        "pinch_ratio_grab": 0.52,
        "token_radius": 46,
        "target_radius": 70,
        "smoothing_factor": 0.50,
        "token_count": 3,
    },
    "Medium": {
        "description": "Medium: 4 Balls • Standard Pinch • Active Coordination",
        "pinch_threshold_grab": 60,
        "pinch_threshold_release": 85,
        "pinch_ratio_grab": 0.42,
        "token_radius": 38,
        "target_radius": 58,
        "smoothing_factor": 0.45,
        "token_count": 4,
    },
    "Hard": {
        "description": "Hard: 6 Precision Balls • Tight Grasp • Dexterity & Endurance",
        "pinch_threshold_grab": 44,
        "pinch_threshold_release": 65,
        "pinch_ratio_grab": 0.32,
        "token_radius": 28,
        "target_radius": 46,
        "smoothing_factor": 0.35,
        "token_count": 6,
    }
}

# Compatibility aliases
DIFFICULTY_PRESETS["Gentle"] = DIFFICULTY_PRESETS["Easy"]
DIFFICULTY_PRESETS["Standard"] = DIFFICULTY_PRESETS["Medium"]
DIFFICULTY_PRESETS["Precision"] = DIFFICULTY_PRESETS["Hard"]

# Full 21-landmark hand skeleton connections
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index finger
    (5, 9), (9, 10), (10, 11), (11, 12),   # Middle finger
    (9, 13), (13, 14), (14, 15), (15, 16), # Ring finger
    (13, 17), (17, 18), (18, 19), (19, 20),# Pinky
    (0, 17)                                # Palm base
]
