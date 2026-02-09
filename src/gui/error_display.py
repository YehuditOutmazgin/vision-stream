"""
Error Display - Handles error message presentation to user.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor


class ErrorDialog(QDialog):
    """Dialog for displaying error messages."""

    def __init__(self, parent=None, error_type: str = "Error", message: str = "", error_code: str = ""):
        super().__init__(parent)
        self.setWindowTitle(f"VisionStream - {error_type}")
        self.setGeometry(200, 200, 500, 200)
        self.setModal(True)
        self.init_ui(error_type, message, error_code)

    def init_ui(self, error_type: str, message: str, error_code: str):
        """Initialize the error dialog UI."""
        layout = QVBoxLayout()

        # Error type header
        type_label = QLabel(error_type)
        type_font = QFont("Arial", 14)
        type_font.setBold(True)
        type_label.setFont(type_font)
        
        # Color code by error type
        if error_type == "Validation Error":
            type_label.setStyleSheet("color: #FF9800;")  # Orange
        elif error_type == "Connection Error":
            type_label.setStyleSheet("color: #F44336;")  # Red
        elif error_type == "Codec Error":
            type_label.setStyleSheet("color: #E91E63;")  # Pink
        else:
            type_label.setStyleSheet("color: #2196F3;")  # Blue

        # Error message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Arial", 11))

        # Error code (if provided)
        if error_code:
            code_label = QLabel(f"Error Code: {error_code}")
            code_label.setFont(QFont("Courier", 9))
            code_label.setStyleSheet("color: #666666;")
            layout.addWidget(code_label)

        # OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)

        layout.addWidget(type_label)
        layout.addWidget(message_label)
        layout.addStretch()
        layout.addWidget(ok_button)

        self.setLayout(layout)

    @staticmethod
    def show_validation_error(parent, message: str):
        """Show validation error dialog."""
        dialog = ErrorDialog(parent, "Validation Error", message)
        dialog.exec()

    @staticmethod
    def show_connection_error(parent, message: str, error_code: str = ""):
        """Show connection error dialog."""
        dialog = ErrorDialog(parent, "Connection Error", message, error_code)
        dialog.exec()

    @staticmethod
    def show_codec_error(parent, codec: str):
        """Show codec error dialog."""
        message = f"Unsupported video codec: {codec}\n\nSupported codecs: H.264, H.265 (HEVC)"
        dialog = ErrorDialog(parent, "Codec Error", message, "ERR_CODEC")
        dialog.exec()

    @staticmethod
    def show_timeout_error(parent):
        """Show timeout error as non-blocking overlay (not modal)."""
        message = "Connection timeout - server not responding.\n\nThe application will attempt to reconnect automatically."
        dialog = ErrorDialog(parent, "Connection Error", message, "ERR_TIMEOUT")
        dialog.setModal(False)  # Non-blocking
        dialog.show()

    @staticmethod
    def show_max_retries_error(parent):
        """Show max retries exceeded error dialog (blocking)."""
        message = "Maximum reconnection attempts exceeded.\n\nPlease check the RTSP URL and try again."
        dialog = ErrorDialog(parent, "Connection Error", message, "ERR_MAX_RETRIES")
        dialog.setModal(True)  # Blocking - requires user action
        dialog.exec()
