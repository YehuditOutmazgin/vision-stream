"""
Reusable UI components for VisionStream.
"""

import numpy as np
from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QImage, QPixmap, QFont, QColor, QPainter
from .styles import COLORS


class VideoDisplay(QLabel):
    """
    Custom video display widget.

    Features:
    - Placeholder when no source is selected
    - Proper aspect-ratio preservation with letterboxing (black bars)
    - Semi-transparent overlay for "Connecting..." / "Reconnecting..."
    """

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(350)
        self.setMinimumWidth(600)
        self.setMaximumWidth(800)
        self.setScaledContents(False)  # Don't scale contents
        self.setStyleSheet(
            f"background-color: {COLORS['muted']}; "
            f"border: 1px solid {COLORS['border']}; "
            f"border-radius: 12px;"
        )
        self.placeholder_layout = None

        # Overlay state (Connecting / Reconnecting)
        self._overlay_active = False
        self._overlay_text = ""
        self._spinner_frame = 0
        self._overlay_timer = QTimer()
        self._overlay_timer.timeout.connect(self._update_spinner)

        self._set_placeholder()

    def _clear_placeholder(self):
        """Clear placeholder layout if present."""
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.setLayout(None)

    def _set_placeholder(self):
        """Display placeholder message."""
        placeholder = QFrame()
        placeholder.setStyleSheet("background-color: transparent; border: none;")
        layout = QVBoxLayout(placeholder)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        # icon_label = QLabel("🎬")
        # icon_label.setFont(QFont("Arial", 48))
        # icon_label.setAlignment(Qt.AlignCenter)

        # text_label = QLabel("No video source selected")
        # text_label.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 15, QFont.Bold))
        # text_label.setAlignment(Qt.AlignCenter)
        # text_label.setStyleSheet(f"color: {COLORS['foreground']}; font-weight: 600;")

        # hint_label = QLabel("Enter a URL, connect your camera, or open a local file")
        # hint_label.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 12))
        # hint_label.setAlignment(Qt.AlignCenter)
        # hint_label.setStyleSheet(f"color: {COLORS['muted_foreground']};")

        # layout.addWidget(icon_label)
        # layout.addWidget(text_label)
        # layout.addWidget(hint_label)

        self.placeholder_layout = layout
        self.setLayout(layout)

    @Slot(np.ndarray)
    def update_frame(self, frame_array: np.ndarray):
        """
        Update display with new frame using letterboxing to preserve aspect ratio.
        """
        try:
            # Clear placeholder if it exists
            if self.layout():
                self._clear_placeholder()

            if frame_array is None or frame_array.size == 0:
                return

            height, width = frame_array.shape[:2]
            bytes_per_line = 3 * width
            q_img = QImage(frame_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)

            # Scale frame while keeping aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # Create final pixmap with letterboxing (black bars)
            final_pixmap = QPixmap(self.width(), self.height())
            final_pixmap.fill(QColor("black"))

            # Center the scaled pixmap
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2

            painter = QPainter(final_pixmap)
            try:
                painter.drawPixmap(x, y, scaled_pixmap)
            finally:
                painter.end()

            self.setPixmap(final_pixmap)
        except Exception as e:
            self.setText(f"Error displaying frame: {str(e)}")

    def clear_display(self):
        """Clear the display and restore placeholder."""
        self.setPixmap(QPixmap())
        self._overlay_active = False
        self._overlay_timer.stop()
        if self.layout():
            self._clear_placeholder()
        self._set_placeholder()

    # ---- Overlay API (Connecting / Reconnecting) ----

    def show_connecting(self, reconnecting: bool = False):
        """
        Show semi-transparent overlay for connecting/reconnecting state.

        Args:
            reconnecting: True to show 'Reconnecting...', False for 'Connecting...'
        """
        self._overlay_text = "Reconnecting..." if reconnecting else "Connecting..."
        self._overlay_active = True
        self._spinner_frame = 0
        if not self._overlay_timer.isActive():
            self._overlay_timer.start(100)
        self._draw_overlay()

    def hide_overlay(self):
        """Hide any active overlay."""
        self._overlay_active = False
        self._overlay_timer.stop()

    def _update_spinner(self):
        """Update spinner animation frame for overlay."""
        if not self._overlay_active:
            return
        self._spinner_frame = (self._spinner_frame + 1) % 4
        self._draw_overlay()

    def _draw_overlay(self):
        """Draw semi-transparent overlay with spinner and status text."""
        overlay = QPixmap(self.width(), self.height())
        overlay.fill(QColor(0, 0, 0, 200))  # Semi-transparent black

        painter = QPainter(overlay)
        try:
            # Spinner animation
            spinner_chars = ['⠋', '⠙', '⠹', '⠸']
            spinner_text = spinner_chars[self._spinner_frame]

            font = QFont("Arial", 48)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor("white"))

            # Draw spinner in center (upper half)
            painter.drawText(
                0, 0, self.width(), self.height() // 2,
                Qt.AlignCenter | Qt.AlignBottom,
                spinner_text
            )

            # Draw status text ("Connecting..." / "Reconnecting...")
            font.setPointSize(14)
            painter.setFont(font)
            painter.drawText(
                0, self.height() // 2, self.width(), self.height() // 2,
                Qt.AlignCenter | Qt.AlignTop,
                self._overlay_text
            )
        finally:
            painter.end()

        self.setPixmap(overlay)


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
        layout.setSpacing(10)
        
        # URL input row with FPS display
        url_row = QHBoxLayout()
        url_row.setSpacing(10)
        
        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter video or RTSP URL...")
        self.url_input.setMinimumHeight(40)
        self.url_input.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 12))
        self.url_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['foreground']};
                padding: 8px 12px;
                font-size: 12px;
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
        self.fps_label.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 12, QFont.Bold))
        self.fps_label.setAlignment(Qt.AlignCenter)
        self.fps_label.setStyleSheet(f"color: {COLORS['primary']}; padding: 8px 12px; background-color: {COLORS['card']}; border: 1px solid {COLORS['border']}; border-radius: 8px; min-width: 90px;")
        
        url_row.addWidget(self.url_input, 1)
        url_row.addWidget(self.fps_label)
        
        # Buttons row
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.camera_btn = QPushButton("📷 Camera")
        self.camera_btn.setMinimumHeight(40)
        self.camera_btn.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 12))
        self.camera_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['foreground']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['muted']};
                border: 1px solid #d1d5db;
            }}
            QPushButton:disabled {{
                background-color: {COLORS['muted']};
                color: {COLORS['muted_foreground']};
                border: 1px solid {COLORS['border']};
            }}
            """
        )
        
        self.file_btn = QPushButton("📁 File")
        self.file_btn.setMinimumHeight(40)
        self.file_btn.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 12))
        self.file_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['foreground']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['muted']};
                border: 1px solid #d1d5db;
            }}
            QPushButton:disabled {{
                background-color: {COLORS['muted']};
                color: {COLORS['muted_foreground']};
                border: 1px solid {COLORS['border']};
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
        layout.setSpacing(6)
        
        # Title
        title = QLabel("Vision Stream")
        title.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {COLORS['foreground']};")
        
        # Description
        description = QLabel(
            "Stream videos from RTSP, webcam, or local files"
        )
        description.setFont(QFont("-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 11))
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet(f"color: {COLORS['muted_foreground']};")
        
        layout.addWidget(title)
        layout.addWidget(description)
