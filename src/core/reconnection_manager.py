"""
Reconnection Manager - Handles automatic reconnection with exponential backoff.
"""

import threading
import time
from enum import Enum
from typing import Callable, Optional
from utils.logger import get_logger
from utils.config import Config


class StreamState(Enum):
    """Stream connection states."""
    IDLE = "idle"
    CONNECTING = "connecting"
    PLAYING = "playing"
    RETRY = "retry"
    ERROR = "error"


class ReconnectionManager:
    """
    Manages automatic reconnection with exponential backoff.
    Implements state machine for stream lifecycle.
    Uses interruptible wait to allow immediate stop during reconnection delays.
    """

    def __init__(self):
        self.logger = get_logger()
        self.state = StreamState.IDLE
        self.attempt_count = 0
        self.state_lock = threading.Lock()
        self.current_wait_time = 0
        
        # Interruptible wait event for reconnection delays
        self.wait_event = threading.Event()
        self.wait_event.set()  # Initially not waiting
        
        # Callbacks
        self.on_state_changed: Optional[Callable[[StreamState], None]] = None
        self.on_reconnect_attempt: Optional[Callable[[int, int], None]] = None
        self.on_max_retries_exceeded: Optional[Callable[[], None]] = None
    
    def interrupt_wait(self):
        """Interrupt any ongoing wait during reconnection delay."""
        self.wait_event.set()

    def get_state(self) -> StreamState:
        """Get current stream state."""
        with self.state_lock:
            return self.state

    def set_state(self, new_state: StreamState):
        """
        Set stream state and trigger callback.
        Thread-safe: Uses lock to protect state changes.
        
        Args:
            new_state: New StreamState
        """
        with self.state_lock:
            if self.state != new_state:
                self.state = new_state
                if self.on_state_changed:
                    try:
                        self.on_state_changed(new_state)
                    except Exception as e:
                        self.logger.log_error("STATE_CALLBACK_ERROR", f"State change callback error: {e}")

    def start_connection(self):
        """Start connection attempt."""
        self.attempt_count = 0
        self.set_state(StreamState.CONNECTING)
        self.logger.log_ui_event("Starting connection")

    def connection_success(self):
        """Handle successful connection."""
        self.attempt_count = 0
        self.set_state(StreamState.PLAYING)
        self.logger.log_reconnect_success()

    def connection_failed(self, error: str = ""):
        """
        Handle connection failure and trigger reconnection logic.
        Uses interruptible wait to allow immediate stop during reconnection delays.
        Implements exponential backoff with maximum retry limit.
        
        Thread-safe: Uses lock to protect state and attempt count.
        
        Args:
            error: Error message
        """
        # Check if we're already in error state (max retries exceeded)
        if self.state == StreamState.ERROR:
            return
        
        self.attempt_count += 1
        
        if self.attempt_count >= Config.MAX_RECONNECTION_ATTEMPTS:
            self.set_state(StreamState.ERROR)
            self.logger.log_error(
                "MAX_RETRIES",
                f"Maximum reconnection attempts ({Config.MAX_RECONNECTION_ATTEMPTS}) exceeded",
                "ERR_MAX_RETRIES"
            )
            if self.on_max_retries_exceeded:
                try:
                    self.on_max_retries_exceeded()
                except Exception as e:
                    self.logger.log_error("MAX_RETRIES_CALLBACK_ERROR", f"Max retries callback error: {e}")
            return
        
        # Calculate wait time with bounds checking
        wait_index = min(self.attempt_count - 1, len(Config.RECONNECTION_DELAYS) - 1)
        wait_time = Config.RECONNECTION_DELAYS[wait_index]
        
        with self.state_lock:
            self.current_wait_time = wait_time
        
        self.set_state(StreamState.RETRY)
        self.logger.log_reconnect_attempt(self.attempt_count, wait_time)
        
        if self.on_reconnect_attempt:
            try:
                self.on_reconnect_attempt(self.attempt_count, wait_time)
            except Exception as e:
                self.logger.log_error("RECONNECT_CALLBACK_ERROR", f"Reconnect attempt callback error: {e}")
        
        # Interruptible wait before retry (can be interrupted by user stop)
        if wait_time > 0:
            self.wait_event.clear()
            self.wait_event.wait(timeout=wait_time)
        
        # Check again if we're in error state before transitioning
        if self.state != StreamState.ERROR:
            self.set_state(StreamState.CONNECTING)

    def stream_interrupted(self):
        """Handle stream interruption (watchdog timeout)."""
        if self.state == StreamState.PLAYING:
            self.logger.log_disconnection("Stream interrupted - no frames")
            self.connection_failed("Stream timeout")

    def user_stop(self):
        """
        Handle user-initiated stop.
        Thread-safe: Interrupts any ongoing reconnection delay.
        Resets state and attempt counter.
        """
        self.attempt_count = 0
        self.interrupt_wait()  # Interrupt any ongoing reconnection delay
        self.set_state(StreamState.IDLE)
        self.logger.log_disconnection("User stopped")

    def reset(self):
        """Reset reconnection manager."""
        self.attempt_count = 0
        self.set_state(StreamState.IDLE)

    def get_retry_info(self) -> dict:
        """
        Get current retry information.
        Thread-safe: Uses lock to protect access to state variables.
        
        Returns:
            Dictionary with retry state information
        """
        with self.state_lock:
            return {
                "state": self.state.value,
                "attempt": self.attempt_count,
                "max_attempts": Config.MAX_RECONNECTION_ATTEMPTS,
                "remaining_attempts": Config.MAX_RECONNECTION_ATTEMPTS - self.attempt_count,
                "current_wait_time": self.current_wait_time,
            }
