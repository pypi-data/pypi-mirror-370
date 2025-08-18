"""Concrete implementations of adapter interfaces.

This module provides ready-to-use implementations of database and notification
adapters for common use cases.
"""

from .memory_db import MemoryDatabaseAdapter
from .sqlite_db import SQLiteDatabaseAdapter
from .console_notifier import ConsoleNotificationAdapter
from .webhook_notifier import WebhookNotificationAdapter
from .file_notifier import FileNotificationAdapter

__all__ = [
    "MemoryDatabaseAdapter",
    "SQLiteDatabaseAdapter",
    "ConsoleNotificationAdapter",
    "WebhookNotificationAdapter",
    "FileNotificationAdapter",
]
