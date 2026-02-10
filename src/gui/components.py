"""
Reusable UI components for VisionStream.
"""

import numpy as np
from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap, QFont
from .styles import COLORS


class VideoDisplay(QLabel):
    """Custom video display widget."""

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(450)
        self.setStyleSheet(
            f"background-color: #f3f4f6; "
            f"border: none; "
            f"border-radius: 12px;"
        )
        self.placeholder_layout = None
        self._set_placeholder()

    def _set_placeholder(self):
        """Display placeholder message."""
        placeholder = QFrame()
        placeholder.setStyleSheet("background-color: transparent; border: none;")
        layout = QVBoxLayout(placeholder)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)
        
        icon_label = QLabel("📹")
        icon_label.setFont(QFont("Arial", 56))
        icon_label.setAlignment(Qt.AlignCenter)
        
        text_label = QLabel("No video source selected")
        text_label.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 16))
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet(f"color: {COLORS['muted_foreground']}; font-weight: 500;")
        
        hint_label = QLabel("Enter a URL, connect your camera, or open a local file")
        hint_label.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 13))
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet(f"color: {COLORS['muted_foreground']};")
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addWidget(hint_label)
        
        self.placeholder_layout = layout
        self.setLayout(layout)

    @Slot(np.ndarray)
    def update_frame(self, frame_array):
        """Update display with new frame."""
        try:
            # Clear placeholder if it exists
            if self.layout():
                while self.layout().count():
                    self.layout().takeAt(0).widget().deleteLater()
            
            height, width, channel = frame_array.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)
        except Exception as e:
            self.setText(f"Error displaying frame: {str(e)}")

    def clear_display(self):
        """Clear the display."""
        self.setPixmap(QPixmap())
        # Clear layout
        if self.layout():
            while self.layout().count():
                self.layout().takeAt(0).widget().deleteLater()
        self._set_placeholder()


class ControlPanel(QFrame):
    """Control panel with URL input and action buttons."""

    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            f"background-color: transparent; "
            f"border: none;"
        )
        self._init_layout()

    def _init_layout(self):
        """Initialize control panel layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # URL input row with FPS display
        url_row = QHBoxLayout()
        url_row.setSpacing(12)
        
        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter video or RTSP URL...")
        self.url_input.setMinimumHeight(44)
        self.url_input.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 13))
        self.url_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['foreground']};
                padding: 8px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
                border-radius: 8px;
            }}
            QLineEdit:disabled {{
                background-color: {COLORS['muted']};
                color: {COLORS['muted_foreground']};
                border: 1px solid {COLORS['border']};
            }}
            """
        )
        
        # FPS display
        self.fps_label = QLabel("FPS: 0.0")
        self.fps_label.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 13, QFont.Bold))
        self.fps_label.setAlignment(Qt.AlignCenter)
        self.fps_label.setStyleSheet(f"color: #3b82f6; padding: 8px 12px; background-color: {COLORS['card']}; border: 1px solid {COLORS['border']}; border-radius: 8px; min-width: 100px;")
        
        url_row.addWidget(self.url_input, 1)
        url_row.addWidget(self.fps_label)
        
        # Buttons row
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        self.camera_btn = QPushButton("📷 Connect Camera")
        self.camera_btn.setMinimumHeight(44)
        self.camera_btn.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 13))
        self.camera_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['foreground']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['muted']};
            }}
            """
        )
        
        self.file_btn = QPushButton("📁 Open Local File")
        self.file_btn.setMinimumHeight(44)
        self.file_btn.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 13))
        self.file_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['foreground']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['muted']};
            }}
            """
        )
        
        buttons_layout.addWidget(self.camera_btn, 1)
        buttons_layout.addWidget(self.file_btn, 1)
        
        layout.addLayout(url_row)
        layout.addLayout(buttons_layout)
    
    def toggle_enabled(self, enabled: bool):
        """Enable or disable all controls."""
        self.url_input.setEnabled(enabled)
        self.file_btn.setEnabled(enabled)
        self.camera_btn.setEnabled(enabled)


class Header(QFrame):
    """Application header with title and description."""

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: transparent; border: none;")
        self._init_layout()

    def _init_layout(self):
        """Initialize header layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("Vision Stream Pro")
        title.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {COLORS['foreground']};")
        
        # Description
        description = QLabel(
            "Live streaming application supporting RTSP protocol, direct webcam connection, "
            "or local file playback.\nClick PLAY to start your stream. Enjoy watching!"
        )
        description.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 11))
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet(f"color: {COLORS['muted_foreground']};")
        
        layout.addWidget(title)
        layout.addWidget(description)
