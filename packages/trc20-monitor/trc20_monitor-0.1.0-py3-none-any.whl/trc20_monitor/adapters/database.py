"""Database adapter interface for TRC20 monitoring."""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..core.models import TRC20Transaction


class DatabaseAdapter(ABC):
    """Abstract base class for database adapters.
    
    This interface defines the methods that all database adapters must implement
    for storing and retrieving TRC20 transaction data.
    """

    @abstractmethod
    async def is_transaction_processed(self, tx_id: str) -> bool:
        """Check if a transaction has already been processed.

        Args:
            tx_id: Transaction ID to check

        Returns:
            True if transaction exists in the database
            
        Raises:
            DatabaseError: If database operation fails
        """
        pass

    @abstractmethod
    async def mark_transaction_processed(self, transaction: TRC20Transaction) -> None:
        """Mark a transaction as processed.

        Args:
            transaction: Transaction to mark as processed
            
        Raises:
            DatabaseError: If database operation fails
        """
        pass

    @abstractmethod
    async def get_processed_transaction(self, tx_id: str) -> Optional[TRC20Transaction]:
        """Get a processed transaction by ID.

        Args:
            tx_id: Transaction ID to retrieve

        Returns:
            Transaction if found, None otherwise
            
        Raises:
            DatabaseError: If database operation fails
        """
        pass

    @abstractmethod
    async def get_recent_transactions(
        self,
        to_address: Optional[str] = None,
        contract_address: Optional[str] = None,
        limit: int = 50,
    ) -> List[TRC20Transaction]:
        """Get recent processed transactions.

        Args:
            to_address: Filter by destination address (optional)
            contract_address: Filter by contract address (optional)
            limit: Maximum number of records to return

        Returns:
            List of transactions sorted by processing time (newest first)
            
        Raises:
            DatabaseError: If database operation fails
        """
        pass

    @abstractmethod
    async def cleanup_old_records(self, days_old: int) -> int:
        """Clean up old processed transaction records.

        Args:
            days_old: Delete records older than this many days

        Returns:
            Number of records deleted
            
        Raises:
            DatabaseError: If database operation fails
        """
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the database (create tables, etc.).
        
        This method is called once when the adapter is first used.
        It should be idempotent (safe to call multiple times).
        
        Raises:
            DatabaseError: If initialization fails
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close database connections and clean up resources.
        
        This method is called when the adapter is no longer needed.
        It should be safe to call multiple times.
        
        Raises:
            DatabaseError: If cleanup fails
        """
        pass

    async def health_check(self) -> bool:
        """Check if the database is healthy and accessible.

        Returns:
            True if database is healthy, False otherwise
        """
        try:
            # Default implementation tries to get recent transactions
            await self.get_recent_transactions(limit=1)
            return True
        except Exception:
            return False

    async def get_transaction_count(
        self,
        to_address: Optional[str] = None,
        contract_address: Optional[str] = None,
    ) -> int:
        """Get count of processed transactions.

        Args:
            to_address: Filter by destination address (optional)
            contract_address: Filter by contract address (optional)

        Returns:
            Number of transactions matching the filters
            
        Raises:
            DatabaseError: If database operation fails
        """
        # Default implementation gets all and counts (subclasses can optimize)
        transactions = await self.get_recent_transactions(
            to_address=to_address,
            contract_address=contract_address,
            limit=999999,  # Large limit to get all
        )
        return len(transactions)