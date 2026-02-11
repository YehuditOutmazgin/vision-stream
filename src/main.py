import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFileDialog, QPushButton, QLabel
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QFont

from utils.config import Config
from utils.error_handler import ErrorHandler
from utils.logger import get_logger
from gui.styles import MAIN_STYLESHEET, COLORS
from gui.components import VideoDisplay, ControlPanel, Header
from gui.stream_controller import StreamController
from gui.ui_manager import UIManager
from gui.error_display import ErrorDialog


class VisionStreamApp(QMainWindow):
    """Main application window for VisionStream."""

    def __init__(self):
        super().__init__()
        self.logger = get_logger()
        self._init_ui()
        self._init_controllers()

    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        self.setFixedSize(800, 650)  # Fixed window size - no resizing
        self.setStyleSheet(MAIN_STYLESHEET)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 16, 12, 16)
        main_layout.setSpacing(12)

        # Header
        self.header = Header()
        main_layout.addWidget(self.header)

        # Control panel
        self.control_panel = ControlPanel()
        self.control_panel.url_input.returnPressed.connect(self._on_play_requested)
        self.control_panel.file_btn.clicked.connect(self._on_file_selected)
        self.control_panel.camera_btn.clicked.connect(self._on_camera_selected)
        main_layout.addWidget(self.control_panel)
        
        # FPS display reference (from control panel)
        self.fps_display = self.control_panel.fps_label

        # Play button
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.setObjectName("play_btn")
        self.play_btn.setMinimumHeight(40)
        self.play_btn.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 13, QFont.Bold))
        self.play_btn.clicked.connect(self._on_play_stop_clicked)
        main_layout.addWidget(self.play_btn)

        # Video display
        self.video_display = VideoDisplay()
        video_container = QWidget()
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_layout.addWidget(self.video_display)
        video_layout.addStretch()
        main_layout.addWidget(video_container, 0)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 11))
        self.status_label.setStyleSheet(f"color: {COLORS['muted_foreground']}; padding: 2px;")
        self.status_label.hide()
        main_layout.addWidget(self.status_label)

    def _init_controllers(self):
        """Initialize stream and UI controllers."""
        self.stream_controller = StreamController(
            on_frame_ready=self.video_display.update_frame,
            on_fps_updated=self._on_fps_updated,
            on_state_changed=self._on_stream_state_changed,
            on_reconnect_attempt=self._on_reconnect_attempt
        )
        
        # Setup max retries callback to show error dialog
        self.stream_controller.reconnection_manager.on_max_retries_exceeded = self._on_max_retries_exceeded
        
        self.ui_manager = UIManager(
            play_btn=self.play_btn,
            fps_display=self.fps_display,
            status_label=self.status_label,
            video_display=self.video_display,
            control_panel=self.control_panel
        )

    @Slot()
    def _on_file_selected(self):
        """Handle file selection."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Video", "", "Video Files (*.mp4 *.avi *.mkv *.mov *.flv)"
        )
        if path:
            self.control_panel.url_input.setText(path)
            self._start_stream()

    @Slot()
    def _on_camera_selected(self):
        """Handle camera selection."""
        self.control_panel.url_input.setText("video=Integrated Camera")
        self._start_stream()

    @Slot()
    def _on_play_requested(self):
        """Handle play request from URL input."""
        self._start_stream()

    @Slot()
    def _on_play_stop_clicked(self):
        """Handle play/stop button click."""
        # Check if we're in connecting or playing state
        if self.play_btn.text() == "⏹ Stop":
            self._stop_stream()
        else:
            self._start_stream()

    def _start_stream(self):
        """Start streaming from the provided source."""
        url = self.control_panel.url_input.text().strip()
        success, error_msg = self.stream_controller.validate_and_start(url)
        
        if not success:
            self._show_error(error_msg)
        else:
            # Update UI to connecting state FIRST
            self.ui_manager.set_connecting()
            # Then start the actual connection in background
            self.stream_controller.start_connection()

    def _stop_stream(self):
        """Stop the current stream."""
        try:
            self.stream_controller.stop()
            self.ui_manager.set_stopped()
        except RuntimeError:
            # Thread already deleted
            self.ui_manager.set_stopped()

    @Slot(float)
    def _on_fps_updated(self, fps):
        """Update FPS display."""
        self.ui_manager.update_fps(fps)

    @Slot(str, str)
    def _on_stream_state_changed(self, state_value, error_msg):
        """Handle stream state changes."""
        try:
            self.ui_manager.handle_state_change(state_value, error_msg)
            # Show error dialog only after all retries failed (not on every attempt)
        except Exception as e:
            self.logger.log_error("UI_ERROR", f"Error in state change handler: {e}")
            import traceback
            traceback.print_exc()

    @Slot(int, int)
    def _on_reconnect_attempt(self, attempt, wait_time):
        """Handle reconnection attempt."""
        self.ui_manager.set_reconnecting(attempt, wait_time)

    def _on_max_retries_exceeded(self):
        """Handle max retries exceeded."""
        try:
            # Stop everything
            self.stream_controller.stop()
            
            # Show error dialog
            user_friendly_msg = "Failed to connect after 5 attempts.\n\nPlease check the URL and try again."
            ErrorDialog.show_validation_error(self, user_friendly_msg)
            
            # Update UI
            self.ui_manager.set_error("Connection failed")
        except Exception as e:
            self.logger.log_error("UI_ERROR", f"Error in max retries handler: {e}")
            import traceback
            traceback.print_exc()

    def _show_error(self, msg):
        """Display error message with dialog."""
        self.stream_controller.stop()
        
        # Map technical errors to friendly text
        user_friendly_msg = ErrorHandler.get_user_friendly_message(msg or "")
        
        # Show error dialog
        ErrorDialog.show_validation_error(self, user_friendly_msg)
        
        # Show error in UI
        self.ui_manager.set_error(user_friendly_msg)

    def closeEvent(self, event):
        """Handle application close event."""
        try:
            if self.stream_controller.connection_thread:
                try:
                    self.stream_controller.connection_thread.stop()
                except RuntimeError:
                    pass
            self._stop_stream()
            event.accept()
        except Exception as e:
            self.logger.log_error("CLOSE_ERROR", f"Error during close: {e}")
            event.accept()


if __name__ == "__main__":
    import os
    import sys
    
    # Suppress FFmpeg/PyAV error messages to console
    if sys.platform == 'win32':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetErrorMode(0x0001 | 0x0002)  # SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX
    
    # Redirect stderr to suppress av/ffmpeg warnings
    import av
    av.logging.set_level(av.logging.ERROR)
    
    try:
        app = QApplication(sys.argv)
        window = VisionStreamApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")