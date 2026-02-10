"""
UI Manager - Handles UI state management and updates.
Manages button states, labels, and visual feedback.
"""

from core.reconnection_manager import StreamState


class UIManager:
    """Manages UI state and updates."""
    
    def __init__(self, play_btn, fps_display, status_label, video_display, control_panel):
        self.play_btn = play_btn
        self.fps_display = fps_display
        self.status_label = status_label
        self.video_display = video_display
        self.control_panel = control_panel
    
    def set_playing(self):
        """Update UI for playing state."""
        self.play_btn.setText("⏹ Stop")
        self.control_panel.toggle_enabled(False)
        self.status_label.hide()
        self.status_label.setText("")  # Clear any previous status text
    
    def set_stopped(self):
        """Update UI for stopped state."""
        self.play_btn.setText("▶ Play")
        self.control_panel.toggle_enabled(True)
        self.video_display.clear_display()
        self.fps_display.setText("FPS: 0.0")  # Reset FPS to 0
        self.status_label.hide()
    
    def set_connecting(self):
        """Update UI for connecting state."""
        self.status_label.setText("🔄 Connecting...")
        self.status_label.show()
    
    def set_reconnecting(self, attempt, wait_time):
        """Update UI for reconnecting state."""
        self.status_label.setText(f"⏳ Reconnecting... (Attempt {attempt}, waiting {wait_time}s)")
        self.status_label.show()
    
    def set_error(self, error_msg):
        """Update UI for error state."""
        self.play_btn.setText("▶ Play")
        self.control_panel.toggle_enabled(True)
        self.status_label.setText("❌ Connection failed. Click Play to retry.")
        self.status_label.show()
        self.fps_display.hide()
        self.video_display.clear_display()
    
    def update_fps(self, fps):
        """Update FPS display."""
        self.fps_display.setText(f"FPS: {fps:.1f}")
    
    def handle_state_change(self, state_value, error_msg=None):
        """Handle reconnection state changes."""
        if state_value == StreamState.CONNECTING.value:
            self.set_connecting()
        elif state_value == StreamState.PLAYING.value:
            self.set_playing()
        elif state_value == StreamState.RETRY.value:
            # Don't change UI during retry, just show reconnecting message
            pass
        elif state_value == StreamState.ERROR.value:
            self.set_error(error_msg or "Connection failed")
        elif state_value == "playing":
            self.set_playing()
        elif state_value == "error":
            self.set_error(error_msg or "Stream error")
