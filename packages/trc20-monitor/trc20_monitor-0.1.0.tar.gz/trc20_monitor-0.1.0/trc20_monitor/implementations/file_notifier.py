"""File-based notification adapter for TRC20 monitoring."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import aiofiles

from ..adapters.notification import NotificationAdapter
from ..core.exceptions import NotificationError
from ..core.models import TRC20Transaction


class FileNotificationAdapter(NotificationAdapter):
    """File-based notification adapter for TRC20 monitoring.
    
    This adapter writes notifications to log files. It supports:
    - JSON structured logging
    - Plain text logging  
    - Log rotation by size or time
    - Multiple output formats
    
    Suitable for audit trails, debugging, and integration with log analysis tools.
    """

    def __init__(
        self,
        log_file_path: str,
        log_format: str = "json",  # "json" or "text"
        max_file_size_mb: int = 100,
        backup_count: int = 5,
        include_metadata: bool = True,
    ):
        """Initialize the file notification adapter.
        
        Args:
            log_file_path: Path to the log file
            log_format: Log format ("json" or "text")
            max_file_size_mb: Maximum file size before rotation (in MB)
            backup_count: Number of backup files to keep
            include_metadata: Whether to include metadata in log entries
        """
        self.log_file_path = Path(log_file_path)
        self.log_format = log_format.lower()
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.backup_count = backup_count
        self.include_metadata = include_metadata
        self._lock = asyncio.Lock()
        self._initialized = False
        self._closed = False

        if self.log_format not in ("json", "text"):
            raise NotificationError(f"Unsupported log format: {log_format}")

    async def initialize(self) -> None:
        """Initialize the notification adapter."""
        async with self._lock:
            if not self._initialized:
                # Create directory if it doesn't exist
                self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                self._initialized = True
                self._closed = False
        
        # Write initialization message after releasing the lock
        if self._initialized:
            await self._write_log_entry({
                "type": "system_init",
                "timestamp": datetime.now().isoformat(),
                "message": "File notification adapter initialized",
                "log_file": str(self.log_file_path),
                "log_format": self.log_format,
            })

    async def close(self) -> None:
        """Close the notification adapter."""
        async with self._lock:
            if not self._closed:
                await self._write_log_entry({
                    "type": "system_close",
                    "timestamp": datetime.now().isoformat(),
                    "message": "File notification adapter closing",
                })
                self._closed = True

    async def send_transaction_alert(
        self,
        transaction: TRC20Transaction,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send a basic transaction alert."""
        if self._closed:
            raise NotificationError("File notification adapter is closed")

        log_entry = {
            "type": "transaction_alert",
            "timestamp": datetime.now().isoformat(),
            "transaction": {
                "tx_id": transaction.tx_id,
                "from_address": transaction.from_address,
                "to_address": transaction.to_address,
                "amount": transaction.amount,
                "amount_formatted": transaction.amount_str,
                "transaction_time": transaction.datetime.isoformat(),
                "block_height": transaction.block_height,
                "contract_address": transaction.contract_address,
            },
            "message": self.format_transaction_message(transaction),
        }

        if self.include_metadata and metadata:
            log_entry["metadata"] = metadata

        await self._write_log_entry(log_entry)

    async def send_large_amount_alert(
        self,
        transaction: TRC20Transaction,
        threshold: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send an alert for large amount transactions."""
        if self._closed:
            raise NotificationError("File notification adapter is closed")

        log_entry = {
            "type": "large_amount_alert",
            "timestamp": datetime.now().isoformat(),
            "threshold": threshold,
            "transaction": {
                "tx_id": transaction.tx_id,
                "from_address": transaction.from_address,
                "to_address": transaction.to_address,
                "amount": transaction.amount,
                "amount_formatted": transaction.amount_str,
                "transaction_time": transaction.datetime.isoformat(),
                "block_height": transaction.block_height,
                "contract_address": transaction.contract_address,
            },
            "message": self.format_large_amount_message(transaction, threshold),
        }

        if self.include_metadata and metadata:
            log_entry["metadata"] = metadata

        await self._write_log_entry(log_entry)

    async def send_error_alert(
        self,
        error_message: str,
        error_type: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send an error alert."""
        if self._closed:
            raise NotificationError("File notification adapter is closed")

        log_entry = {
            "type": "error_alert",
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "message": self.format_error_message(error_message, error_type),
        }

        if self.include_metadata and metadata:
            log_entry["metadata"] = metadata

        await self._write_log_entry(log_entry)

    async def send_system_alert(
        self,
        message: str,
        severity: str = "info",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send a system-level alert."""
        if self._closed:
            raise NotificationError("File notification adapter is closed")

        log_entry = {
            "type": "system_alert",
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "message": message,
        }

        if self.include_metadata and metadata:
            log_entry["metadata"] = metadata

        await self._write_log_entry(log_entry)

    async def _write_log_entry(self, log_entry: Dict[str, Any]) -> None:
        """Write a log entry to the file."""
        async with self._lock:
            # Check if rotation is needed
            await self._rotate_if_needed()

            # Format the log entry
            if self.log_format == "json":
                log_line = json.dumps(log_entry, separators=(',', ':')) + '\n'
            else:  # text format
                log_line = self._format_text_entry(log_entry) + '\n'

            try:
                async with aiofiles.open(self.log_file_path, 'a', encoding='utf-8') as f:
                    await f.write(log_line)
                    await f.flush()
            except Exception as e:
                raise NotificationError(f"Failed to write to log file: {e}") from e

    def _format_text_entry(self, log_entry: Dict[str, Any]) -> str:
        """Format log entry as plain text."""
        timestamp = log_entry.get("timestamp", "")
        entry_type = log_entry.get("type", "unknown").upper()
        message = log_entry.get("message", "")

        text_line = f"[{timestamp}] {entry_type}: {message}"

        # Add transaction details if present
        if "transaction" in log_entry:
            tx = log_entry["transaction"]
            text_line += f" | TX: {tx.get('tx_id', 'N/A')}"
            text_line += f" | Amount: {tx.get('amount_formatted', 'N/A')} USDT"
            text_line += f" | From: {tx.get('from_address', 'N/A')}"
            text_line += f" | To: {tx.get('to_address', 'N/A')}"

        # Add error details if present
        if "error_type" in log_entry:
            text_line += f" | Error Type: {log_entry['error_type']}"

        return text_line

    async def _rotate_if_needed(self) -> None:
        """Rotate log file if it exceeds size limit."""
        if not self.log_file_path.exists():
            return

        file_size = self.log_file_path.stat().st_size
        if file_size < self.max_file_size_bytes:
            return

        # Perform rotation
        for i in range(self.backup_count - 1, 0, -1):
            old_name = f"{self.log_file_path}.{i}"
            new_name = f"{self.log_file_path}.{i + 1}"
            
            old_path = Path(old_name)
            new_path = Path(new_name)
            
            if old_path.exists():
                if new_path.exists():
                    new_path.unlink()  # Remove oldest backup
                old_path.rename(new_path)

        # Move current log to .1
        backup_path = Path(f"{self.log_file_path}.1")
        if backup_path.exists():
            backup_path.unlink()
        self.log_file_path.rename(backup_path)

    async def health_check(self) -> bool:
        """Check if the file system is accessible."""
        if self._closed:
            return False

        try:
            # Test write access
            test_entry = {
                "type": "health_check",
                "timestamp": datetime.now().isoformat(),
                "message": "Health check test",
            }
            await self._write_log_entry(test_entry)
            return True
        except Exception:
            return False

    # Additional file-specific methods

    async def get_log_file_info(self) -> Dict[str, Any]:
        """Get information about the log file."""
        if not self.log_file_path.exists():
            return {
                "exists": False,
                "path": str(self.log_file_path),
            }

        stat = self.log_file_path.stat()
        return {
            "exists": True,
            "path": str(self.log_file_path),
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "format": self.log_format,
        }

    async def get_recent_entries(self, count: int = 10) -> list[str]:
        """Get the most recent log entries.
        
        Args:
            count: Number of recent entries to return
            
        Returns:
            List of log entries as strings
        """
        if not self.log_file_path.exists():
            return []

        try:
            async with aiofiles.open(self.log_file_path, 'r', encoding='utf-8') as f:
                lines = await f.readlines()
                return lines[-count:] if lines else []
        except Exception:
            return []

    async def clear_log_file(self) -> bool:
        """Clear the log file contents.
        
        Returns:
            True if successful, False otherwise
        """
        if self._closed:
            return False

        try:
            async with self._lock:
                # Truncate the file
                async with aiofiles.open(self.log_file_path, 'w', encoding='utf-8') as f:
                    pass  # Opening in write mode truncates the file

                # Write reinitialization message
                await self._write_log_entry({
                    "type": "log_cleared",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Log file cleared",
                })
            return True
        except Exception:
            return False

    def __str__(self) -> str:
        """String representation of the file notification adapter."""
        return f"FileNotificationAdapter(path='{self.log_file_path}', format='{self.log_format}', closed={self._closed})"