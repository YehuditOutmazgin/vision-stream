"""Unit tests for ReconnectionManager."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
import time
from core.reconnection_manager import ReconnectionManager, StreamState


class TestReconnectionManager(unittest.TestCase):
    """Test cases for ReconnectionManager state machine."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = ReconnectionManager()
        self.state_changes = []
        self.reconnect_attempts = []
        self.max_retries_called = False

        # Register callbacks
        self.manager.on_state_changed = lambda state: self.state_changes.append(state)
        self.manager.on_reconnect_attempt = lambda attempt, delay: self.reconnect_attempts.append((attempt, delay))
        self.manager.on_max_retries_exceeded = lambda: self._set_max_retries_called()

    def _set_max_retries_called(self):
        """Helper to set max retries flag."""
        self.max_retries_called = True

    def test_initial_state(self):
        """Test initial state is IDLE."""
        self.assertEqual(self.manager.get_state(), StreamState.IDLE)

    def test_start_connection(self):
        """Test starting connection changes state to CONNECTING."""
        self.manager.start_connection()
        self.assertEqual(self.manager.get_state(), StreamState.CONNECTING)
        self.assertIn(StreamState.CONNECTING, self.state_changes)

    def test_connection_success(self):
        """Test successful connection changes state to PLAYING."""
        self.manager.start_connection()
        self.manager.connection_success()
        self.assertEqual(self.manager.get_state(), StreamState.PLAYING)
        self.assertEqual(self.manager.attempt_count, 0)

    def test_connection_failed_first_attempt(self):
        """Test first connection failure triggers retry."""
        self.manager.start_connection()
        self.manager.connection_failed("Test error")
        
        self.assertEqual(self.manager.attempt_count, 1)
        self.assertEqual(len(self.reconnect_attempts), 1)
        self.assertEqual(self.reconnect_attempts[0][0], 1)  # Attempt 1

    def test_max_retries_exceeded(self):
        """Test max retries exceeded changes state to ERROR."""
        self.manager.start_connection()
        
        # Simulate 5 failed attempts
        for _ in range(5):
            self.manager.connection_failed("Test error")
        
        self.assertEqual(self.manager.get_state(), StreamState.ERROR)
        self.assertTrue(self.max_retries_called)

    def test_user_stop_resets_state(self):
        """Test user stop resets state to IDLE."""
        self.manager.start_connection()
        self.manager.connection_failed("Test error")
        self.manager.user_stop()
        
        self.assertEqual(self.manager.get_state(), StreamState.IDLE)
        self.assertEqual(self.manager.attempt_count, 0)

    def test_stream_interrupted_from_playing(self):
        """Test stream interruption from PLAYING state."""
        self.manager.start_connection()
        self.manager.connection_success()
        self.manager.stream_interrupted()
        
        self.assertEqual(self.manager.attempt_count, 1)
        self.assertNotEqual(self.manager.get_state(), StreamState.PLAYING)

    def test_reset(self):
        """Test reset clears state and attempts."""
        self.manager.start_connection()
        self.manager.connection_failed("Test error")
        self.manager.reset()
        
        self.assertEqual(self.manager.get_state(), StreamState.IDLE)
        self.assertEqual(self.manager.attempt_count, 0)

    def test_get_retry_info(self):
        """Test retry info returns correct data."""
        self.manager.start_connection()
        self.manager.connection_failed("Test error")
        
        info = self.manager.get_retry_info()
        self.assertEqual(info["attempt"], 1)
        self.assertEqual(info["remaining_attempts"], 4)

    def test_interrupt_wait(self):
        """Test interrupt wait can stop reconnection delay."""
        self.manager.start_connection()
        
        # Start connection failure in background (would normally wait)
        import threading
        def fail_connection():
            self.manager.connection_failed("Test error")
        
        thread = threading.Thread(target=fail_connection)
        start_time = time.time()
        thread.start()
        
        # Interrupt immediately
        time.sleep(0.1)
        self.manager.interrupt_wait()
        thread.join(timeout=1.0)
        
        elapsed = time.time() - start_time
        # Should complete quickly (< 1 second) instead of waiting full delay
        self.assertLess(elapsed, 1.0)


if __name__ == "__main__":
    unittest.main()
