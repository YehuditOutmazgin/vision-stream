"""
Video Widget - Displays video frames with FPS counter and aspect ratio preservation.
"""

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QImage, QPixmap, QFont, QColor, QPainter
from PySide6.QtCore import Qt, QTimer
import numpy as np


class VideoWidget(QLabel):
    """Custom widget for video frame rendering."""

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: black;")
        self.setMinimumSize(640, 480)
        
        # FPS tracking
        self.frame_count = 0
        self.fps = 0
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self.update_fps)
        self.fps_timer.start(1000)  # Update every second
        
        # Stream info (resolution, codec)
        self.stream_info = {}
        
        # Connection state
        self.is_connecting = False
        self.connecting_spinner_frame = 0
        self.connecting_timer = QTimer()
        self.connecting_timer.timeout.connect(self._update_spinner)
        self.connecting_timer.start(100)  # Update spinner every 100ms

    def display_frame(self, frame_array: np.ndarray):
        """
        Display a frame from NumPy array with optimized scaling and aspect ratio.
        Uses FastTransformation for performance during playback.
        
        Args:
            frame_array: NumPy array in RGB24 format
        """
        if frame_array is None or frame_array.size == 0:
            return

        height, width = frame_array.shape[:2]
        
        # Convert NumPy array to QImage (zero-copy reference to frame data)
        bytes_per_line = 3 * width
        q_image = QImage(
            frame_array.data,
            width,
            height,
            bytes_per_line,
            QImage.Format_RGB888
        )

        # Convert to pixmap and scale with aspect ratio preservation
        # Use FastTransformation for performance during playback
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.FastTransformation  # Fast scaling for real-time performance
        )
        
        # Create final pixmap with letterboxing (black bars)
        final_pixmap = QPixmap(self.width(), self.height())
        final_pixmap.fill(QColor("black"))
        
        # Center the scaled pixmap
        x = (self.width() - scaled_pixmap.width()) // 2
        y = (self.height() - scaled_pixmap.height()) // 2
        
        # Draw frame and FPS counter with proper painter lifecycle management
        painter = QPainter(final_pixmap)
        try:
            painter.drawPixmap(x, y, scaled_pixmap)
            # Draw FPS counter
            self.draw_fps(painter)
        finally:
            # Ensure painter is properly ended before NumPy buffer lifecycle changes
            painter.end()
        
        self.setPixmap(final_pixmap)
        self.frame_count += 1

    def draw_fps(self, painter: QPainter):
        """
        Draw FPS counter and stream info in top-right corner with semi-transparent background.
        
        Note: This method receives an active QPainter. The caller is responsible
        for calling painter.end() after this method returns to ensure proper
        lifecycle management and prevent crashes with NumPy buffer references.
        
        Args:
            painter: Active QPainter object (caller must call end() after)
        """
        # Prepare text lines
        lines = [f"FPS: {self.fps}"]
        if self.stream_info:
            if 'resolution' in self.stream_info:
                lines.append(f"Resolution: {self.stream_info['resolution']}")
            if 'codec' in self.stream_info:
                lines.append(f"Codec: {self.stream_info['codec'].upper()}")
        
        font = QFont("Arial", 10)
        font.setBold(True)
        painter.setFont(font)
        
        # Calculate dimensions
        metrics = painter.fontMetrics()
        max_width = max(metrics.horizontalAdvance(line) for line in lines)
        line_height = metrics.height()
        total_height = line_height * len(lines)
        
        # Position in top-right corner with padding
        padding = 8
        x = self.width() - max_width - padding * 2
        y = padding
        
        # Draw semi-transparent background
        bg_color = QColor(0, 0, 0, 150)
        painter.fillRect(x - padding, y - padding, max_width + padding * 2, total_height + padding * 2, bg_color)
        
        # Draw text lines
        painter.setPen(QColor("white"))
        for i, line in enumerate(lines):
            painter.drawText(x, y + (i + 1) * line_height - 3, line)

    def update_fps(self):
        """Update FPS counter."""
        self.fps = self.frame_count
        self.frame_count = 0

    def clear_display(self):
        """Clear the video display and show black screen."""
        # Create black pixmap
        black_pixmap = QPixmap(self.width(), self.height())
        black_pixmap.fill(QColor("black"))
        self.setPixmap(black_pixmap)
        
        # Reset counters
        self.frame_count = 0
        self.fps = 0
        self.stream_info = {}
        self.is_connecting = False

    def set_stream_info(self, info: dict):
        """
        Set stream information (resolution, codec, etc.).
        
        Args:
            info: Dictionary with 'resolution', 'codec', 'fps' keys
        """
        self.stream_info = info

    def set_connecting(self, is_connecting: bool):
        """
        Set connecting state and show/hide spinner.
        
        Args:
            is_connecting: True to show connecting indicator, False to hide
        """
        self.is_connecting = is_connecting
        self.connecting_spinner_frame = 0
        if is_connecting:
            self._show_connecting_overlay()

    def _update_spinner(self):
        """Update spinner animation frame."""
        if self.is_connecting:
            self.connecting_spinner_frame = (self.connecting_spinner_frame + 1) % 4
            self._show_connecting_overlay()

    def _show_connecting_overlay(self):
        """Display connecting overlay with spinner."""
        # Create overlay pixmap
        overlay = QPixmap(self.width(), self.height())
        overlay.fill(QColor(0, 0, 0, 200))  # Semi-transparent black
        
        painter = QPainter(overlay)
        
        # Draw spinner animation
        spinner_chars = ['⠋', '⠙', '⠹', '⠸']
        spinner_text = spinner_chars[self.connecting_spinner_frame]
        
        font = QFont("Arial", 48)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor("white"))
        
        # Draw spinner in center
        painter.drawText(
            0, 0, self.width(), self.height() // 2,
            Qt.AlignCenter | Qt.AlignBottom,
            spinner_text
        )
        
        # Draw "Connecting..." text
        font.setPointSize(14)
        painter.setFont(font)
        painter.drawText(
            0, self.height() // 2, self.width(), self.height() // 2,
            Qt.AlignCenter | Qt.AlignTop,
            "Connecting..."
        )
        
        painter.end()
        self.setPixmap(overlay)
