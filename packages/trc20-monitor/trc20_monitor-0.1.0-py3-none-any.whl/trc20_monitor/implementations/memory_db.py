"""Memory-based database adapter for TRC20 monitoring."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from ..adapters.database import DatabaseAdapter
from ..core.exceptions import DatabaseError
from ..core.models import TRC20Transaction


class MemoryDatabaseAdapter(DatabaseAdapter):
    """In-memory database adapter for TRC20 monitoring.
    
    This adapter stores all transaction data in memory. It's suitable for:
    - Testing and development
    - Temporary monitoring sessions
    - Low-volume applications where persistence isn't required
    
    Note: All data is lost when the process terminates.
    """

    def __init__(self):
        """Initialize the memory database adapter."""
        self._processed_transactions: Dict[str, TRC20Transaction] = {}
        self._lock = asyncio.Lock()
        self._initialized = False
        self._closed = False

    async def initialize(self) -> None:
        """Initialize the database adapter."""
        async with self._lock:
            if not self._initialized:
                self._processed_transactions.clear()
                self._initialized = True
                self._closed = False

    async def close(self) -> None:
        """Close the database adapter and clean up resources."""
        async with self._lock:
            self._closed = True
            # Keep data for potential debugging, just mark as closed

    async def is_transaction_processed(self, tx_id: str) -> bool:
        """Check if a transaction has already been processed."""
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        async with self._lock:
            return tx_id in self._processed_transactions

    async def mark_transaction_processed(self, transaction: TRC20Transaction) -> None:
        """Mark a transaction as processed."""
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        async with self._lock:
            # Create a copy of the transaction with current timestamp as processed_at
            processed_transaction = TRC20Transaction(
                tx_id=transaction.tx_id,
                from_address=transaction.from_address,
                to_address=transaction.to_address,
                amount=transaction.amount,
                timestamp=transaction.timestamp,
                block_height=transaction.block_height,
                contract_address=transaction.contract_address,
            )
            
            self._processed_transactions[transaction.tx_id] = processed_transaction

    async def get_processed_transaction(self, tx_id: str) -> Optional[TRC20Transaction]:
        """Get a processed transaction by ID."""
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        async with self._lock:
            return self._processed_transactions.get(tx_id)

    async def get_recent_transactions(
        self,
        to_address: Optional[str] = None,
        contract_address: Optional[str] = None,
        limit: int = 50,
    ) -> List[TRC20Transaction]:
        """Get recent processed transactions."""
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        async with self._lock:
            transactions = list(self._processed_transactions.values())

            # Apply filters
            if to_address:
                transactions = [tx for tx in transactions if tx.to_address == to_address]

            if contract_address:
                transactions = [tx for tx in transactions if tx.contract_address == contract_address]

            # Sort by timestamp (newest first)
            transactions.sort(key=lambda tx: tx.timestamp, reverse=True)

            # Apply limit
            return transactions[:limit]

    async def cleanup_old_records(self, days_old: int) -> int:
        """Clean up old processed transaction records."""
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        cutoff_timestamp = int((datetime.now() - timedelta(days=days_old)).timestamp() * 1000)
        
        async with self._lock:
            old_tx_ids = [
                tx_id for tx_id, tx in self._processed_transactions.items()
                if tx.timestamp < cutoff_timestamp
            ]

            for tx_id in old_tx_ids:
                del self._processed_transactions[tx_id]

            return len(old_tx_ids)

    async def health_check(self) -> bool:
        """Check if the database is healthy and accessible."""
        if self._closed:
            return False
            
        try:
            # Simple check: try to access the data structure
            async with self._lock:
                len(self._processed_transactions)
            return True
        except Exception:
            return False

    async def get_transaction_count(
        self,
        to_address: Optional[str] = None,
        contract_address: Optional[str] = None,
    ) -> int:
        """Get count of processed transactions."""
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        async with self._lock:
            transactions = list(self._processed_transactions.values())

            # Apply filters
            if to_address:
                transactions = [tx for tx in transactions if tx.to_address == to_address]

            if contract_address:
                transactions = [tx for tx in transactions if tx.contract_address == contract_address]

            return len(transactions)

    # Additional methods specific to memory adapter

    async def clear_all_data(self) -> int:
        """Clear all stored transaction data.
        
        Returns:
            Number of records cleared
        """
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        async with self._lock:
            count = len(self._processed_transactions)
            self._processed_transactions.clear()
            return count

    async def get_all_tx_ids(self) -> Set[str]:
        """Get all processed transaction IDs.
        
        Returns:
            Set of all transaction IDs
        """
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        async with self._lock:
            return set(self._processed_transactions.keys())

    async def get_addresses_summary(self) -> Dict[str, Dict[str, int]]:
        """Get a summary of transactions by address.
        
        Returns:
            Dictionary with address as key and stats as value
        """
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        summary = {}
        async with self._lock:
            for tx in self._processed_transactions.values():
                # From address stats
                if tx.from_address not in summary:
                    summary[tx.from_address] = {"sent_count": 0, "received_count": 0}
                summary[tx.from_address]["sent_count"] += 1

                # To address stats  
                if tx.to_address not in summary:
                    summary[tx.to_address] = {"sent_count": 0, "received_count": 0}
                summary[tx.to_address]["received_count"] += 1

        return summary

    def __len__(self) -> int:
        """Get the number of stored transactions (synchronous)."""
        return len(self._processed_transactions)

    def __contains__(self, tx_id: str) -> bool:
        """Check if transaction ID exists (synchronous)."""
        return tx_id in self._processed_transactions

    def __str__(self) -> str:
        """String representation of the memory database."""
        return f"MemoryDatabaseAdapter(transactions={len(self._processed_transactions)}, closed={self._closed})"