class MitakeError(Exception):
    """Base exception for Mitake SMS API errors"""
    pass


class AuthenticationError(MitakeError):
    """Raised when authentication fails"""
    pass


class APIError(MitakeError):
    """Raised when API returns an error"""
    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data