"""
This package defines custom exception classes used to handle domain-specific
errors across the application.
"""

from .error_response import ErrorHTTPException, BadRequest

__all__ = [ErrorHTTPException.__name__, BadRequest.__name__]

__aux__ = [globals().get(n)() for n in __all__]

all_errors = {a.status_code: dict(a) for a in __aux__}
