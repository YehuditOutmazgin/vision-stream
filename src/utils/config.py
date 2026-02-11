"""
Configuration - Application settings and constants.
"""

from pathlib import Path


class Config:
    """Application configuration constants."""

    # Application info
    APP_NAME = "VisionStream"
    APP_VERSION = "1.0.0"
    
    # Paths
    LOG_DIR = Path("logs")
    
    # RTSP Configuration
    RTSP_TRANSPORT = "tcp"  # TCP for reliability
    RTSP_TIMEOUT = 10  # seconds - initial connection timeout
    
    # Frame Buffer Configuration
    FRAME_BUFFER_SIZE = 1  # Single-frame buffer (Latest Frame Policy)
    WATCHDOG_TIMEOUT = 2.5  # seconds - no frames timeout
    WATCHDOG_CHECK_INTERVAL = 0.1  # seconds - check every 100ms
    
    # Reconnection Configuration
    MAX_RECONNECTION_ATTEMPTS = 5
    RECONNECTION_DELAYS = [0, 2, 5, 10, 30]  # seconds between attempts
    
    # FFmpeg Configuration
    FFMPEG_OPTIONS = {
        "rtsp_transport": "tcp",      # Force TCP for reliability (Req 6.9)
        "fflags": "nobuffer",         # Disable internal buffering (Req 6.10)
        "flags": "low_delay",         # Enable low-delay mode (Req 6.10)
        "strict": "experimental",     # Allow experimental codecs
        "allowed_media_types": "video",  # Ignore audio for performance
    }
    
    # Video Configuration
    SUPPORTED_CODECS = ["h264", "hevc", "h265", "mpeg4", "msmpeg4v3", "h263"]
    TARGET_PIXEL_FORMAT = "rgb24"
    STRICT_LATEST_FRAME = True  # Strict Latest Frame Policy (Req 6.7)
    
    # UI Configuration
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    MIN_WINDOW_WIDTH = 640
    MIN_WINDOW_HEIGHT = 480
    # Default webcam device string for Windows/DirectShow
    # Can be customized to camera name in system, e.g.: "video=Integrated Camera"
    DEFAULT_WEBCAM_DEVICE = "video=Integrated Camera"
    
    # FPS Display
    FPS_UPDATE_INTERVAL = 1000  # milliseconds
    FPS_DISPLAY_POSITION = "top-right"  # Position on screen
    
    # Latency Target
    GLASS_TO_GLASS_LATENCY_TARGET = 500  # milliseconds
    
    # Logging
    LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOG_LEVEL = "DEBUG"
    
    # Error Messages
    ERROR_MESSAGES = {
        "EMPTY_URL": "URL cannot be empty",
        "INVALID_URL_FORMAT": "Invalid URL format. Expected: rtsp://host:port/path",
        "CONNECTION_TIMEOUT": "Connection timeout - server not responding",
        "CONNECTION_REFUSED": "Connection refused - server offline or port closed",
        "UNSUPPORTED_CODEC": "Unsupported video codec",
        "NETWORK_ERROR": "Network error occurred",
        "STREAM_INTERRUPTED": "Stream interrupted",
        "MAX_RETRIES_EXCEEDED": "Maximum reconnection attempts exceeded",
    }


# Global config instance
_config = Config()
