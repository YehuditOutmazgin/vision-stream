"""
URL Validator - Validates RTSP URLs against required format.
Supports flexible RTSP URL formats including credentials, optional port, and optional path.
"""

import re
from typing import Tuple
from urllib.parse import urlparse
from pathlib import Path
from .config import Config


class URLValidator:
    """Validates RTSP URLs with flexible format support."""

    # Flexible RTSP URL pattern supporting:
    # - Optional credentials: user:pass@
    # - Optional port (defaults to 554)
    # - Optional path
    # Pattern: rtsp://[user:pass@]host[:port][/path]
    RTSP_PATTERN = r'^rtsp://(?:(?:[^:@]+):(?:[^@]+)@)?(?:[a-zA-Z0-9\-\.]+|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:/.*)?$'

    @staticmethod
    def validate(url: str) -> Tuple[bool, str]:
        r"""
        Validate RTSP URL, local file path, or webcam identifier.
        
        Supports:
        - RTSP URLs: rtsp://[user:pass@]host[:port][/path]
        - Local files: C:\path\to\video.mp4 or relative paths
        - Webcam: video=Camera Name or device index (0, 1, etc.)
        
        Args:
            url: URL string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if empty
        if not url or not url.strip():
            return False, Config.ERROR_MESSAGES.get("EMPTY_URL", "URL cannot be empty")

        url = url.strip()

        # Check if it's a webcam identifier (video= or just a digit)
        if url.startswith('video=') or url.isdigit():
            # Webcam identifiers are always valid (actual availability checked at connection time)
            return True, ""

        # Check for unsupported protocols (http, https, ftp, etc.)
        unsupported_protocols = ['http://', 'https://', 'ftp://', 'file://']
        for protocol in unsupported_protocols:
            if url.lower().startswith(protocol):
                return False, f"Unsupported protocol. Only RTSP streams are supported. Use rtsp:// instead of {protocol}"

        # Check if it's a local file path
        if not url.lower().startswith('rtsp://'):
            # Treat as local file path - check if it looks like a file path
            # File paths typically contain: \ or / or : (drive letter) or have file extension
            looks_like_path = ('/' in url or '\\' in url or ':' in url or '.' in url)
            
            if not looks_like_path:
                # Doesn't look like RTSP or file path - unclear input
                return False, "Invalid input. Expected RTSP URL (rtsp://...) or file path (C:/path/to/video.mp4)"
            
            # Try to validate as file path
            try:
                file_path = Path(url)
                
                # Check if file exists
                if not file_path.exists():
                    return False, f"File not found: {url}"
                
                # Check if it's actually a file (not a directory)
                if not file_path.is_file():
                    return False, f"Path is not a file: {url}"
                
                # Check if it has a video extension
                video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.m4v', '.mpg', '.mpeg'}
                if file_path.suffix.lower() not in video_extensions:
                    return False, f"Unsupported file type: {file_path.suffix}. Expected video file (.mp4, .avi, etc.)"
                
                return True, ""
            except (OSError, ValueError) as e:
                # Path is invalid or inaccessible
                return False, f"Invalid file path: {url}"

        # RTSP URL validation
        if not re.match(URLValidator.RTSP_PATTERN, url, re.IGNORECASE):
            return False, "Invalid RTSP URL format. Expected: rtsp://[user:pass@]host[:port][/path]"

        # Additional validation using urllib.parse
        try:
            parsed = urlparse(url)
            
            # Validate host
            if not parsed.hostname:
                return False, "Host cannot be empty"
            
            # Validate port if specified
            if parsed.port is not None:
                if parsed.port < 1 or parsed.port > 65535:
                    return False, "Port must be between 1 and 65535"
            
            # Validate credentials if present
            if parsed.username and not parsed.password:
                return False, "If username is provided, password must also be provided"
            
            return True, ""

        except Exception as e:
            return False, f"URL validation error: {str(e)}"

    @staticmethod
    def get_error_message(url: str) -> str:
        """Get validation error message for a URL."""
        is_valid, error_msg = URLValidator.validate(url)
        return error_msg if not is_valid else ""
