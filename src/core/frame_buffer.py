"""
Frame Buffer Manager - Implements Latest Frame Policy with watchdog.
"""

import threading
import time
from typing import Optional, Callable
import numpy as np
from utils.logger import get_logger
from utils.config import Config


class FrameBuffer:
    """
    Single-frame buffer with Latest Frame Policy.
    Implements watchdog mechanism for stream monitoring.
    Thread-safe with daemon watchdog thread.
    """

    def __init__(self):
        self.logger = get_logger()
        self.current_frame: Optional[np.ndarray] = None
        self.frame_lock = threading.Lock()
        
        # Watchdog
        self.last_frame_time = time.time()
        self.watchdog_running = False
        self.watchdog_thread: Optional[threading.Thread] = None
        
        # Callbacks (thread-safe)
        self.on_frame_ready: Optional[Callable] = None
        self.on_timeout: Optional[Callable] = None

    def put_frame(self, frame: np.ndarray):
        """
        Put a new frame into the buffer.
        Immediately overwrites the previous frame (Strict Latest Frame Policy).
        Zero-copy: stores reference to frame data.
        Atomic swap: minimal lock contention to prevent GUI starvation.
        
        Thread-safe: Uses lock for atomic frame swap.
        Callback executed outside lock to prevent blocking frame delivery.
        
        Args:
            frame: NumPy array in RGB24 format from PyAV
            
        Raises:
            ValueError: If frame is None or invalid
        """
        if frame is None:
            self.logger.log_error("FRAME_ERROR", "Attempted to put None frame")
            return
        
        if not isinstance(frame, np.ndarray):
            self.logger.log_error("FRAME_ERROR", f"Invalid frame type: {type(frame)}")
            return
        
        # Atomic swap: minimal lock duration
        with self.frame_lock:
            self.current_frame = frame
            self.last_frame_time = time.time()
        
        # Notify outside lock to prevent callback blocking frame delivery
        if self.on_frame_ready:
            try:
                self.on_frame_ready()
            except Exception as e:
                self.logger.log_error("CALLBACK_ERROR", f"Frame ready callback error: {e}")

    def get_frame(self) -> Optional[np.ndarray]:
        """
        Get the current frame from the buffer (zero-copy).
        Returns direct reference to frame data without copying.
        
        Returns:
            NumPy array or None if no frame available
        """
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame
        return None

    def clear(self):
        """Clear the buffer."""
        with self.frame_lock:
            self.current_frame = None
        self.last_frame_time = time.time()

    def start_watchdog(self):
        """Start the watchdog monitoring thread."""
        if self.watchdog_running:
            return
        
        self.watchdog_running = True
        self.watchdog_thread = threading.Thread(
            target=self._watchdog_loop,
            daemon=True,
            name="FrameBufferWatchdog"
        )
        self.watchdog_thread.start()
        self.logger.log_ui_event("Watchdog started")

    def stop_watchdog(self):
        """Stop the watchdog monitoring thread."""
        self.watchdog_running = False
        if self.watchdog_thread:
            self.watchdog_thread.join(timeout=1)
        self.logger.log_ui_event("Watchdog stopped")

    def _watchdog_loop(self):
        """
        Watchdog loop - monitors frame arrival with 2.5s timeout.
        Checks every 100ms for frame timeout.
        Triggers reconnection if no frames received.
        
        Thread-safe: Uses time.time() which is thread-safe.
        Prevents repeated timeout triggers by resetting timer only once per timeout.
        """
        timeout_triggered = False
        
        while self.watchdog_running:
            time.sleep(Config.WATCHDOG_CHECK_INTERVAL)
            
            elapsed = time.time() - self.last_frame_time
            
            # Timeout threshold: 2.5 seconds
            if elapsed > Config.WATCHDOG_TIMEOUT:
                if not timeout_triggered:
                    self.logger.log_timeout(Config.WATCHDOG_TIMEOUT)
                    
                    if self.on_timeout:
                        try:
                            self.on_timeout()
                        except Exception as e:
                            self.logger.log_error("TIMEOUT_CALLBACK_ERROR", f"Timeout callback error: {e}")
                    
                    timeout_triggered = True
            else:
                # Reset flag when frames resume
                timeout_triggered = False

    def reset_frame_timer(self):
        """
        Reset the frame timer (called when stream reconnects).
        Thread-safe: Uses lock to protect timer reset.
        """
        with self.frame_lock:
            self.last_frame_time = time.time()

    def get_buffer_stats(self) -> dict:
        """Get buffer statistics."""
        with self.frame_lock:
            has_frame = self.current_frame is not None
            frame_size = self.current_frame.nbytes if has_frame else 0
        
        return {
            "has_frame": has_frame,
            "frame_size_bytes": frame_size,
            "time_since_last_frame": time.time() - self.last_frame_time,
        }
