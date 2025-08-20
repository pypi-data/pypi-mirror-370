"""Custom exceptions for RoWifi API"""

class RoWifiError(Exception):
    """Base exception for RoWifi API errors"""
    def __init__(self, message="RoWifi API error occurred", status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response
    
    def __str__(self):
        if self.status_code:
            return f"Error {self.status_code}: {super().__str__()}"
        return super().__str__()

class AuthenticationError(RoWifiError):
    """Raised when authentication fails"""
    def __init__(self, message="Authentication failed", status_code=401, response=None):
        super().__init__(message, status_code, response)
    
    def __str__(self):
        base_msg = f"Error {self.status_code}: {Exception.__str__(self)}"
        return f"{base_msg} - Please check your credentials."

class RateLimitError(RoWifiError):
    """Raised when rate limit is exceeded"""
    def __init__(self, message="Rate limit exceeded", retry_after=None, status_code=429, response=None):
        super().__init__(message, status_code, response)
        self.retry_after = retry_after
    
    def __str__(self):
        base_msg = f"Error {self.status_code}: {Exception.__str__(self)}"
        if self.retry_after:
            return f"{base_msg} - Retry after {self.retry_after} seconds"
        return base_msg

class NotFoundError(RoWifiError):
    """Raised when a resource is not found"""
    def __init__(self, message="Resource not found", status_code=404, response=None):
        super().__init__(message, status_code, response)

class ValidationError(RoWifiError):
    """Raised when request validation fails"""
    def __init__(self, message="Request validation failed", status_code=400, response=None):
        super().__init__(message, status_code, response)

class ServerError(RoWifiError):
    """Raised when server returns 5xx error"""
    def __init__(self, message="Server error occurred", status_code=500, response=None):
        super().__init__(message, status_code, response)
    
    @property
    def is_retriable(self):
        """Some server errors are worth retrying"""
        retriable_codes = {500, 502, 503, 504}
        return self.status_code in retriable_codes if self.status_code else True