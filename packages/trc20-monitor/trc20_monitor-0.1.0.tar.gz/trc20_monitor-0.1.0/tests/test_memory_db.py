"""Tests for memory database adapter."""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta

from trc20_monitor.implementations.memory_db import MemoryDatabaseAdapter
from trc20_monitor.core.models import TRC20Transaction
from trc20_monitor.core.exceptions import DatabaseError


class TestMemoryDatabaseAdapter:
    """Test MemoryDatabaseAdapter."""

    @pytest_asyncio.fixture
    async def db_adapter(self):
        """Create and initialize a memory database adapter."""
        adapter = MemoryDatabaseAdapter()
        await adapter.initialize()
        return adapter

    @pytest.fixture
    def sample_transaction(self):
        """Create a sample transaction."""
        return TRC20Transaction(
            tx_id="a" * 64,
            from_address="TFromAddress123",
            to_address="TToAddress456",
            amount=100.5,
            timestamp=int(datetime.now().timestamp() * 1000),
            block_height=12345,
            contract_address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
        )

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test database adapter initialization."""
        adapter = MemoryDatabaseAdapter()
        assert not adapter._initialized
        
        await adapter.initialize()
        assert adapter._initialized
        assert not adapter._closed

    @pytest.mark.asyncio
    async def test_close(self, db_adapter):
        """Test closing the database adapter."""
        assert not db_adapter._closed
        
        await db_adapter.close()
        assert db_adapter._closed

    @pytest.mark.asyncio
    async def test_mark_and_check_transaction(self, db_adapter, sample_transaction):
        """Test marking and checking transaction processing."""
        # Initially should not be processed
        is_processed = await db_adapter.is_transaction_processed(sample_transaction.tx_id)
        assert not is_processed

        # Mark as processed
        await db_adapter.mark_transaction_processed(sample_transaction)

        # Now should be processed
        is_processed = await db_adapter.is_transaction_processed(sample_transaction.tx_id)
        assert is_processed

    @pytest.mark.asyncio
    async def test_get_processed_transaction(self, db_adapter, sample_transaction):
        """Test retrieving a processed transaction."""
        # Initially should return None
        retrieved = await db_adapter.get_processed_transaction(sample_transaction.tx_id)
        assert retrieved is None

        # Mark as processed
        await db_adapter.mark_transaction_processed(sample_transaction)

        # Now should return the transaction
        retrieved = await db_adapter.get_processed_transaction(sample_transaction.tx_id)
        assert retrieved is not None
        assert retrieved.tx_id == sample_transaction.tx_id
        assert retrieved.amount == sample_transaction.amount

    @pytest.mark.asyncio
    async def test_get_recent_transactions(self, db_adapter):
        """Test getting recent transactions."""
        # Create multiple transactions
        transactions = []
        for i in range(5):
            tx = TRC20Transaction(
                tx_id=f"{'a' * 63}{i}",
                from_address="TFromAddress123",
                to_address=f"TToAddress{i}",
                amount=float(100 + i),
                timestamp=int(datetime.now().timestamp() * 1000) + i * 1000,
                block_height=12345 + i,
            )
            transactions.append(tx)
            await db_adapter.mark_transaction_processed(tx)

        # Get recent transactions
        recent = await db_adapter.get_recent_transactions(limit=3)
        assert len(recent) == 3
        
        # Should be sorted by timestamp (newest first)
        timestamps = [tx.timestamp for tx in recent]
        assert timestamps == sorted(timestamps, reverse=True)

    @pytest.mark.asyncio
    async def test_get_recent_transactions_with_filters(self, db_adapter):
        """Test getting recent transactions with filters."""
        # Create transactions with different addresses
        tx1 = TRC20Transaction(
            tx_id="a" * 64,
            from_address="TFromAddress123",
            to_address="TTargetAddress1",
            amount=100.0,
            timestamp=int(datetime.now().timestamp() * 1000),
            contract_address="TContract1",
        )
        
        tx2 = TRC20Transaction(
            tx_id="b" * 64,
            from_address="TFromAddress456",
            to_address="TTargetAddress2",
            amount=200.0,
            timestamp=int(datetime.now().timestamp() * 1000) + 1000,
            contract_address="TContract2",
        )

        await db_adapter.mark_transaction_processed(tx1)
        await db_adapter.mark_transaction_processed(tx2)

        # Filter by to_address
        filtered = await db_adapter.get_recent_transactions(to_address="TTargetAddress1")
        assert len(filtered) == 1
        assert filtered[0].tx_id == tx1.tx_id

        # Filter by contract_address
        filtered = await db_adapter.get_recent_transactions(contract_address="TContract2")
        assert len(filtered) == 1
        assert filtered[0].tx_id == tx2.tx_id

    @pytest.mark.asyncio
    async def test_cleanup_old_records(self, db_adapter):
        """Test cleaning up old transaction records."""
        # Create old and new transactions
        old_timestamp = int((datetime.now() - timedelta(days=35)).timestamp() * 1000)
        new_timestamp = int((datetime.now() - timedelta(days=5)).timestamp() * 1000)

        old_tx = TRC20Transaction(
            tx_id="a" * 64,
            from_address="TFromAddress123",
            to_address="TToAddress456",
            amount=100.0,
            timestamp=old_timestamp,
        )

        new_tx = TRC20Transaction(
            tx_id="b" * 64,
            from_address="TFromAddress789",
            to_address="TToAddress012",
            amount=200.0,
            timestamp=new_timestamp,
        )

        await db_adapter.mark_transaction_processed(old_tx)
        await db_adapter.mark_transaction_processed(new_tx)

        # Verify both are stored
        assert await db_adapter.is_transaction_processed(old_tx.tx_id)
        assert await db_adapter.is_transaction_processed(new_tx.tx_id)

        # Cleanup records older than 30 days
        deleted_count = await db_adapter.cleanup_old_records(days_old=30)
        assert deleted_count == 1

        # Old transaction should be gone, new one should remain
        assert not await db_adapter.is_transaction_processed(old_tx.tx_id)
        assert await db_adapter.is_transaction_processed(new_tx.tx_id)

    @pytest.mark.asyncio
    async def test_health_check(self, db_adapter):
        """Test health check functionality."""
        # Should be healthy after initialization
        is_healthy = await db_adapter.health_check()
        assert is_healthy

        # Should be unhealthy after closing
        await db_adapter.close()
        is_healthy = await db_adapter.health_check()
        assert not is_healthy

    @pytest.mark.asyncio
    async def test_get_transaction_count(self, db_adapter):
        """Test getting transaction count."""
        # Initially should be 0
        count = await db_adapter.get_transaction_count()
        assert count == 0

        # Add some transactions
        tx1 = TRC20Transaction(
            tx_id="a" * 64,
            from_address="TFromAddress123",
            to_address="TTargetAddress1",
            amount=100.0,
            timestamp=int(datetime.now().timestamp() * 1000),
            contract_address="TContract1",
        )
        
        tx2 = TRC20Transaction(
            tx_id="b" * 64,
            from_address="TFromAddress456",
            to_address="TTargetAddress1",
            amount=200.0,
            timestamp=int(datetime.now().timestamp() * 1000),
            contract_address="TContract2",
        )

        await db_adapter.mark_transaction_processed(tx1)
        await db_adapter.mark_transaction_processed(tx2)

        # Total count should be 2
        count = await db_adapter.get_transaction_count()
        assert count == 2

        # Count with filter should be 2 (both have same to_address)
        count = await db_adapter.get_transaction_count(to_address="TTargetAddress1")
        assert count == 2

        # Count with different filter should be 0
        count = await db_adapter.get_transaction_count(to_address="TTargetAddress2")
        assert count == 0

    @pytest.mark.asyncio
    async def test_operations_when_closed(self, db_adapter):
        """Test that operations fail when adapter is closed."""
        await db_adapter.close()

        sample_tx = TRC20Transaction(
            tx_id="a" * 64,
            from_address="TFromAddress123",
            to_address="TToAddress456",
            amount=100.0,
            timestamp=int(datetime.now().timestamp() * 1000),
        )

        # All operations should raise DatabaseError
        with pytest.raises(DatabaseError, match="Database adapter is closed"):
            await db_adapter.is_transaction_processed("test")

        with pytest.raises(DatabaseError, match="Database adapter is closed"):
            await db_adapter.mark_transaction_processed(sample_tx)

        with pytest.raises(DatabaseError, match="Database adapter is closed"):
            await db_adapter.get_processed_transaction("test")

        with pytest.raises(DatabaseError, match="Database adapter is closed"):
            await db_adapter.get_recent_transactions()

        with pytest.raises(DatabaseError, match="Database adapter is closed"):
            await db_adapter.cleanup_old_records(30)

    @pytest.mark.asyncio
    async def test_clear_all_data(self, db_adapter, sample_transaction):
        """Test clearing all data."""
        # Add a transaction
        await db_adapter.mark_transaction_processed(sample_transaction)
        assert await db_adapter.is_transaction_processed(sample_transaction.tx_id)

        # Clear all data
        cleared_count = await db_adapter.clear_all_data()
        assert cleared_count == 1

        # Transaction should be gone
        assert not await db_adapter.is_transaction_processed(sample_transaction.tx_id)

    @pytest.mark.asyncio
    async def test_get_addresses_summary(self, db_adapter):
        """Test getting addresses summary."""
        # Add transactions with various addresses
        tx1 = TRC20Transaction(
            tx_id="a" * 64,
            from_address="TFromAddr1",
            to_address="TToAddr1",
            amount=100.0,
            timestamp=int(datetime.now().timestamp() * 1000),
        )
        
        tx2 = TRC20Transaction(
            tx_id="b" * 64,
            from_address="TFromAddr1",  # Same from address
            to_address="TToAddr2",
            amount=200.0,
            timestamp=int(datetime.now().timestamp() * 1000),
        )

        tx3 = TRC20Transaction(
            tx_id="c" * 64,
            from_address="TFromAddr2",
            to_address="TToAddr1",  # Same to address
            amount=300.0,
            timestamp=int(datetime.now().timestamp() * 1000),
        )

        await db_adapter.mark_transaction_processed(tx1)
        await db_adapter.mark_transaction_processed(tx2)
        await db_adapter.mark_transaction_processed(tx3)

        summary = await db_adapter.get_addresses_summary()

        # TFromAddr1 should have sent 2 transactions
        assert summary["TFromAddr1"]["sent_count"] == 2
        assert summary["TFromAddr1"]["received_count"] == 0

        # TToAddr1 should have received 2 transactions
        assert summary["TToAddr1"]["sent_count"] == 0
        assert summary["TToAddr1"]["received_count"] == 2

    def test_dunder_methods(self):
        """Test dunder methods."""
        adapter = MemoryDatabaseAdapter()
        
        # Test __len__
        assert len(adapter) == 0
        
        # Test __contains__
        assert "test_tx" not in adapter
        
        # Test __str__
        str_repr = str(adapter)
        assert "MemoryDatabaseAdapter" in str_repr
        assert "transactions=0" in str_repr