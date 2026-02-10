"""
Error Types - Categorizes errors into specific types for better handling.
"""

from enum import Enum


class ErrorType(Enum):
    """Error categories as per specification."""
    VALIDATION_ERROR = "validation"      # Malformed URL
    CONNECTION_ERROR = "connection"      # Server offline/refused
    CODEC_ERROR = "codec"                # Unsupported codec
    NETWORK_ERROR = "network"            # Network timeout/unreachable
    UNKNOWN_ERROR = "unknown"            # Other errors


class ApplicationError(Exception):
    """Base application error with type categorization."""
    
    def __init__(self, message: str, error_type: ErrorType = ErrorType.UNKNOWN_ERROR):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)
    
    def __str__(self):
        return f"[{self.error_type.value.upper()}] {self.message}"


class ValidationError(ApplicationError):
    """Raised when URL validation fails."""
    def __init__(self, message: str):
        super().__init__(message, ErrorType.VALIDATION_ERROR)


class ConnectionError(ApplicationError):
    """Raised when connection to server fails."""
    def __init__(self, message: str):
        super().__init__(message, ErrorType.CONNECTION_ERROR)


class CodecError(ApplicationError):
    """Raised when codec is unsupported."""
    def __init__(self, message: str):
        super().__init__(message, ErrorType.CODEC_ERROR)


class NetworkError(ApplicationError):
    """Raised when network error occurs."""
    def __init__(self, message: str):
        super().__init__(message, ErrorType.NETWORK_ERROR)
