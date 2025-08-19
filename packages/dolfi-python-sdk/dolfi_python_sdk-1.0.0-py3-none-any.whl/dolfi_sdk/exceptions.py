"""
Custom exceptions for Dolfi SDK.
"""


class DolfiError(Exception):
    """Base exception class for all Dolfi SDK errors."""
    
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DolfiAuthenticationError(DolfiError):
    """Raised when API authentication fails (401 Unauthorized)."""
    
    def __init__(self, message: str = "Authentication failed. Please check your API key."):
        super().__init__(message, status_code=401)


class DolfiValidationError(DolfiError):
    """Raised when request validation fails (422 Validation Error)."""
    
    def __init__(self, message: str, validation_details: dict = None):
        super().__init__(message, status_code=422)
        self.validation_details = validation_details or {}


class DolfiAPIError(DolfiError):
    """Raised when API returns an unexpected error."""
    
    def __init__(self, message: str, status_code: int, response_data: dict = None):
        super().__init__(message, status_code)
        self.response_data = response_data or {}


class DolfiConnectionError(DolfiError):
    """Raised when there's a connection error to the API."""
    
    def __init__(self, message: str = "Failed to connect to Dolfi API"):
        super().__init__(message)


class DolfiTimeoutError(DolfiError):
    """Raised when API request times out."""
    
    def __init__(self, message: str = "Request to Dolfi API timed out"):
        super().__init__(message)