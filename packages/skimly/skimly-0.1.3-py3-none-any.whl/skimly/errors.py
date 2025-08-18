from typing import Union, Any

class SkimlyError(Exception):
    """Base Skimly error class"""
    def __init__(self, message: str, status: int = 500, code: str | None = None, data: Any = None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.data = data

class SkimlyHTTPError(SkimlyError):
    """HTTP error from Skimly API"""
    def __init__(self, status: int, status_text: str, response_text: str = ""):
        super().__init__(f"HTTP {status} {status_text}", status, data=response_text)
        self.status_text = status_text
        self.response_text = response_text

class SkimlyNetworkError(SkimlyError):
    """Network or timeout error"""
    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message, 0, data=original_error)
        self.original_error = original_error
