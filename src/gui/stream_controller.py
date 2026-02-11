"""
Stream Controller - Handles all stream-related operations.
Manages stream lifecycle, reconnection, and error handling.
"""

import os
from PySide6.QtCore import QTimer, QThread, Signal, QObject
from core.stream_engine import RTSPStreamEngine
from core.reconnection_manager import ReconnectionManager, StreamState
from utils.url_validator import URLValidator
from utils.error_handler import ErrorHandler
from utils.logger import get_logger

logger = get_logger()


class ConnectionThread(QThread):
    """Thread for handling connection attempts without blocking UI."""
    connection_success = Signal()
    connection_failed = Signal(str)
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self._stopped = False
        self.setTerminationEnabled(True)
    
    def run(self):
        """Attempt connection in background thread."""
        if self._stopped:
            return
        
        try:
            success = self.engine.start()
            if self._stopped:
                # If stopped during connection, stop the engine
                self.engine.stop()
                return
            
            if success:
                self.connection_success.emit()
            else:
                self.connection_failed.emit("Failed to start stream")
        except Exception as e:
            if not self._stopped:
                self.connection_failed.emit(str(e))
    
    def stop(self):
        """Stop the connection attempt."""
        self._stopped = True
        if self.engine:
            self.engine.interrupt_event.set()


class StreamController:
    """Controls stream operations and reconnection logic."""
    
    def __init__(self, on_frame_ready, on_fps_updated, on_state_changed, on_reconnect_attempt):
        self.engine = None
        self.connection_thread = None
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
        return True, ""
    
    def start_connection(self):
        """Start connection attempt after UI update."""
        self.reconnection_manager.start_connection()
        # Use QTimer to defer connection attempt, allowing UI to update first
        QTimer.singleShot(10, self._attempt_reconnect)
    
    def _attempt_reconnect(self):
        """Attempt to reconnect to the stream in background thread."""
        if not self.current_url:
            return
        
        # Stop any existing connection thread and WAIT for it
        if self.connection_thread:
            self.connection_thread.stop()
            if self.connection_thread.isRunning():
                if self.engine:
                    self.engine.interrupt_event.set()
                self.connection_thread.quit()
                if not self.connection_thread.wait(3000):
                    self.connection_thread.terminate()
                    self.connection_thread.wait(1000)
            try:
                self.connection_thread.connection_success.disconnect()
                self.connection_thread.connection_failed.disconnect()
            except:
                pass
            self.connection_thread = None
        
        # Stop existing engine if any
        if self.engine:
            try:
                self.engine.frame_ready.disconnect()
                self.engine.fps_updated.disconnect()
                self.engine.error_occurred.disconnect()
            except:
                pass
            self.engine.stop()
            self.engine = None
        
        self.engine = RTSPStreamEngine(self.current_url)
        self.engine.frame_ready.connect(self.on_frame_ready)
        self.engine.fps_updated.connect(self.on_fps_updated)
        self.engine.error_occurred.connect(self._on_stream_error)
        
        # Start connection in background thread
        self.connection_thread = ConnectionThread(self.engine)
        self.connection_thread.connection_success.connect(self._on_connection_success)
        self.connection_thread.connection_failed.connect(self._on_connection_failed)
        self.connection_thread.finished.connect(self.connection_thread.deleteLater)
        self.connection_thread.start()
    
    def _on_connection_success(self):
        """Handle successful connection."""
        self.reconnection_manager.connection_success()
        self.on_state_changed("playing", None)
    
    def _on_connection_failed(self, error_msg):
        """Handle failed connection."""
        # Don't show error immediately - let reconnection manager handle retries
        self.reconnection_manager.connection_failed(error_msg)
    
    def _on_stream_error(self, error_msg):
        """Handle stream errors."""
        # Ignore errors if we're not running or already in error state
        if not self.current_url or self.reconnection_manager.state == StreamState.ERROR:
            return
        self.reconnection_manager.connection_failed(error_msg)
        # Don't change UI to error - let reconnection manager handle it
    
    def _on_reconnection_state_changed(self, state):
        """Handle reconnection state changes."""
        if state.value == "connecting":
            self.on_state_changed(state.value, None)
        elif state.value == "error":
            # Only show error when all retries are exhausted
            self.reconnect_timer.stop()
            self.on_state_changed(state.value, "Connection failed")

    
    def _on_reconnect_attempt_callback(self, attempt, wait_time):
        """Handle reconnection attempt."""
        self.on_reconnect_attempt(attempt, wait_time)
        if wait_time > 0:
            self.reconnect_timer.start(int(wait_time * 1000))
        else:
            self._attempt_reconnect()
    
    def stop(self):
        """Stop the stream."""
        self.current_url = None
        self.reconnect_timer.stop()
        self.reconnection_manager.user_stop()
        
        # Stop connection thread
        if self.connection_thread:
            try:
                self.connection_thread.stop()
                if self.connection_thread.isRunning():
                    self.connection_thread.quit()
                    if not self.connection_thread.wait(3000):
                        self.connection_thread.terminate()
                        self.connection_thread.wait(1000)
            except RuntimeError:
                pass  # Thread already deleted
            finally:
                self.connection_thread = None
        
        if self.engine:
            try:
                self.engine.frame_ready.disconnect()
                self.engine.fps_updated.disconnect()
                self.engine.error_occurred.disconnect()
            except:
                pass
            self.engine.stop()
            self.engine = None
    
    def get_retry_info(self):
        """Get current retry information."""
        return self.reconnection_manager.get_retry_info()
