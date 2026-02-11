"""
URL Validator - Validates RTSP URLs against required format.
Supports flexible RTSP URL formats including credentials, optional port, and optional path.
"""

import re
from typing import Tuple
from urllib.parse import urlparse
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
        """
        Validate RTSP URL format with flexible parsing.
        
        Supports:
        - rtsp://host/path (port defaults to 554)
        - rtsp://host:port/path
        - rtsp://user:pass@host:port/path
        - rtsp://host (path optional)
        
        Args:
            url: URL string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if empty
        if not url or not url.strip():
            # Use centralized message from Config to maintain consistency
            return False, Config.ERROR_MESSAGES.get("EMPTY_URL", "URL cannot be empty")

        url = url.strip()

        # Check if starts with rtsp://
        if not url.lower().startswith('rtsp://'):
            return False, "URL must start with 'rtsp://'"

        # Check format with flexible regex
        if not re.match(URLValidator.RTSP_PATTERN, url, re.IGNORECASE):
            return False, "Invalid URL format. Expected: rtsp://[user:pass@]host[:port][/path]"

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
