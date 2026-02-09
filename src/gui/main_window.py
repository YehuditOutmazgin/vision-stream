"""
Main Window - Primary UI component for VisionStream.
"""

import re
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel
)
from PySide6.QtCore import Qt, Signal
from .video_widget import VideoWidget
from .error_display import ErrorDialog


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
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()

        # Control panel
        control_layout = QHBoxLayout()

        # URL input
        url_label = QLabel("RTSP URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("rtsp://host:port/path")

        # Buttons
        self.play_button = QPushButton("Play")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        
        # Connect button signals
        self.play_button.clicked.connect(self._on_play_clicked)
        self.stop_button.clicked.connect(self._on_stop_clicked)

        control_layout.addWidget(url_label)
        control_layout.addWidget(self.url_input)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.stop_button)

        # Video widget
        self.video_widget = VideoWidget()

        # Status bar
        self.status_label = QLabel("Ready")

        # Add to main layout
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.video_widget)
        main_layout.addWidget(self.status_label)

        central_widget.setLayout(main_layout)

    def validate_url(self, url: str) -> bool:
        """
        Validate RTSP URL format.
        
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
        
        if not self.RTSP_URL_PATTERN.match(url):
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
        if self.stop_button.isEnabled():
            self.stop_requested.emit()
        
        event.accept()

    def set_playing(self):
        """Update UI state to playing."""
        self.play_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.url_input.setReadOnly(True)
        self.status_label.setText("Playing...")
        self.video_widget.set_connecting(False)

    def set_stopped(self):
        """Update UI state to stopped."""
        self.play_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.url_input.setReadOnly(False)
        self.status_label.setText("Ready")
        self.video_widget.clear_display()
        self.video_widget.set_connecting(False)

    def set_connecting(self):
        """Update UI state to connecting."""
        self.play_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.url_input.setReadOnly(True)
        self.status_label.setText("Connecting...")
        self.video_widget.set_connecting(True)

    def set_error(self, error_message: str):
        """
        Update UI state to error.
        
        Args:
            error_message: Error message to display
        """
        self.play_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.url_input.setReadOnly(False)
        self.status_label.setText(f"Error: {error_message}")
        self.video_widget.set_connecting(False)

    def _on_play_clicked(self):
        """Handle Play button click with URL validation."""
        url = self.url_input.text().strip()
        if self.validate_url(url):
            self.play_requested.emit(url)

    def _on_stop_clicked(self):
        """Handle Stop button click."""
        self.stop_requested.emit()
