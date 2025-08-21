
class CollibraAPIError(Exception):
    """Base exception for Collibra API errors"""


class UnauthorizedError(CollibraAPIError):
    """Raised when authentication fails"""


class ForbiddenError(CollibraAPIError):
    """Raised when access is forbidden"""


class NotFoundError(CollibraAPIError):
    """Raised when resource is not found"""


class ServerError(CollibraAPIError):
    """Raised when server returns 5xx errors"""
