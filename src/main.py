import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Slot

# Ensure src directory is on sys.path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.stream_engine import RTSPStreamEngine
from core.reconnection_manager import ReconnectionManager, StreamState
from core.frame_buffer import FrameBuffer
from gui.main_window import MainWindow
from gui.error_display import ErrorDialog
from utils.url_validator import URLValidator
from utils.logger import get_logger


class StreamController(QObject):
    """
    Connects MainWindow to RTSPStreamEngine according to specification.
    Wires FrameBuffer + ReconnectionManager:
    - FrameBuffer: Strict Latest Frame Policy + Watchdog on stream
    - ReconnectionManager: Manages reconnection attempts with backoff
    """

    def __init__(self, window: MainWindow):
        super().__init__(window)
        self.window = window
        self.engine: RTSPStreamEngine | None = None
        self.current_url: str | None = None
        self.logger = get_logger()

        # Single-frame buffer + watchdog
        self.frame_buffer = FrameBuffer()
        self.frame_buffer.on_frame_ready = self._on_buffer_frame_ready
        self.frame_buffer.on_timeout = self._on_frame_timeout

        # Reconnection state machine
        self.reconnect_manager = ReconnectionManager()
        self.reconnect_manager.on_state_changed = self._on_state_changed
        self.reconnect_manager.on_reconnect_attempt = self._on_reconnect_attempt
        self.reconnect_manager.on_max_retries_exceeded = self._on_max_retries_exceeded

        # Connect signals from GUI
        self.window.play_requested.connect(self.on_play_requested)
        self.window.stop_requested.connect(self.on_stop_requested)

    # ---------- GUI event handlers ----------

    @Slot(str)
    def on_play_requested(self, url: str):
        """Handle Play from UI with centralized URL validation.

        Supports three input types:
        1. Valid RTSP URL (rtsp://...) - validated by URLValidator
        2. Local path to existing video file
        3. Local webcam (e.g. "video=0" or "0")
        """
        raw_url = (url or "").strip()

        # 1) Existing local file
        is_local_path = os.path.exists(raw_url)

        # 2) Local webcam (DirectShow / index)
        lower_url = raw_url.lower()
        is_webcam = lower_url.startswith("video=") or lower_url.isdigit()

        if not (is_local_path or is_webcam):
            # 3) Must be valid RTSP URL
            is_valid, error_msg = URLValidator.validate(raw_url)
            if not is_valid:
                ErrorDialog.show_validation_error(self.window, error_msg)
                self.logger.log_validation_error(error_msg)
                return

        self.current_url = raw_url

        # Start connection state machine
        self.reconnect_manager.start_connection()
        self.window.set_connecting()
        self._start_engine()

    @Slot()
    def on_stop_requested(self):
        """Handle Stop from UI (user clicked Stop)."""
        self.reconnect_manager.user_stop()
        self._stop_engine()
        self.window.set_stopped()

    # ---------- Engine lifecycle ----------

    def _start_engine(self):
        """Create and start the stream engine for the current URL."""
        if not self.current_url:
            return

        # Ensure existing engine is stopped
        self._stop_engine()

        self.engine = RTSPStreamEngine(self.current_url)

        # Instead of feeding VideoWidget directly, pass through FrameBuffer
        self.engine.frame_ready.connect(self._on_engine_frame)
        self.engine.error_occurred.connect(self.on_engine_error)
        self.engine.connection_established.connect(self.on_connection_established)

        # Reset and use watchdog
        self.frame_buffer.clear()
        self.frame_buffer.start_watchdog()

        # start() is asynchronous - returns immediately, results via signals
        started = self.engine.start()
        if started:
            self.logger.log_ui_event(f"Starting stream for URL: {self.current_url}")
        else:
            # If immediate error occurs, wait for error_occurred, but keep UI consistent
            self.window.set_error("Failed to start stream")

    def _stop_engine(self):
        """Stop and clean up the current stream engine."""
        # Stop watchdog
        self.frame_buffer.stop_watchdog()
        self.frame_buffer.clear()

        if self.engine:
            # Disconnect signals to ensure no more frames arrive after stop
            try:
                self.engine.frame_ready.disconnect(self._on_engine_frame)
            except Exception:
                pass
            try:
                self.engine.error_occurred.disconnect(self.on_engine_error)
            except Exception:
                pass
            try:
                self.engine.connection_established.disconnect(self.on_connection_established)
            except Exception:
                pass

            self.engine.stop()
            self.engine = None

    # ---------- Engine signal handlers ----------

    @Slot(dict)
    def on_connection_established(self, info: dict):
        """Called when the engine successfully connects."""
        codec = info.get("codec", "unknown")
        resolution = info.get("resolution", "unknown")
        fps = info.get("fps", 0)
        self.logger.log_codec_info(codec, resolution, fps)

        # Update state machine
        self.reconnect_manager.connection_success()
        # Reset watchdog timer
        self.frame_buffer.reset_frame_timer()
        
        # Pass stream info to video widget
        self.window.video_widget.set_stream_info(info)

    @Slot(str)
    def on_engine_error(self, error_message: str):
        """Handle errors emitted by the stream engine."""
        self.logger.log_connection_error(error_message)
        
        # Check if it's a codec error - don't retry codec errors
        if "codec" in error_message.lower():
            # Codec error - stop completely, don't retry
            self._stop_engine()
            self.window.set_error(error_message)
            return
        
        # For other errors, try reconnecting via ReconnectionManager
        self._stop_engine()
        self.reconnect_manager.connection_failed(error_message)

    @Slot()
    def _on_frame_timeout(self):
        """Called by FrameBuffer watchdog when no frames arrive for too long."""
        self.logger.log_timeout(0)
        # Notify state machine that stream interrupted - it will handle retry
        self._stop_engine()
        self.reconnect_manager.stream_interrupted()

    @Slot()
    def _on_buffer_frame_ready(self):
        """Called when FrameBuffer has a new frame ready for display."""
        frame = self.frame_buffer.get_frame()
        if frame is not None:
            self.window.video_widget.display_frame(frame)

    @Slot(object)
    def _on_engine_frame(self, frame):
        """
        Receive frame from engine, push to FrameBuffer (Strict Latest Frame Policy).
        """
        self.frame_buffer.put_frame(frame)

    # ---------- ReconnectionManager callbacks ----------

    def _on_state_changed(self, state: StreamState):
        """Update GUI based on high-level stream state."""
        if state == StreamState.CONNECTING:
            self.window.set_connecting()
        elif state == StreamState.PLAYING:
            self.window.set_playing()
        elif state == StreamState.IDLE:
            self.window.set_stopped()
        elif state == StreamState.ERROR:
            # Final error state - on_max_retries_exceeded will show message
            pass

    def _on_reconnect_attempt(self, attempt: int, wait_time: int):
        """
        Called by ReconnectionManager before next connection attempt.
        After internal wait, arrange new start attempt.
        """
        # Wait already performed inside ReconnectionManager, just try opening engine again
        self.logger.log_reconnect_attempt(attempt, wait_time)
        if self.current_url:
            self._start_engine()

    def _on_max_retries_exceeded(self):
        """Handle case where automatic reconnection gave up."""
        message = "Maximum reconnection attempts exceeded.\n\nPlease check the RTSP URL or network and try again."
        self.window.set_error(message)
        # Show popup only after all attempts exhausted
        ErrorDialog.show_connection_error(self.window, message, "ERR_MAX_RETRIES")
        self._stop_engine()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    controller = StreamController(window)
    window.show()
    sys.exit(app.exec())


def main():
    """Entry point for console script."""
    app = QApplication(sys.argv)
    window = MainWindow()
    controller = StreamController(window)
    window.show()
    sys.exit(app.exec())