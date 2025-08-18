"""SQLite database adapter for TRC20 monitoring."""

import aiosqlite
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from ..adapters.database import DatabaseAdapter
from ..core.exceptions import DatabaseError
from ..core.models import TRC20Transaction


class SQLiteDatabaseAdapter(DatabaseAdapter):
    """SQLite database adapter for TRC20 monitoring.
    
    This adapter uses SQLite for persistent storage. It's suitable for:
    - Development and testing with persistence
    - Single-node deployments
    - Applications with moderate transaction volumes
    
    The database will be created automatically if it doesn't exist.
    """

    def __init__(self, database_path: str = "trc20_monitor.db"):
        """Initialize the SQLite database adapter.
        
        Args:
            database_path: Path to the SQLite database file
        """
        self.database_path = database_path
        self._lock = asyncio.Lock()
        self._initialized = False
        self._closed = False

    async def initialize(self) -> None:
        """Initialize the database and create tables if needed."""
        async with self._lock:
            if self._initialized:
                return

            try:
                # Create database directory if it doesn't exist
                db_path = Path(self.database_path)
                db_path.parent.mkdir(parents=True, exist_ok=True)

                # Create tables
                async with aiosqlite.connect(self.database_path) as db:
                    await db.execute("""
                        CREATE TABLE IF NOT EXISTS processed_transactions (
                            tx_id TEXT PRIMARY KEY,
                            from_address TEXT NOT NULL,
                            to_address TEXT NOT NULL,
                            amount REAL NOT NULL,
                            timestamp INTEGER NOT NULL,
                            block_height INTEGER DEFAULT 0,
                            contract_address TEXT,
                            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)

                    # Create indexes for better query performance
                    await db.execute("""
                        CREATE INDEX IF NOT EXISTS idx_to_address 
                        ON processed_transactions(to_address)
                    """)
                    
                    await db.execute("""
                        CREATE INDEX IF NOT EXISTS idx_contract_address 
                        ON processed_transactions(contract_address)
                    """)
                    
                    await db.execute("""
                        CREATE INDEX IF NOT EXISTS idx_timestamp 
                        ON processed_transactions(timestamp)
                    """)

                    await db.commit()

                self._initialized = True
                self._closed = False

            except Exception as e:
                raise DatabaseError(f"Failed to initialize SQLite database: {e}") from e

    async def close(self) -> None:
        """Close the database adapter."""
        async with self._lock:
            self._closed = True
            # SQLite connections are closed automatically per query

    async def is_transaction_processed(self, tx_id: str) -> bool:
        """Check if a transaction has already been processed."""
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        try:
            async with aiosqlite.connect(self.database_path) as db:
                cursor = await db.execute(
                    "SELECT 1 FROM processed_transactions WHERE tx_id = ?", (tx_id,)
                )
                result = await cursor.fetchone()
                return result is not None
        except Exception as e:
            raise DatabaseError(f"Failed to check transaction {tx_id}: {e}") from e

    async def mark_transaction_processed(self, transaction: TRC20Transaction) -> None:
        """Mark a transaction as processed."""
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        try:
            async with aiosqlite.connect(self.database_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO processed_transactions 
                    (tx_id, from_address, to_address, amount, timestamp, block_height, contract_address)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    transaction.tx_id,
                    transaction.from_address,
                    transaction.to_address,
                    transaction.amount,
                    transaction.timestamp,
                    transaction.block_height,
                    transaction.contract_address,
                ))
                await db.commit()
        except Exception as e:
            raise DatabaseError(f"Failed to mark transaction {transaction.tx_id} as processed: {e}") from e

    async def get_processed_transaction(self, tx_id: str) -> Optional[TRC20Transaction]:
        """Get a processed transaction by ID."""
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        try:
            async with aiosqlite.connect(self.database_path) as db:
                cursor = await db.execute("""
                    SELECT tx_id, from_address, to_address, amount, timestamp, 
                           block_height, contract_address
                    FROM processed_transactions 
                    WHERE tx_id = ?
                """, (tx_id,))
                
                row = await cursor.fetchone()
                if row is None:
                    return None

                return TRC20Transaction(
                    tx_id=row[0],
                    from_address=row[1],
                    to_address=row[2],
                    amount=row[3],
                    timestamp=row[4],
                    block_height=row[5],
                    contract_address=row[6],
                )
        except Exception as e:
            raise DatabaseError(f"Failed to get transaction {tx_id}: {e}") from e

    async def get_recent_transactions(
        self,
        to_address: Optional[str] = None,
        contract_address: Optional[str] = None,
        limit: int = 50,
    ) -> List[TRC20Transaction]:
        """Get recent processed transactions."""
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        try:
            query = """
                SELECT tx_id, from_address, to_address, amount, timestamp, 
                       block_height, contract_address
                FROM processed_transactions
            """
            params = []
            conditions = []

            if to_address:
                conditions.append("to_address = ?")
                params.append(to_address)

            if contract_address:
                conditions.append("contract_address = ?")
                params.append(contract_address)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            async with aiosqlite.connect(self.database_path) as db:
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()

                transactions = []
                for row in rows:
                    transactions.append(TRC20Transaction(
                        tx_id=row[0],
                        from_address=row[1],
                        to_address=row[2],
                        amount=row[3],
                        timestamp=row[4],
                        block_height=row[5],
                        contract_address=row[6],
                    ))

                return transactions
        except Exception as e:
            raise DatabaseError(f"Failed to get recent transactions: {e}") from e

    async def cleanup_old_records(self, days_old: int) -> int:
        """Clean up old processed transaction records."""
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        cutoff_timestamp = int((datetime.now() - timedelta(days=days_old)).timestamp() * 1000)

        try:
            async with aiosqlite.connect(self.database_path) as db:
                cursor = await db.execute(
                    "DELETE FROM processed_transactions WHERE timestamp < ?",
                    (cutoff_timestamp,)
                )
                await db.commit()
                return cursor.rowcount
        except Exception as e:
            raise DatabaseError(f"Failed to cleanup old records: {e}") from e

    async def get_transaction_count(
        self,
        to_address: Optional[str] = None,
        contract_address: Optional[str] = None,
    ) -> int:
        """Get count of processed transactions."""
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        try:
            query = "SELECT COUNT(*) FROM processed_transactions"
            params = []
            conditions = []

            if to_address:
                conditions.append("to_address = ?")
                params.append(to_address)

            if contract_address:
                conditions.append("contract_address = ?")
                params.append(contract_address)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            async with aiosqlite.connect(self.database_path) as db:
                cursor = await db.execute(query, params)
                result = await cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            raise DatabaseError(f"Failed to get transaction count: {e}") from e

    async def health_check(self) -> bool:
        """Check if the database is healthy and accessible."""
        if self._closed:
            return False

        try:
            async with aiosqlite.connect(self.database_path) as db:
                cursor = await db.execute("SELECT 1")
                await cursor.fetchone()
                return True
        except Exception:
            return False

    # Additional SQLite-specific methods

    async def vacuum_database(self) -> None:
        """Vacuum the database to reclaim space and optimize performance."""
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        try:
            async with aiosqlite.connect(self.database_path) as db:
                await db.execute("VACUUM")
        except Exception as e:
            raise DatabaseError(f"Failed to vacuum database: {e}") from e

    async def get_database_info(self) -> dict:
        """Get information about the database."""
        if self._closed:
            raise DatabaseError("Database adapter is closed")

        try:
            info = {
                "database_path": self.database_path,
                "file_exists": Path(self.database_path).exists(),
                "file_size": 0,
                "total_transactions": 0,
            }

            if info["file_exists"]:
                info["file_size"] = Path(self.database_path).stat().st_size

            async with aiosqlite.connect(self.database_path) as db:
                cursor = await db.execute("SELECT COUNT(*) FROM processed_transactions")
                result = await cursor.fetchone()
                info["total_transactions"] = result[0] if result else 0

            return info
        except Exception as e:
            raise DatabaseError(f"Failed to get database info: {e}") from e

    def __str__(self) -> str:
        """String representation of the SQLite database adapter."""
        return f"SQLiteDatabaseAdapter(path='{self.database_path}', closed={self._closed})"