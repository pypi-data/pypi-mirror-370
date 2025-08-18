"""Background worker process for TRC20 monitoring.

This module provides a worker class that can run monitoring in the background
with configurable intervals and error handling.
"""

from .worker import TRC20Worker

__all__ = ["TRC20Worker"]
