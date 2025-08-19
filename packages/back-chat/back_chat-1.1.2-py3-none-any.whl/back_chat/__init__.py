"""
back_chat is the backend service for a real-time chat application, built with
Python and designed with redundancy and reliability in mind.

It provides WebSocket-based messaging, user session handling, and integration
with authentication systems. The architecture supports failover and horizontal
scalability to ensure consistent performance and uptime.
"""


from .configuration import __version__, API_IP, API_PORT, LOGGER, LOG_CONFIG
from .define_api import APP

__all__ = [
    APP.__module__,
    __version__, str(LOG_CONFIG.__str__),
    API_IP, API_PORT.__str__(), LOGGER.__module__
]
