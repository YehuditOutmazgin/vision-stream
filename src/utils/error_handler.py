"""
Error Handler - Translates technical errors to user-friendly messages.
"""

import re


class ErrorHandler:
    """Converts technical errors to clear user messages."""

    @staticmethod
    def get_user_friendly_message(error_str: str) -> str:
        """
        Convert technical error messages to user-friendly messages.
        
        Args:
            error_str: Technical error message
            
        Returns:
            User-friendly error message
        """
        error_lower = error_str.lower()
        
        # Connection timeout errors
        if "timeout" in error_lower or "timed out" in error_lower:
            return "Connection timeout: The server is not responding. Please check if the URL is correct and the server is online."
        
        # File not found errors
        if "no such file" in error_lower or "errno 2" in error_lower:
            return "File not found: The video file does not exist. Please check the file path."
        
        # Camera/device not found
        if "errno 5" in error_lower or "i/o error" in error_lower:
            return "Camera not found: No camera device detected. Please check if your camera is connected and not in use by another application."
        
        # Connection refused
        if "connection refused" in error_lower or "errno 111" in error_lower:
            return "Connection refused: The server rejected the connection. Please verify the URL and server status."
        
        # Network unreachable
        if "network unreachable" in error_lower or "errno 101" in error_lower:
            return "Network unreachable: Cannot reach the server. Please check your internet connection and the URL."
        
        # Host not found
        if "name or service not known" in error_lower or "getaddrinfo failed" in error_lower:
            return "Host not found: The server address is invalid or unreachable. Please check the URL."
        
        # Invalid format
        if "invalid data found" in error_lower or "unknown format" in error_lower:
            return "Invalid video format: The file format is not supported. Please use MP4, AVI, MKV, MOV, or FLV."
        
        # No video stream
        if "no video stream" in error_lower or "no video streams found" in error_lower:
            return "No video stream found: The source does not contain a valid video stream."
        
        # Permission denied
        if "permission denied" in error_lower or "errno 13" in error_lower:
            return "Permission denied: You don't have permission to access this file or device."
        
        # Generic source error
        if "source error" in error_lower:
            return "Source error: Unable to access the video source. Please verify the URL or file path."
        
        # Default message
        return "Connection error: Unable to connect to the video source. Please check your URL and try again."
