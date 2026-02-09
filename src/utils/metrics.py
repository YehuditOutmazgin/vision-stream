"""
Metrics - Performance metrics and counters for VisionStream.
"""

import time


class FPSCounter:
    """
    FPS (Frames Per Second) counter for real-time performance monitoring.
    
    Tracks frame count and calculates actual FPS every second.
    Thread-safe for use in multi-threaded environments.
    """

    def __init__(self):
        """Initialize FPS counter."""
        self.start_time = time.time()
        self.frame_count = 0
        self.current_fps = 0.0

    def update(self) -> float:
        """
        Update frame count and calculate FPS if 1 second has elapsed.
        
        Call this method once per frame for accurate FPS calculation.
        
        Returns:
            Current FPS (updated every 1 second, otherwise returns previous value)
        """
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        
        # Update FPS every 1 second
        if elapsed >= 1.0:
            self.current_fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()
        
        return self.current_fps

    def get_fps(self) -> float:
        """
        Get current FPS without updating.
        
        Returns:
            Current FPS value
        """
        return self.current_fps

    def reset(self):
        """Reset FPS counter."""
        self.start_time = time.time()
        self.frame_count = 0
        self.current_fps = 0.0


class LatencyTracker:
    """
    Track glass-to-glass latency (frame capture to display).
    
    Useful for monitoring real-time performance and detecting bottlenecks.
    """

    def __init__(self, window_size: int = 30):
        """
        Initialize latency tracker.
        
        Args:
            window_size: Number of frames to average over
        """
        self.window_size = window_size
        self.latencies = []
        self.avg_latency = 0.0

    def record(self, latency_ms: float):
        """
        Record a latency measurement.
        
        Args:
            latency_ms: Latency in milliseconds
        """
        self.latencies.append(latency_ms)
        
        # Keep only last window_size measurements
        if len(self.latencies) > self.window_size:
            self.latencies.pop(0)
        
        # Calculate average
        if self.latencies:
            self.avg_latency = sum(self.latencies) / len(self.latencies)

    def get_average(self) -> float:
        """
        Get average latency.
        
        Returns:
            Average latency in milliseconds
        """
        return self.avg_latency

    def get_max(self) -> float:
        """
        Get maximum latency in current window.
        
        Returns:
            Maximum latency in milliseconds
        """
        return max(self.latencies) if self.latencies else 0.0

    def get_min(self) -> float:
        """
        Get minimum latency in current window.
        
        Returns:
            Minimum latency in milliseconds
        """
        return min(self.latencies) if self.latencies else 0.0

    def reset(self):
        """Reset latency tracker."""
        self.latencies = []
        self.avg_latency = 0.0
