"""
RTSP Stream Engine - Handles video decoding and frame processing using PyAV/FFmpeg.
"""
import av
import av.error
import threading
import time
from typing import Optional, Callable, Any
import numpy as np
from PySide6.QtCore import QObject, Signal
from utils.logger import get_logger
from utils.config import Config

logger = get_logger()

class RTSPStreamEngine(QObject):
    """
    RTSP Stream Engine for handling video decoding and frame processing.
    Uses PyAV/FFmpeg for ultra-low latency streaming with H.264/H.265 support.
    Emits Qt signals for thread-safe communication with GUI.
    """
    
    # Qt Signals for GUI communication
    frame_ready = Signal(np.ndarray)  # Emitted when new frame is ready
    fps_updated = Signal(float)       # Emitted with FPS updates
    error_occurred = Signal(str)      # Emitted on error
    connection_established = Signal(dict)  # Emitted on successful connection
    
    def __init__(self, rtsp_url: str):
        """
        Initialize the RTSP Stream Engine.
        
        Args:
            rtsp_url: The RTSP stream URL
        """
        super().__init__()
        self.rtsp_url = rtsp_url
        self.container = None
        self.stream = None
        self.is_running = False
        self.capture_thread = None
        self.frame_callbacks = []
        self.fps_callbacks = []  # Callbacks for FPS updates
        self.fps = 30
        self.frame_count = 0
        self.last_frame_time = time.time()
        self.codec_name = None
        self.width = None
        self.height = None
        self.connection_timeout = Config.RTSP_TIMEOUT
        self.interrupt_event = threading.Event()  # For graceful interruption
        
    def add_frame_callback(self, callback: Callable[[np.ndarray], Any]):
        """
        Add a callback function to be called for each frame.
        
        Args:
            callback: Function that takes a frame (numpy array) as input
        """
        self.frame_callbacks.append(callback)
    
    def add_fps_callback(self, callback: Callable[[float], Any]):
        """
        Add a callback function to be called with FPS updates.
        
        Args:
            callback: Function that takes FPS (float) as input
        """
        self.fps_callbacks.append(callback)
        
    def remove_frame_callback(self, callback: Callable[[np.ndarray], Any]):
        """
        Remove a frame callback.
        
        Args:
            callback: The callback function to remove
        """
        if callback in self.frame_callbacks:
            self.frame_callbacks.remove(callback)
    
    def remove_fps_callback(self, callback: Callable[[float], Any]):
        """
        Remove an FPS callback.
        
        Args:
            callback: The callback function to remove
        """
        if callback in self.fps_callbacks:
            self.fps_callbacks.remove(callback)
    def start(self) -> bool:
        """
        Start the RTSP stream or Local Webcam capture.
        """
        if self.is_running:
            logger.log_ui_event("Stream is already running")
            return True
            
        try:
            # בדיקה האם מדובר במצלמה מקומית (מתחיל ב-video= או שזה רק מספר)
            is_webcam = "video=" in self.rtsp_url or self.rtsp_url.isdigit()
            
            options = Config.FFMPEG_OPTIONS.copy()
            
            if is_webcam:
                # הגדרות ספציפיות למצלמת מחשב בווינדוס
                logger.log_ui_event(f"Attempting to open webcam: {self.rtsp_url}")
                self.container = av.open(
                    self.rtsp_url,
                    format='dshow',  # חובה עבור מצלמות Windows
                    options={'framerate': '30'} # מבקש מהמצלמה 30 FPS
                )
            else:
                # הגדרות רגילות ל-RTSP
                options.update({
                    'rtsp_transport': 'tcp',
                    'stimeout': '5000000',
                    'allowed_media_types': 'video',
                    'buffer_size': '2048000',
                })
                self.container = av.open(
                    self.rtsp_url,
                    options=options,
                    timeout=self.connection_timeout
                )
            
            # Find video stream
            if not self.container or len(self.container.streams.video) == 0:
                raise ValueError("No video streams found in the provided URL/Device")

            self.stream = self.container.streams.video[0]
            
            # Get codec information
            self.codec_name = self.stream.codec_context.name
            self.width = self.stream.width
            self.height = self.stream.height
            
            # תיקון קטן עבור מצלמות שלא מדווחות FPS בצורה תקינה
            try:
                self.fps = float(self.stream.average_rate) or 30
            except:
                self.fps = 30
            
            # Log connection and codec info
            logger.log_connection(self.rtsp_url)
            logger.log_codec_info(self.codec_name, f"{self.width}x{self.height}", int(self.fps))
            
            # Emit connection established signal
            self.connection_established.emit({
                'codec': self.codec_name,
                'resolution': f"{self.width}x{self.height}",
                'fps': int(self.fps)
            })
            
            # בבדיקת מצלמה אנחנו מוותרים על בדיקת התמיכה ב-Codec כי זה משתנה בין מצלמות
            if not is_webcam and self.codec_name.lower() not in Config.SUPPORTED_CODECS:
                logger.log_codec_error(self.codec_name)
                self.error_occurred.emit(f"Unsupported codec: {self.codec_name}")
                return False
            
            self.is_running = True
            self.frame_count = 0
            self.last_frame_time = time.time()
            
            self.capture_thread = threading.Thread(
                target=self._capture_frames,
                daemon=True,
                name="RTSPStreamCapture"
            )
            self.capture_thread.start()
            
            return True
            
        except Exception as e:
            logger.log_error("CONNECTION_ERROR", f"Failed to open stream: {e}", "ERR_STREAM_OPEN")
            self.error_occurred.emit(f"Connection error: {str(e)}")
            return False
    # def start(self) -> bool:
    #     """
    #     Start the RTSP stream capture with PyAV/FFmpeg.
        
    #     Returns:
    #         True if stream started successfully, False otherwise
    #     """
    #     if self.is_running:
    #         logger.log_ui_event("Stream is already running")
    #         return True
            
    #     try:
    #         # Open RTSP stream with low-latency FFmpeg options
    #         options = Config.FFMPEG_OPTIONS.copy()
    #         options.update({
    #             'rtsp_transport': 'tcp',  # כפיית TCP למניעת "Invalid Data"
    #             'stimeout': '5000000',  # פסק זמן של 5 שניות (במיקרו-שניות)
    #             'allowed_media_types': 'video',  # התעלמות מאודיו כדי לחסוך משאבים
    #             'buffer_size': '2048000',  # הגדלת באפר ליציבות
    #         })
    #         self.container = av.open(
    #             self.rtsp_url,
    #             options=options,
    #             timeout=self.connection_timeout
    #         )
            
    #         # Find video stream
    #         if not self.container or len(self.container.streams.video) == 0:
    #             raise ValueError("No video streams found in the provided URL")

    #         self.stream = self.container.streams.video[0]
            
    #         # Get codec information
    #         self.codec_name = self.stream.codec_context.name
    #         self.width = self.stream.width
    #         self.height = self.stream.height
    #         self.fps = float(self.stream.average_rate) or 30
            
    #         # Log connection and codec info
    #         logger.log_connection(self.rtsp_url)
    #         logger.log_codec_info(
    #             self.codec_name,
    #             f"{self.width}x{self.height}",
    #             int(self.fps)
    #         )
            
    #         # Emit connection established signal
    #         self.connection_established.emit({
    #             'codec': self.codec_name,
    #             'resolution': f"{self.width}x{self.height}",
    #             'fps': int(self.fps)
    #         })
            
    #         # Validate codec support
    #         if self.codec_name.lower() not in Config.SUPPORTED_CODECS:
    #             logger.log_codec_error(self.codec_name)
    #             self.error_occurred.emit(f"Unsupported codec: {self.codec_name}")
    #             return False
            
    #         self.is_running = True
    #         self.frame_count = 0
    #         self.last_frame_time = time.time()
            
    #         self.capture_thread = threading.Thread(
    #             target=self._capture_frames,
    #             daemon=True,
    #             name="RTSPStreamCapture"
    #         )
    #         self.capture_thread.start()
            
    #         return True
            
    #     except Exception as e:
    #         logger.log_error("CONNECTION_ERROR", f"Failed to open RTSP stream: {e}", "ERR_RTSP_OPEN")
    #         self.error_occurred.emit(f"Connection error: {str(e)}")
    #         return False
    
    def stop(self):
        """
        Stop the RTSP stream capture and release resources.
        Signals interrupt event to allow graceful thread termination.
        """
        self.is_running = False
        self.interrupt_event.set()  # Signal interrupt to capture thread
        
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
        
        if self.container:
            try:
                self.container.close()
            except Exception as e:
                logger.log_error("CLOSE_ERROR", f"Error closing container: {e}")
            finally:
                self.container = None
        
        self.stream = None
        logger.log_disconnection("Stream stopped")
    
    def _capture_frames(self):
        """
        Internal method to capture and decode frames in a separate thread.
        Converts frames to RGB24 NumPy arrays with zero-copy techniques.
        Sends FPS updates via callbacks and signals, handles graceful interruption.
        """
        while self.is_running and self.container:
            try:
                for frame in self.container.decode(self.stream):
                    if not self.is_running or self.interrupt_event.is_set():
                        break
                    
                    # Convert frame to RGB24 NumPy array (zero-copy)
                    rgb_frame = frame.to_ndarray(format=Config.TARGET_PIXEL_FORMAT)
                    
                    self.frame_count += 1
                    current_time = time.time()
                    
                    # Emit frame ready signal to GUI
                    self.frame_ready.emit(rgb_frame)
                    
                    # Call frame callbacks
                    for callback in self.frame_callbacks:
                        try:
                            callback(rgb_frame)
                        except Exception as e:
                            logger.log_error("CALLBACK_ERROR", f"Error in frame callback: {e}")
                    
                    # Calculate actual FPS every 30 frames and notify via callback and signal
                    if self.frame_count % 30 == 0:
                        elapsed = current_time - self.last_frame_time
                        actual_fps = 30 / elapsed if elapsed > 0 else 0
                        logger.log_ui_event(f"Actual FPS: {actual_fps:.2f}")
                        
                        # Emit FPS signal to GUI
                        self.fps_updated.emit(actual_fps)
                        
                        # Notify FPS callbacks (for non-GUI use)
                        for callback in self.fps_callbacks:
                            try:
                                callback(actual_fps)
                            except Exception as e:
                                logger.log_error("FPS_CALLBACK_ERROR", f"Error in FPS callback: {e}")
                        
                        self.last_frame_time = current_time
                            
            except Exception as e:
                logger.log_error("DECODE_ERROR", f"Error decoding frame: {e}", "ERR_DECODE")
                self.error_occurred.emit(f"Decode error: {str(e)}")
                break
        
        logger.log_ui_event("Frame capture thread ended")
    
    def get_frame(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """
        Get a frame from the stream (deprecated - use frame callbacks instead).
        
        Args:
            timeout: Maximum time to wait for a frame
            
        Returns:
            Frame as numpy array or None if no frame available
        """
        # This method is deprecated with PyAV - use callbacks instead
        return None
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """
        Get the most recent frame (deprecated - use frame callbacks instead).
        
        Returns:
            Latest frame as numpy array or None if no frame available
        """
        # This method is deprecated with PyAV - use callbacks instead
        return None
    
    def is_connected(self) -> bool:
        """
        Check if the stream is connected and running.
        
        Returns:
            True if stream is connected, False otherwise
        """
        return self.is_running and self.container is not None and self.stream is not None
    
    def get_stream_info(self) -> dict:
        """
        Get information about the current stream.
        
        Returns:
            Dictionary containing stream information
        """
        if not self.container or not self.stream:
            return {}
            
        return {
            'url': self.rtsp_url,
            'codec': self.codec_name,
            'fps': self.fps,
            'width': self.width,
            'height': self.height,
            'frame_count': self.frame_count,
            'is_connected': self.is_connected(),
        }
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
