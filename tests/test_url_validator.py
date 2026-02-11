"""Unit tests for URLValidator."""
import sys
from pathlib import Path
import tempfile
import os
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
        self.assertIn("unsupported protocol", error.lower())

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

    def test_local_file_path_not_found(self):
        """Test local file path that doesn't exist."""
        is_valid, error = URLValidator.validate("C:\\Videos\\nonexistent.mp4")
        self.assertFalse(is_valid)
        self.assertIn("not found", error.lower())

    def test_local_file_path_exists(self):
        """Test local file path that exists."""
        # Create a temporary video file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            is_valid, error = URLValidator.validate(tmp_path)
            self.assertTrue(is_valid)
            self.assertEqual(error, "")
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_local_file_invalid_extension(self):
        """Test local file with non-video extension."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            is_valid, error = URLValidator.validate(tmp_path)
            self.assertFalse(is_valid)
            self.assertIn("unsupported", error.lower())
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_webcam_identifier_video_prefix(self):
        """Test webcam identifier with video= prefix."""
        is_valid, error = URLValidator.validate("video=Integrated Camera")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_webcam_identifier_digit(self):
        """Test webcam identifier as digit."""
        is_valid, error = URLValidator.validate("0")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")


if __name__ == "__main__":
    unittest.main()
