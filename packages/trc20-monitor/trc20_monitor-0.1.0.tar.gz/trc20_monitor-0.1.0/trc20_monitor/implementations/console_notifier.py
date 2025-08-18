"""Console notification adapter for TRC20 monitoring."""

import asyncio
import sys
from datetime import datetime
from typing import Dict, Any, Optional, TextIO

from ..adapters.notification import NotificationAdapter
from ..core.exceptions import NotificationError
from ..core.models import TRC20Transaction


class ConsoleNotificationAdapter(NotificationAdapter):
    """Console-based notification adapter for TRC20 monitoring.
    
    This adapter prints notifications to stdout/stderr. It's suitable for:
    - Development and testing
    - Command-line applications
    - Logging and debugging
    
    All notifications are printed with timestamps and formatted for readability.
    """

    def __init__(
        self,
        use_colors: bool = True,
        output_stream: Optional[TextIO] = None,
        error_stream: Optional[TextIO] = None,
        include_metadata: bool = True,
    ):
        """Initialize the console notification adapter.
        
        Args:
            use_colors: Whether to use ANSI color codes
            output_stream: Stream for normal notifications (default: stdout)
            error_stream: Stream for error notifications (default: stderr)
            include_metadata: Whether to include metadata in output
        """
        self.use_colors = use_colors
        self.output_stream = output_stream or sys.stdout
        self.error_stream = error_stream or sys.stderr
        self.include_metadata = include_metadata
        self._lock = asyncio.Lock()
        self._initialized = False
        self._closed = False

        # ANSI color codes
        self._colors = {
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "bold": "\033[1m",
            "reset": "\033[0m",
        } if use_colors else {key: "" for key in ["green", "yellow", "red", "blue", "magenta", "cyan", "white", "bold", "reset"]}

    async def initialize(self) -> None:
        """Initialize the notification adapter."""
        async with self._lock:
            if not self._initialized:
                self._initialized = True
                self._closed = False
        
        # Print initialization message after releasing the lock
        if self._initialized:
            await self._print_info("Console notification adapter initialized")

    async def close(self) -> None:
        """Close the notification adapter."""
        was_open = False
        async with self._lock:
            if not self._closed:
                was_open = True
                self._closed = True
        
        # Print closing message after releasing the lock
        if was_open:
            await self._print_info("Console notification adapter closing")

    async def send_transaction_alert(
        self,
        transaction: TRC20Transaction,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send a basic transaction alert."""
        if self._closed:
            raise NotificationError("Console notification adapter is closed")

        message = self._format_transaction_alert(transaction)
        await self._print_success(message)

        if self.include_metadata and metadata:
            await self._print_metadata(metadata)

    async def send_large_amount_alert(
        self,
        transaction: TRC20Transaction,
        threshold: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send an alert for large amount transactions."""
        if self._closed:
            raise NotificationError("Console notification adapter is closed")

        message = self._format_large_amount_alert(transaction, threshold)
        await self._print_warning(message)

        if self.include_metadata and metadata:
            await self._print_metadata(metadata)

    async def send_error_alert(
        self,
        error_message: str,
        error_type: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send an error alert."""
        if self._closed:
            raise NotificationError("Console notification adapter is closed")

        message = f"ERROR ({error_type}): {error_message}"
        await self._print_error(message)

        if self.include_metadata and metadata:
            await self._print_metadata(metadata)

    async def send_system_alert(
        self,
        message: str,
        severity: str = "info",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send a system-level alert."""
        if self._closed:
            raise NotificationError("Console notification adapter is closed")

        formatted_message = f"SYSTEM ({severity.upper()}): {message}"

        if severity == "error" or severity == "critical":
            await self._print_error(formatted_message)
        elif severity == "warning":
            await self._print_warning(formatted_message)
        else:
            await self._print_info(formatted_message)

        if self.include_metadata and metadata:
            await self._print_metadata(metadata)

    async def health_check(self) -> bool:
        """Check if the notification system is healthy."""
        if self._closed:
            return False

        try:
            # Test by printing a health check message
            test_message = f"Health check at {datetime.now().isoformat()}"
            async with self._lock:
                self.output_stream.write(f"[HEALTH] {test_message}\n")
                self.output_stream.flush()
            return True
        except Exception:
            return False

    # Helper methods for formatting and printing

    def _format_transaction_alert(self, transaction: TRC20Transaction) -> str:
        """Format a transaction alert message."""
        return (
            f"💰 New USDT Transaction\n"
            f"   Amount: {transaction.amount_str} USDT\n"
            f"   From: {transaction.from_address}\n"
            f"   To: {transaction.to_address}\n"
            f"   Time: {transaction.datetime.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"   TX ID: {transaction.tx_id}"
        )

    def _format_large_amount_alert(self, transaction: TRC20Transaction, threshold: float) -> str:
        """Format a large amount transaction alert."""
        return (
            f"🚨 Large USDT Transaction Alert!\n"
            f"   Amount: {transaction.amount_str} USDT (threshold: {threshold})\n"
            f"   From: {transaction.from_address}\n"
            f"   To: {transaction.to_address}\n"
            f"   Time: {transaction.datetime.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"   TX ID: {transaction.tx_id}"
        )

    async def _print_success(self, message: str) -> None:
        """Print a success message."""
        await self._print_with_color(message, "green", "[SUCCESS]")

    async def _print_warning(self, message: str) -> None:
        """Print a warning message."""
        await self._print_with_color(message, "yellow", "[WARNING]")

    async def _print_error(self, message: str) -> None:
        """Print an error message to error stream."""
        await self._print_with_color(message, "red", "[ERROR]", use_error_stream=True)

    async def _print_info(self, message: str) -> None:
        """Print an info message."""
        await self._print_with_color(message, "blue", "[INFO]")

    async def _print_metadata(self, metadata: Dict[str, Any]) -> None:
        """Print metadata information."""
        if not metadata:
            return

        metadata_str = "   Metadata:\n"
        for key, value in metadata.items():
            metadata_str += f"     {key}: {value}\n"
        
        await self._print_with_color(metadata_str.rstrip(), "cyan", "[METADATA]")

    async def _print_with_color(
        self,
        message: str,
        color: str,
        prefix: str,
        use_error_stream: bool = False,
    ) -> None:
        """Print a message with color and timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color_code = self._colors.get(color, "")
        reset_code = self._colors.get("reset", "")
        bold_code = self._colors.get("bold", "")
        
        formatted_message = (
            f"{bold_code}{color_code}{timestamp} {prefix}{reset_code}\n"
            f"{message}\n"
        )

        stream = self.error_stream if use_error_stream else self.output_stream

        async with self._lock:
            stream.write(formatted_message)
            stream.flush()

    # Additional console-specific methods

    async def print_separator(self, char: str = "=", length: int = 60) -> None:
        """Print a separator line."""
        if self._closed:
            return

        separator = char * length
        async with self._lock:
            self.output_stream.write(f"\n{separator}\n")
            self.output_stream.flush()

    async def print_banner(self, text: str) -> None:
        """Print a banner with the given text."""
        if self._closed:
            return

        banner_char = "="
        banner_width = max(60, len(text) + 10)
        padding = (banner_width - len(text) - 2) // 2
        
        banner = (
            f"\n{banner_char * banner_width}\n"
            f"{' ' * padding}{text}{' ' * padding}\n"
            f"{banner_char * banner_width}\n"
        )

        color_code = self._colors.get("bold", "")
        reset_code = self._colors.get("reset", "")

        async with self._lock:
            self.output_stream.write(f"{color_code}{banner}{reset_code}")
            self.output_stream.flush()

    def set_colors_enabled(self, enabled: bool) -> None:
        """Enable or disable color output."""
        self.use_colors = enabled
        if enabled:
            self._colors = {
                "green": "\033[92m",
                "yellow": "\033[93m", 
                "red": "\033[91m",
                "blue": "\033[94m",
                "magenta": "\033[95m",
                "cyan": "\033[96m",
                "white": "\033[97m",
                "bold": "\033[1m",
                "reset": "\033[0m",
            }
        else:
            self._colors = {key: "" for key in self._colors.keys()}

    def __str__(self) -> str:
        """String representation of the console notification adapter."""
        return f"ConsoleNotificationAdapter(colors={self.use_colors}, closed={self._closed})"