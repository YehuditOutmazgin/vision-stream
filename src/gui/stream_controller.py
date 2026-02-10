"""
Stream Controller - Handles all stream-related operations.
Manages stream lifecycle, reconnection, and error handling.
"""

import os
from PySide6.QtCore import QTimer
from core.stream_engine import RTSPStreamEngine
from core.reconnection_manager import ReconnectionManager, StreamState
from utils.url_validator import URLValidator
from utils.error_handler import ErrorHandler
from utils.logger import get_logger

logger = get_logger()


class StreamController:
    """Controls stream operations and reconnection logic."""
    
    def __init__(self, on_frame_ready, on_fps_updated, on_state_changed, on_reconnect_attempt):
        self.engine = None
        self.reconnection_manager = ReconnectionManager()
        self.current_url = None
        self.reconnect_timer = QTimer()
        self.reconnect_timer.timeout.connect(self._attempt_reconnect)
        
        # Callbacks
        self.on_frame_ready = on_frame_ready
        self.on_fps_updated = on_fps_updated
        self.on_state_changed = on_state_changed
        self.on_reconnect_attempt = on_reconnect_attempt
        
        # Setup reconnection manager callbacks
        self.reconnection_manager.on_state_changed = self._on_reconnection_state_changed
        self.reconnection_manager.on_reconnect_attempt = self._on_reconnect_attempt_callback
    
    def validate_and_start(self, url: str) -> tuple[bool, str]:
        """
        Validate URL and start stream.
        
        Returns:
            (success: bool, error_message: str)
        """
        url = url.strip()
        
        if not url:
            return False, "Please enter a URL, select a file, or connect a camera."
        
        is_local = os.path.exists(url) or "video=" in url
        
        if not is_local:
            is_valid, error_msg = URLValidator.validate(url)
            if not is_valid:
                return False, f"Invalid URL: {error_msg}"
        
        self.current_url = url
        self.reconnection_manager.start_connection()
        self._attempt_reconnect()
        return True, ""
    
    def _attempt_reconnect(self):
        """Attempt to reconnect to the stream."""
        if not self.current_url:
            return
        
        self.engine = RTSPStreamEngine(self.current_url)
        self.engine.frame_ready.connect(self.on_frame_ready)
        self.engine.fps_updated.connect(self.on_fps_updated)
        self.engine.error_occurred.connect(self._on_stream_error)
        
        if self.engine.start():
            self.reconnection_manager.connection_success()
            # Emit playing state to UI
            self.on_state_changed("playing", None)
        else:
            self.reconnection_manager.connection_failed("Failed to start stream")
    
    def _on_stream_error(self, error_msg):
        """Handle stream errors with reconnection logic."""
        if "timeout" in error_msg.lower() or "no frames" in error_msg.lower():
            self.reconnection_manager.connection_failed(error_msg)
        else:
            # For other errors, trigger error callback
            self.on_state_changed("error", error_msg)
    
    def _on_reconnection_state_changed(self, state):
        """Handle reconnection state changes."""
        # Only emit state changes for CONNECTING and ERROR states
        # PLAYING state is handled directly in _attempt_reconnect
        if state.value == "connecting":
            self.on_state_changed(state.value, None)
        elif state.value == "error":
            self.on_state_changed(state.value, None)
    
    def _on_reconnect_attempt_callback(self, attempt, wait_time):
        """Handle reconnection attempt."""
        self.on_reconnect_attempt(attempt, wait_time)
        if wait_time > 0:
            self.reconnect_timer.start(int(wait_time * 1000))
        else:
            self._attempt_reconnect()
    
    def stop(self):
        """Stop the stream."""
        self.reconnect_timer.stop()
        self.reconnection_manager.user_stop()
        
        if self.engine:
            self.engine.stop()
            self.engine = None
        
        self.current_url = None
    
    def get_retry_info(self):
        """Get current retry information."""
        return self.reconnection_manager.get_retry_info()
