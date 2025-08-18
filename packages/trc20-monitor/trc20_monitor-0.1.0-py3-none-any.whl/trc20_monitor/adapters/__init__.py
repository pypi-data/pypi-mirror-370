"""Abstract adapter interfaces for TRC20 monitoring.

This module defines the abstract base classes that all adapters must implement.
This allows for pluggable backends for database storage and notifications.
"""

from .database import DatabaseAdapter
from .notification import NotificationAdapter

__all__ = [
    "DatabaseAdapter",
    "NotificationAdapter",
]
