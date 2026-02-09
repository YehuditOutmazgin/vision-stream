import sys
import os
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.stream_engine import RTSPStreamEngine
from utils.config import Config
from utils.url_validator import URLValidator
from utils.logger import get_logger

class VideoWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: black;")
        self.setText("No Stream")
        self.setMinimumSize(Config.MIN_WINDOW_WIDTH, Config.MIN_WINDOW_HEIGHT)

    @Slot(np.ndarray)
    def update_frame(self, frame_array):
        height, width, channel = frame_array.shape
        bytes_per_line = 3 * width
        
        q_img = QImage(frame_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        pixmap = QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(
            self.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)


class VisionStreamApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = get_logger()
        self.engine = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        self.resize(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Control Layout
        ctrl_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter RTSP URL, Local File path, or 'video=0' for Webcam")

        # New: Button for local files
        self.file_btn = QPushButton("Open File")
        self.file_btn.clicked.connect(self.handle_select_file)

        # New: Button for local webcam
        self.webcam_btn = QPushButton("Webcam")
        self.webcam_btn.clicked.connect(self.handle_use_webcam)

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.handle_play_stop)

        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setStyleSheet("color: #00FF00; font-weight: bold;")

        # Adding widgets to layout
        ctrl_layout.addWidget(self.url_input)
        ctrl_layout.addWidget(self.file_btn)
        ctrl_layout.addWidget(self.webcam_btn)
        ctrl_layout.addWidget(self.play_btn)
        ctrl_layout.addWidget(self.fps_label)

        self.video_display = VideoWidget()

        main_layout.addLayout(ctrl_layout)
        main_layout.addWidget(self.video_display)

    @Slot()
    def handle_select_file(self):
        """
        Open file dialog and set the path to the input field.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video", "", "Video Files (*.mp4 *.avi *.mkv *.mov);;All Files (*.*)"
        )
        if file_path:
            self.url_input.setText(file_path)

    @Slot()
    def handle_use_webcam(self):
        """
        Set default webcam device string to the input field.
        """
        self.url_input.setText("video=0")

    def handle_play_stop(self):
        if self.engine and self.engine.is_running:
            self.stop_stream()
        else:
            self.start_stream()

    def start_stream(self):
        url = self.url_input.text().strip()

        # Validation bypass for local files and webcam devices
        is_local_path = os.path.exists(url)
        is_webcam = "video=" in url or url.isdigit()

        if not (is_local_path or is_webcam):
            is_valid, error_msg = URLValidator.validate(url)
            if not is_valid:
                QMessageBox.warning(self, "Validation Error", error_msg)
                return

        self.engine = RTSPStreamEngine(url)
        self.engine.frame_ready.connect(self.video_display.update_frame)
        self.engine.fps_updated.connect(lambda fps: self.fps_label.setText(f"FPS: {fps:.2f}"))
        self.engine.error_occurred.connect(self.handle_error)

        if self.engine.start():
            self.play_btn.setText("Stop")
            self.url_input.setEnabled(False)
            self.file_btn.setEnabled(False)
            self.webcam_btn.setEnabled(False)
        else:
            pass

    def stop_stream(self):
        if self.engine:
            self.engine.stop()
            self.engine = None

        self.play_btn.setText("Play")
        self.url_input.setEnabled(True)
        self.file_btn.setEnabled(True)
        self.webcam_btn.setEnabled(True)
        self.video_display.clear()
        self.video_display.setText("Stream Stopped")
        self.fps_label.setText("FPS: 0")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VisionStreamApp()
    window.show()
    sys.exit(app.exec())