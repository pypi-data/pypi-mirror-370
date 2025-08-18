"""Notification adapter interface for TRC20 monitoring."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from ..core.models import TRC20Transaction


class NotificationAdapter(ABC):
    """Abstract base class for notification adapters.
    
    This interface defines the methods that all notification adapters must implement
    for sending alerts about TRC20 transactions.
    """

    @abstractmethod
    async def send_transaction_alert(
        self,
        transaction: TRC20Transaction,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send a basic transaction alert.

        Args:
            transaction: The transaction to alert about
            metadata: Additional metadata to include (optional)
            
        Raises:
            NotificationError: If notification sending fails
        """
        pass

    @abstractmethod
    async def send_large_amount_alert(
        self,
        transaction: TRC20Transaction,
        threshold: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send an alert for large amount transactions.

        Args:
            transaction: The large amount transaction
            threshold: The threshold that was exceeded
            metadata: Additional metadata to include (optional)
            
        Raises:
            NotificationError: If notification sending fails
        """
        pass

    @abstractmethod
    async def send_error_alert(
        self,
        error_message: str,
        error_type: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send an error alert.

        Args:
            error_message: Description of the error
            error_type: Type/category of the error
            metadata: Additional error context (optional)
            
        Raises:
            NotificationError: If notification sending fails
        """
        pass

    @abstractmethod
    async def send_system_alert(
        self,
        message: str,
        severity: str = "info",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send a system-level alert.

        Args:
            message: Alert message
            severity: Alert severity level (info, warning, error, critical)
            metadata: Additional context (optional)
            
        Raises:
            NotificationError: If notification sending fails
        """
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the notification adapter.
        
        This method is called once when the adapter is first used.
        It can be used to validate configuration, establish connections, etc.
        
        Raises:
            NotificationError: If initialization fails
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close connections and clean up resources.
        
        This method is called when the adapter is no longer needed.
        It should be safe to call multiple times.
        
        Raises:
            NotificationError: If cleanup fails
        """
        pass

    async def health_check(self) -> bool:
        """Check if the notification system is healthy and accessible.

        Returns:
            True if notification system is healthy, False otherwise
        """
        try:
            # Default implementation tries to send a test system alert
            await self.send_system_alert(
                message="Health check test",
                severity="info",
                metadata={"test": True},
            )
            return True
        except Exception:
            return False

    async def send_batch_alerts(
        self,
        transactions: list[TRC20Transaction],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send alerts for multiple transactions.

        Default implementation sends individual alerts. Subclasses can optimize
        for batch sending if the notification system supports it.

        Args:
            transactions: List of transactions to send alerts for
            metadata: Additional metadata for all transactions
            
        Raises:
            NotificationError: If any notification sending fails
        """
        for transaction in transactions:
            await self.send_transaction_alert(transaction, metadata)

    def format_transaction_message(self, transaction: TRC20Transaction) -> str:
        """Format a transaction into a human-readable message.
        
        This is a helper method that can be used by implementations.

        Args:
            transaction: Transaction to format

        Returns:
            Formatted message string
        """
        return (
            f"💰 New USDT Transaction\n"
            f"Amount: {transaction.amount_str} USDT\n"
            f"From: {transaction.from_address}\n"
            f"To: {transaction.to_address}\n"
            f"Time: {transaction.datetime.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"TX ID: {transaction.tx_id}"
        )

    def format_large_amount_message(
        self, transaction: TRC20Transaction, threshold: float
    ) -> str:
        """Format a large amount transaction into a message.

        Args:
            transaction: Large amount transaction
            threshold: The threshold that was exceeded

        Returns:
            Formatted message string
        """
        return (
            f"🚨 Large USDT Transaction Alert\n"
            f"Amount: {transaction.amount_str} USDT (threshold: {threshold})\n"
            f"From: {transaction.from_address}\n"
            f"To: {transaction.to_address}\n"
            f"Time: {transaction.datetime.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"TX ID: {transaction.tx_id}"
        )

    def format_error_message(self, error_message: str, error_type: str) -> str:
        """Format an error into a message.

        Args:
            error_message: Error description
            error_type: Error type

        Returns:
            Formatted message string
        """
        return f"❌ TRC20 Monitor Error ({error_type})\n{error_message}"