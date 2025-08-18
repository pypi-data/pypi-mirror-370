"""TRC20 Monitor - Professional Tron USDT Transaction Monitoring.

A robust, production-ready Python package for monitoring TRC20 token transactions
(primarily USDT) on the Tron blockchain with pluggable adapters for different
database and notification systems.
"""

__version__ = "0.1.0"
__author__ = "TRC20 Monitor Team"
__email__ = "support@trc20monitor.com"
__license__ = "MIT"

# Main API exports
from .core.monitor import TRC20Monitor
from .core.models import TRC20Transaction, MonitorConfig
from .core.exceptions import (
    TRC20MonitorError,
    APIError,
    ValidationError,
    ConfigurationError,
)

# Adapter interfaces
from .adapters.database import DatabaseAdapter
from .adapters.notification import NotificationAdapter

# Common implementations
from .implementations.memory_db import MemoryDatabaseAdapter
from .implementations.console_notifier import ConsoleNotificationAdapter

# Utilities
from .utils.tron import TronAddressConverter
from .utils.validation import validate_address, validate_amount

__all__ = [
    # Core classes
    "TRC20Monitor",
    "TRC20Transaction",
    "MonitorConfig",
    # Exceptions
    "TRC20MonitorError",
    "APIError",
    "ValidationError",
    "ConfigurationError",
    # Adapter interfaces
    "DatabaseAdapter",
    "NotificationAdapter",
    # Default implementations
    "MemoryDatabaseAdapter",
    "ConsoleNotificationAdapter",
    # Utilities
    "TronAddressConverter",
    "validate_address",
    "validate_amount",
]
