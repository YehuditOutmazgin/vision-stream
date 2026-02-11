"""Unit tests for URLValidator."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from utils.url_validator import URLValidator


class TestURLValidator(unittest.TestCase):
    """Test cases for URLValidator."""

    def test_empty_url(self):
        """Test validation of empty URL."""
        is_valid, error = URLValidator.validate("")
        self.assertFalse(is_valid)
        self.assertIn("empty", error.lower())

    def test_whitespace_url(self):
        """Test validation of whitespace-only URL."""
        is_valid, error = URLValidator.validate("   ")
        self.assertFalse(is_valid)
        self.assertIn("empty", error.lower())

    def test_valid_rtsp_basic(self):
        """Test valid basic RTSP URL."""
        is_valid, error = URLValidator.validate("rtsp://192.168.1.100:554/stream")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_valid_rtsp_no_port(self):
        """Test valid RTSP URL without port (defaults to 554)."""
        is_valid, error = URLValidator.validate("rtsp://camera.local/live")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_valid_rtsp_with_credentials(self):
        """Test valid RTSP URL with username and password."""
        is_valid, error = URLValidator.validate("rtsp://admin:password123@192.168.1.100:554/stream")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_valid_rtsp_no_path(self):
        """Test valid RTSP URL without path."""
        is_valid, error = URLValidator.validate("rtsp://192.168.1.100:554")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_invalid_no_rtsp_prefix(self):
        """Test invalid URL without rtsp:// prefix."""
        is_valid, error = URLValidator.validate("http://192.168.1.100:554/stream")
        self.assertFalse(is_valid)
        self.assertIn("rtsp://", error.lower())

    def test_invalid_malformed_host(self):
        """Test invalid URL with malformed host."""
        # Note: 999.999.999.999 passes regex but would fail on actual connection
        is_valid, error = URLValidator.validate("rtsp://invalid host:554/stream")
        self.assertFalse(is_valid)

    def test_invalid_port_out_of_range(self):
        """Test invalid URL with port out of range."""
        is_valid, error = URLValidator.validate("rtsp://192.168.1.100:99999/stream")
        self.assertFalse(is_valid)

    def test_invalid_username_without_password(self):
        """Test invalid URL with username but no password."""
        is_valid, error = URLValidator.validate("rtsp://admin@192.168.1.100:554/stream")
        self.assertFalse(is_valid)
        # Error message should indicate format issue
        self.assertIn("format", error.lower())

    def test_local_file_path(self):
        """Test local file path (not RTSP)."""
        is_valid, error = URLValidator.validate("C:\\Videos\\sample.mp4")
        self.assertFalse(is_valid)
        self.assertIn("rtsp://", error.lower())

    def test_webcam_identifier(self):
        """Test webcam identifier (not RTSP)."""
        is_valid, error = URLValidator.validate("video=Integrated Camera")
        self.assertFalse(is_valid)
        self.assertIn("rtsp://", error.lower())


if __name__ == "__main__":
    unittest.main()
