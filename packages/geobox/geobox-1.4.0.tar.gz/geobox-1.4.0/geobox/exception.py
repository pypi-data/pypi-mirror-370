class GeoboxError(Exception):
    """Base class for all exceptions raised by the Geobox SDK."""
    pass

# Error Classes
class AuthenticationError(GeoboxError):
    """Raised when there is an authentication error."""

    def __init__(self, message="Authentication failed"):
        self.message = message
        super().__init__(self.message)

class AuthorizationError(GeoboxError):
    """Raised when there is an authorization error."""

    def __init__(self, message="Authorization failed"):
        self.message = message
        super().__init__(self.message)

class ApiRequestError(GeoboxError):
    """Raised when there is an error with the API request."""

    def __init__(self, status_code, message="API request failed"):
        self.status_code = status_code
        self.message = f"{message}: Status code {status_code}"
        super().__init__(self.message)

class NotFoundError(GeoboxError):
    """Raised when a requested resource is not found."""

    def __init__(self, message="Resource not found"):
        self.message = message
        super().__init__(self.message)

class ValidationError(GeoboxError):
    """Raised when there is a validation error."""

    def __init__(self, message="Validation error"):
        self.message = message
        super().__init__(self.message)

class ServerError(GeoboxError):
    """Raised when there is a server error."""
    
    def __init__(self, message="Server error"):
        self.message = message
        super().__init__(self.message)
