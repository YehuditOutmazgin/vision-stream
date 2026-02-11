"""
Logger - Comprehensive logging system for VisionStream.
Thread-safe singleton with unified file output and console display.
"""

import logging
import threading
from datetime import datetime
from pathlib import Path


class VisionStreamLogger:
    """
    Thread-safe singleton logger for VisionStream application.
    
    Features:
    - Unified log file (all events in one file)
    - Thread-safe logging from multiple threads
    - Separate console output (INFO level) and file output (DEBUG level)
    - Prevents duplicate handlers on multiple instantiations
    """
    
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, app_name: str = "visionstream"):
        """Implement thread-safe singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, app_name: str = "visionstream"):
        """Initialize logger only once (singleton)."""
        if self._initialized:
            return
        
        self.app_name = app_name
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Create unified logger
        self.logger = self._setup_logger()
        self._initialized = True

    def _setup_logger(self) -> logging.Logger:
        """
        Setup unified logger with file and console handlers.
        Prevents duplicate handlers by checking existing handlers.
        """
        logger = logging.getLogger(self.app_name)
        
        # Prevent duplicate handlers if logger already configured
        if logger.handlers:
            return logger
        
        logger.setLevel(logging.DEBUG)
        
        # Log file path with date
        log_file = self.log_dir / f"{self.app_name}_{datetime.now().strftime('%Y-%m-%d')}.log"
        
        # File handler - writes all levels (DEBUG and above)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler - writes only INFO and above (less verbose)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter with thread name for debugging
        formatter = logging.Formatter(
            '[%(asctime)s] %(threadName)s/%(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger

    def log_connection(self, url: str):
        """Log connection event."""
        self.logger.info(f"CONNECT: {url}")

    def log_disconnection(self, reason: str = "User stopped"):
        """Log disconnection event."""
        self.logger.info(f"DISCONNECT: {reason}")

    def log_codec_info(self, codec: str, resolution: str, fps: int):
        """Log codec information."""
        self.logger.info(f"CODEC: {codec}, {resolution}, {fps} FPS")

    def log_timeout(self, seconds: float):
        """Log timeout event."""
        self.logger.warning(f"TIMEOUT: No frames for {seconds}s")

    def log_reconnect_attempt(self, attempt: int, wait_time: int = 0):
        """Log reconnection attempt."""
        if wait_time > 0:
            self.logger.info(f"RECONNECT: Attempt {attempt} (wait {wait_time}s)")
        else:
            self.logger.info(f"RECONNECT: Attempt {attempt} (immediate)")

    def log_reconnect_success(self):
        """Log successful reconnection."""
        self.logger.info("CONNECT: Successfully reconnected")

    def log_error(self, error_type: str, message: str, error_code: str = ""):
        """
        Log error event to unified log file.
        
        Args:
            error_type: Type of error (e.g., CONNECTION_ERROR, CODEC_ERROR)
            message: Error message
            error_code: Optional error code for reference
        """
        error_msg = f"[{error_type}] {message}"
        if error_code:
            error_msg += f" (Code: {error_code})"
        self.logger.error(error_msg)

    def log_validation_error(self, message: str):
        """Log validation error."""
        self.log_error("VALIDATION_ERROR", message)

    def log_connection_error(self, message: str):
        """Log connection error."""
        self.log_error("CONNECTION_ERROR", message)

    def log_codec_error(self, codec: str):
        """Log codec error."""
        self.log_error("CODEC_ERROR", f"Unsupported codec: {codec}")

    def log_ui_event(self, event: str):
        """Log UI event (debug level)."""
        self.logger.debug(f"UI: {event}")

    def log_latency(self, avg_ms: float, window_size: int):
        """
        Log average latency over a sliding window.

        Args:
            avg_ms: Average latency in milliseconds
            window_size: Number of recent frames used for the average
        """
        self.logger.info(f"LATENCY: avg={avg_ms:.2f}ms over last {window_size} frames")


def get_logger() -> VisionStreamLogger:
    """
    Get or create the global logger instance (thread-safe singleton).
    
    Returns:
        VisionStreamLogger: Singleton logger instance
    """
    return VisionStreamLogger()
