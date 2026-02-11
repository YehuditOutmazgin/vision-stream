"""
Main Window - Primary UI component for VisionStream.
"""

import os
import re
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from .video_widget import VideoWidget
from .error_display import ErrorDialog
from utils.config import Config


class MainWindow(QMainWindow):
    """Main application window."""

    # RTSP URL validation regex pattern
    RTSP_URL_PATTERN = re.compile(r'^rtsp://[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=]+$')
    
    # Signals for stream control
    play_requested = Signal(str)  # Emitted when Play button clicked with URL
    stop_requested = Signal()     # Emitted when Stop button clicked

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VisionStream RTSP Viewer")
        self.setGeometry(100, 100, 1280, 720)
        # Track current playback state to drive Play/Stop toggle
        self.is_playing = False
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        # Reduce margins/spacing so status is close to URL and video
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(4)

        # Control panel
        control_layout = QHBoxLayout()
        control_layout.setSpacing(4)

        # URL input
        url_label = QLabel("RTSP URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("rtsp://host:port/path")

        # Play/Stop toggle button
        self.play_button = QPushButton("Play")

        # Convenience buttons for local file and webcam
        self.open_file_button = QPushButton("Open File")
        self.webcam_button = QPushButton("Webcam")

        # Connect button signals
        self.play_button.clicked.connect(self._on_play_stop_clicked)
        self.open_file_button.clicked.connect(self._on_open_file_clicked)
        self.webcam_button.clicked.connect(self._on_webcam_clicked)

        control_layout.addWidget(url_label)
        control_layout.addWidget(self.url_input)
        control_layout.addWidget(self.open_file_button)
        control_layout.addWidget(self.webcam_button)
        control_layout.addWidget(self.play_button)

        # Video widget
        self.video_widget = VideoWidget()

        # Status bar (moved above video for better visibility)
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_label.setFixedHeight(20)

        # Add to main layout (status above video widget)
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.video_widget)

        central_widget.setLayout(main_layout)

    def validate_url(self, url: str) -> bool:
        """
        Lightweight validation of user input before delegating
        the full validation to the controller/engine.

        Supports three input types:
        1. Path to existing local file
        2. Local webcam ("video=0" or "0")
        3. Valid RTSP URL (rtsp://...)
        
        Args:
            url: URL string to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        if not url or not url.strip():
            ErrorDialog.show_validation_error(
                self,
                "URL cannot be empty"
            )
            return False

        url = url.strip()

        # 1) Local file path
        if os.path.exists(url):
            return True

        # 2) Webcam device ("video=0" / "0")
        lower_url = url.lower()
        if lower_url.startswith("video=") or lower_url.isdigit():
            return True

        # 3) RTSP URL – enforce RTSP pattern
        if not url.lower().startswith("rtsp://") or not self.RTSP_URL_PATTERN.match(url):
            ErrorDialog.show_validation_error(
                self,
                "Invalid URL format.\n\nExpected format: rtsp://host:port/path"
            )
            return False

        return True

    def closeEvent(self, event):
        """
        Handle application close event with graceful shutdown.
        
        Args:
            event: Close event
        """
        # Stop any active stream
        if self.is_playing:
            self.stop_requested.emit()
        
        event.accept()

    def set_playing(self):
        """Update UI state to playing."""
        self.is_playing = True
        self.play_button.setText("Stop")
        self.play_button.setEnabled(True)
        self.open_file_button.setEnabled(False)
        self.webcam_button.setEnabled(False)
        self.url_input.setReadOnly(True)
        self.status_label.setText("Playing...")
        self.video_widget.set_connecting(False)

    def set_stopped(self):
        """Update UI state to stopped."""
        self.is_playing = False
        self.play_button.setText("Play")
        self.play_button.setEnabled(True)
        self.open_file_button.setEnabled(True)
        self.webcam_button.setEnabled(True)
        self.url_input.setReadOnly(False)
        self.status_label.setText("Ready")
        self.video_widget.clear_display()
        self.video_widget.set_connecting(False)

    def set_connecting(self):
        """Update UI state to connecting."""
        # During connecting, treat button as Stop (allow user to cancel)
        self.is_playing = True
        self.play_button.setText("Stop")
        self.play_button.setEnabled(True)
        self.open_file_button.setEnabled(False)
        self.webcam_button.setEnabled(False)
        self.url_input.setReadOnly(True)
        self.status_label.setText("Connecting...")
        self.video_widget.set_connecting(True)

    def set_error(self, error_message: str):
        """
        Update UI state to error.
        
        Args:
            error_message: Error message to display
        """
        self.is_playing = False
        self.play_button.setText("Play")
        self.play_button.setEnabled(True)
        self.open_file_button.setEnabled(True)
        self.webcam_button.setEnabled(True)
        self.url_input.setReadOnly(False)
        self.status_label.setText(f"Error: {error_message}")
        self.video_widget.clear_display()
        self.video_widget.set_connecting(False)

    def _on_play_stop_clicked(self):
        """Toggle between Play and Stop based on current state."""
        if self.is_playing:
            # Request stop
            self.stop_requested.emit()
        else:
            # Validate and request play
            url = self.url_input.text().strip()
            if self.validate_url(url):
                self.play_requested.emit(url)

    def _on_open_file_clicked(self):
        """Open a file dialog and put selected path into the URL field."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov);;All Files (*.*)",
        )
        if file_path:
            self.url_input.setText(file_path)
            # Auto-start playback if not already playing
            if not self.is_playing:
                self._on_play_stop_clicked()

    def _on_webcam_clicked(self):
        """Set default webcam device string into the URL field."""
        self.url_input.setText(Config.DEFAULT_WEBCAM_DEVICE)
        # Auto-start playback if not already playing
        if not self.is_playing:
            self._on_play_stop_clicked()
