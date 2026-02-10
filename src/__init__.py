"""
VisionStream RTSP Viewer - Main package.
High-performance desktop video player for RTSP streams with ultra-low latency.
"""

__version__ = "1.0.0"
__author__ = "VisionStream Team"
__description__ = "Professional RTSP video player with automatic reconnection and real-time monitoring"

# Import main components for easy access
from .core import RTSPStreamEngine, ReconnectionManager, StreamState, FrameBuffer
from .utils import (
    Config,
    get_logger,
    ErrorHandler,
    URLValidator,
    ErrorType,
)
from .gui import (
    VideoDisplay,
    ControlPanel,
    Header,
    StreamController,
    UIManager,
    COLORS,
    MAIN_STYLESHEET,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__description__",
    # Core components
    "RTSPStreamEngine",
    "ReconnectionManager",
    "StreamState",
    "FrameBuffer",
    # Utils
    "Config",
    "get_logger",
    "ErrorHandler",
    "URLValidator",
    "ErrorType",
    # GUI components
    "VideoDisplay",
    "ControlPanel",
    "Header",
    "StreamController",
    "UIManager",
    "COLORS",
    "MAIN_STYLESHEET",
]
