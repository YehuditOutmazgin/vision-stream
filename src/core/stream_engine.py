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
        # Thread that handles the (potentially slow) initial connection so the GUI stays responsive
        self._connect_thread: Optional[threading.Thread] = None
        
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
        This method is intentionally non-blocking so the GUI thread stays responsive.
        """
        if self.is_running:
            logger.log_ui_event("Stream is already running")
            return True

        # Clear interrupt indicator from previous sessions
        self.interrupt_event.clear()

        # Mark as "running" now so GUI button changes to "Stop"
        self.is_running = True

        def _connect_and_start():
            """
            Runs in a background thread: opens the container and starts the
            frame capture thread. Any errors are sent back via Qt signals.
            """
            try:
                # Check if this is a local webcam (starts with video= or is just a number)
                is_webcam = "video=" in self.rtsp_url or self.rtsp_url.isdigit()

                options = Config.FFMPEG_OPTIONS.copy()

                if is_webcam:
                    # Specific settings for Windows webcam
                    logger.log_ui_event(f"Attempting to open webcam: {self.rtsp_url}")
                    self.container = av.open(
                        self.rtsp_url,
                        format='dshow',  # Required for Windows cameras
                        options={'framerate': '30'}  # Request 30 FPS from camera
                    )
                else:
                    # Regular RTSP settings
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

                # Small fix for cameras that don't report FPS properly
                try:
                    self.fps = float(self.stream.average_rate) or 30
                except Exception:
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

                # For webcam testing, skip codec support check as it varies between cameras
                if not is_webcam and self.codec_name.lower() not in Config.SUPPORTED_CODECS:
                    logger.log_codec_error(self.codec_name)
                    self.error_occurred.emit(f"Unsupported codec: {self.codec_name}")
                    # Stop gracefully to clean up resources
                    self.stop()
                    return

                self.frame_count = 0
                self.last_frame_time = time.time()

                # Start the loop that reads frames in a separate thread
                self.capture_thread = threading.Thread(
                    target=self._capture_frames,
                    daemon=True,
                    name="RTSPStreamCapture"
                )
                self.capture_thread.start()

            except Exception as e:
                # Connection error - notify GUI and clean up state
                error_msg = str(e)
                
                # Provide user-friendly error messages
                if "Invalid data found" in error_msg:
                    user_msg = "The stream source returned invalid data. Please check the URL or try a different stream."
                elif "I/O error" in error_msg and "video=" in self.rtsp_url:
                    # Webcam error - try to provide helpful suggestions
                    from utils.webcam_utils import get_available_webcams
                    available = get_available_webcams()
                    if available:
                        user_msg = f"Webcam not found. Available cameras: {', '.join(available)}"
                    else:
                        user_msg = "Webcam not found. Try using the full camera name (e.g., 'video=Integrated Camera')"
                elif "Connection refused" in error_msg:
                    user_msg = "Connection refused. Check if the RTSP server is running and accessible."
                elif "timed out" in error_msg.lower():
                    user_msg = "Connection timeout. Check your network connection and firewall settings."
                else:
                    user_msg = f"Connection error: {error_msg}"
                
                logger.log_error("CONNECTION_ERROR", f"Failed to open stream: {e}", "ERR_STREAM_OPEN")
                self.error_occurred.emit(user_msg)
                self.stop()

        # Start connection in background thread
        self._connect_thread = threading.Thread(
            target=_connect_and_start,
            daemon=True,
            name="RTSPConnect"
        )
        self._connect_thread.start()

        # Immediately return control to GUI
        return True
    
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
