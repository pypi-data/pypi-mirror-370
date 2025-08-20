"""RoWifi Python API Client"""

__version__ = "1.0.0"
__author__ = "RoWifi Team"
__email__ = "admin@rowifi.xyz"

from .client import RoWifiClient
from .exceptions import (
    RoWifiError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError
)
from .models import (
    RoUser,
    Denylist,
    XPUser,
    DenylistKind
)

__all__ = [
    'RoWifiClient',
    'RoWifiError',
    'AuthenticationError', 
    'RateLimitError',
    'NotFoundError',
    'ValidationError',
    'ServerError',
    'RoUser',
    'Denylist',
    'XPUser',
    'DenylistKind'
]