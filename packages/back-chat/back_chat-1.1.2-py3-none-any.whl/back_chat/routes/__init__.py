"""
This package contains all route definitions (endpoints) for the application,
typically grouped by functionality or resource.
"""

from .v1_routes import v1_router
from .api_routes import api_router
from .streaming_routes import ws_router

__all__ = [
    v1_router.__str__(),
    api_router.__str__(),
    ws_router.__str__(),
]
