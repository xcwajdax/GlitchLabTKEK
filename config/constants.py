"""
Constants and configuration values for Glitch Lab.
"""

# Application metadata
APP_NAME = "Glitch Lab"
APP_VERSION = "1.0"

# Default animation parameters
DEFAULT_ANIM_PARAMS = {
    'pattern_mode': 'every',
    'intensity_mode': 'constant',
    'every_n': 2,
    'random_chance': 50,
    'burst_on': 3,
    'burst_off': 5,
    'pulse_cycles': 3,
    'keyframes': []
}

# Default processing parameters
DEFAULT_MULTIPLIER = 1
DEFAULT_INTENSITY = 0.5
DEFAULT_GLITCH_ENABLED = True

# UI constants
PREVIEW_SIZE = (400, 300)
THUMBNAIL_SIZE = (100, 75)
DEFAULT_FPS = 24

# File extensions supported
SUPPORTED_IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']

# Progress callback messages
PROGRESS_SCANNING = "Skanowanie plików wejściowych..."
PROGRESS_NO_FRAMES = "Nie znaleziono plików klatek."