"""
RTSP & Multi-Source Stream Engine - Handles video decoding using PyAV/FFmpeg.
Supports RTSP, Local Webcams (dshow), and Video Files.
"""
import av
import av.error
import threading
import time
import os
from typing import Optional, Callable, Any, Dict
import numpy as np
from PySide6.QtCore import QObject, Signal
from utils.logger import get_logger
from utils.config import Config
from core.frame_buffer import FrameBuffer

logger = get_logger()

class RTSPStreamEngine(QObject):
    """
    Stream Engine for handling video decoding and frame processing.
    Uses PyAV/FFmpeg for ultra-low latency streaming with H.264/H.265 support.
    Integrates FrameBuffer with Latest Frame Policy and Watchdog monitoring.
    """
    
    frame_ready = Signal(np.ndarray)
    fps_updated = Signal(float)
    error_occurred = Signal(str)
    connection_established = Signal(dict)
    
    def __init__(self, rtsp_url: str):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.container = None
        self.stream = None
        self.is_running = False
        self.capture_thread = None
        self.frame_callbacks = []
        self.fps_callbacks = []
        self.fps = 30
        self.frame_count = 0
        self.last_frame_time = time.time()
        self.codec_name = None
        self.width = None
        self.height = None
        self.connection_timeout = Config.RTSP_TIMEOUT
        self.interrupt_event = threading.Event()
        
        # Frame buffer with watchdog
        self.frame_buffer = FrameBuffer()
        self.frame_buffer.on_frame_ready = self._on_frame_ready
        self.frame_buffer.on_timeout = self._on_frame_timeout
        
    def add_frame_callback(self, callback: Callable[[np.ndarray], Any]):
        self.frame_callbacks.append(callback)
    
    def add_fps_callback(self, callback: Callable[[float], Any]):
        self.fps_callbacks.append(callback)
        
    def remove_frame_callback(self, callback: Callable[[np.ndarray], Any]):
        if callback in self.frame_callbacks:
            self.frame_callbacks.remove(callback)
    
    def remove_fps_callback(self, callback: Callable[[float], Any]):
        if callback in self.fps_callbacks:
            self.fps_callbacks.remove(callback)

    def start(self) -> bool:
        """
        Start streaming from the provided source.
        Supports RTSP, local files, and webcams.
        
        Returns:
            True if stream started successfully, False otherwise
        """
        if self.is_running:
            logger.log_ui_event("Stream is already running")
            return True
            
        try:
            is_webcam = "video=" in self.rtsp_url or self.rtsp_url.isdigit()
            is_file = os.path.isfile(self.rtsp_url)
            
            options = Config.FFMPEG_OPTIONS.copy()
            
            try:
                if is_webcam:
                    device_name = self.rtsp_url if "video=" in self.rtsp_url else f"video={self.rtsp_url}"
                    logger.log_ui_event(f"Attempting to open webcam: {device_name}")
                    self.container = av.open(
                        device_name,
                        format='dshow',
                        options={'framerate': '30', 'video_size': '640x480'}
                    )
                elif is_file:
                    logger.log_ui_event(f"Attempting to open local file: {self.rtsp_url}")
                    self.container = av.open(self.rtsp_url)
                else:
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
            except Exception as e:
                # Ensure container is closed if opening failed
                if self.container:
                    try:
                        self.container.close()
                    except:
                        pass
                    self.container = None
                raise e
            
            if not self.container or len(self.container.streams.video) == 0:
                raise ValueError("No video streams found in the provided source")

            self.stream = self.container.streams.video[0]
            
            if not self.stream:
                raise ValueError("Failed to get video stream")
            
            self.codec_name = self.stream.codec_context.name
            self.width = self.stream.width
            self.height = self.stream.height
            
            try:
                self.fps = float(self.stream.average_rate) or 30
            except:
                self.fps = 30
            
            logger.log_connection(self.rtsp_url)
            logger.log_codec_info(self.codec_name, f"{self.width}x{self.height}", int(self.fps))
            
            self.connection_established.emit({
                'codec': self.codec_name,
                'resolution': f"{self.width}x{self.height}",
                'fps': int(self.fps)
            })
            
            if not (is_webcam or is_file) and self.codec_name.lower() not in Config.SUPPORTED_CODECS:
                logger.log_codec_error(self.codec_name)
                self.error_occurred.emit(f"Unsupported codec: {self.codec_name}")
                return False
            
            self.is_running = True
            self.interrupt_event.clear()
            self.frame_count = 0
            self.last_frame_time = time.time()
            
            # Start watchdog monitoring
            self.frame_buffer.start_watchdog()
            
            self.capture_thread = threading.Thread(
                target=self._capture_frames,
                daemon=True,
                name="StreamCaptureThread"
            )
            self.capture_thread.start()
            
            return True
            
        except Exception as e:
            logger.log_error("CONNECTION_ERROR", f"Failed to open source: {e}")
            self.error_occurred.emit(f"Source error: {str(e)}")
            self.is_running = False
            return False

    def stop(self):
        """
        Stop the stream engine and cleanup resources.
        Thread-safe: Signals capture thread to stop and waits for it.
        Cleans up all callbacks and closes container.
        """
        self.is_running = False
        self.interrupt_event.set()
        
        # Stop watchdog
        self.frame_buffer.stop_watchdog()
        
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
        
        # Clear callbacks to prevent memory leaks
        self.frame_callbacks.clear()
        self.fps_callbacks.clear()
        
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
        Capture frames from the stream in a separate thread.
        Handles frame decoding, conversion, and callback execution.
        Uses FrameBuffer with Latest Frame Policy and Watchdog monitoring.
        
        Thread-safe: Runs in daemon thread, uses signals for GUI updates.
        Handles exceptions gracefully without crashing the thread.
        """
        try:
            if not self.container or not self.stream:
                logger.log_error("DECODE_ERROR", "Container or stream is None")
                self.error_occurred.emit("Stream error: Invalid container or stream")
                return
            
            # Calculate target time between frames (e.g., 0.033s for 30 FPS)
            frame_sleep = 1.0 / self.fps if self.fps > 0 else 0.03
            
            for frame in self.container.decode(self.stream):
                if not self.is_running or self.interrupt_event.is_set():
                    break
                
                try:
                    start_time = time.time()
                    
                    # Convert frame to RGB24 NumPy array
                    rgb_frame = frame.to_ndarray(format=Config.TARGET_PIXEL_FORMAT)
                    self.frame_count += 1
                    current_time = time.time()
                    
                    # Put frame into buffer (Latest Frame Policy)
                    self.frame_buffer.put_frame(rgb_frame)
                    
                    # Execute all registered frame callbacks (e.g., for AI processing or recording)
                    for callback in self.frame_callbacks:
                        try:
                            callback(rgb_frame)
                        except Exception as e:
                            logger.log_error("CALLBACK_ERROR", f"Error in frame callback: {e}")
                    
                    # [Optimization for Local Files] 
                    # Pace the decoding to match original FPS to save CPU/GPU and ensure smooth motion.
                    # Only active for local files; live streams remain real-time.
                    if os.path.isfile(self.rtsp_url):
                        processing_time = time.time() - start_time
                        sleep_time = max(0, frame_sleep - processing_time)
                        time.sleep(sleep_time)

                    # Calculate and emit actual FPS every 30 frames
                    if self.frame_count % 30 == 0:
                        elapsed = current_time - self.last_frame_time
                        actual_fps = 30 / elapsed if elapsed > 0 else 0
                        
                        self.fps_updated.emit(actual_fps)
                        
                        # Execute FPS callbacks
                        for callback in self.fps_callbacks:
                            try:
                                callback(actual_fps)
                            except Exception as e:
                                logger.log_error("FPS_CALLBACK_ERROR", f"Error in FPS callback: {e}")
                        
                        self.last_frame_time = current_time
                
                except Exception as e:
                    logger.log_error("FRAME_PROCESSING_ERROR", f"Error processing frame: {e}")
                    # Continue processing next frame instead of crashing
                    continue
                            
        except Exception as e:
            if self.is_running:
                logger.log_error("DECODE_ERROR", f"Error during streaming: {e}", "ERR_DECODE")
                self.error_occurred.emit(f"Stream error: {str(e)}")
        finally:
            logger.log_ui_event("Frame capture thread ended")
            self.is_running = False
    
    def _on_frame_ready(self):
        """Callback when frame is ready in buffer."""
        frame = self.frame_buffer.get_frame()
        if frame is not None:
            self.frame_ready.emit(frame)
    
    def _on_frame_timeout(self):
        """Callback when watchdog detects frame timeout."""
        logger.log_timeout(Config.WATCHDOG_TIMEOUT)
        if self.is_running:
            # Trigger reconnection through error signal
            self.error_occurred.emit(f"Stream timeout: No frames received for {Config.WATCHDOG_TIMEOUT}s")

    def is_connected(self) -> bool:
        return self.is_running and self.container is not None
    
    def get_stream_info(self) -> dict:
        if not self.container or not self.stream:
            return {}
        return {
            'url': self.rtsp_url,
            'codec': self.codec_name,
            'fps': self.fps,
            'width': self.width,
            'height': self.height,
            'is_connected': self.is_connected(),
        }
    
    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()