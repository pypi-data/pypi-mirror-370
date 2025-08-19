"""
This package contains custom Python descriptors used to control attribute
access and behavior within models or services.
"""

from .message import MessageType, MessageMode

__all__ = [MessageType.__name__, MessageMode.__name__]
