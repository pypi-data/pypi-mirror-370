"""Core TRC20 monitoring logic."""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional

import aiohttp

from ..adapters.database import DatabaseAdapter
from ..adapters.notification import NotificationAdapter
from ..utils.retry import with_retry
from ..utils.validation import validate_address
from .exceptions import APIError, ConfigurationError, ValidationError
from .models import MonitorConfig, TRC20Transaction


class TRC20Monitor:
    """Monitor TRC20 token transactions (primarily USDT) on Tron network.
    
    This is the main class that orchestrates the monitoring process using
    pluggable adapters for database storage and notifications.
    """

    def __init__(
        self,
        config: MonitorConfig,
        database_adapter: DatabaseAdapter,
        notification_adapter: NotificationAdapter,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize TRC20Monitor.

        Args:
            config: Monitoring configuration
            database_adapter: Database adapter for storing processed transactions
            notification_adapter: Notification adapter for sending alerts
            logger: Logger instance (optional)
            
        Raises:
            ConfigurationError: If configuration is invalid
            ValidationError: If addresses are invalid
        """
        self.config = config
        self.database_adapter = database_adapter
        self.notification_adapter = notification_adapter
        self.logger = logger or logging.getLogger(__name__)

        # Validate monitor addresses
        for addr in self.config.monitor_addresses:
            if not validate_address(addr):
                raise ValidationError(f"Invalid Tron address: {addr}")

        # Initialize state
        self._initialized = False
        self._closed = False

        self.logger.info(
            f"Monitoring {len(self.config.monitor_addresses)} addresses for TRC20 transactions"
        )
        self.logger.info(f"Contract: {self.config.usdt_contract_address}")
        self.logger.info(f"Max transaction age: {self.config.max_transaction_age_hours} hours")

    async def initialize(self) -> None:
        """Initialize the monitor and its adapters."""
        if self._initialized:
            return

        await self.database_adapter.initialize()
        await self.notification_adapter.initialize()

        self._initialized = True
        self.logger.info("TRC20 Monitor initialized successfully")

    async def close(self) -> None:
        """Close the monitor and its adapters."""
        if self._closed:
            return

        await self.database_adapter.close()
        await self.notification_adapter.close()

        self._closed = True
        self.logger.info("TRC20 Monitor closed")

    async def check_transactions(self) -> None:
        """Check transactions for all monitored addresses."""
        if not self._initialized:
            await self.initialize()

        for address in self.config.monitor_addresses:
            try:
                await self.check_address_transactions(address)
            except Exception as error:
                self.logger.error(f"Error checking transactions for {address}: {error}")
                await self.notification_adapter.send_error_alert(
                    error_message=f"Failed to check transactions for {address}: {error}",
                    error_type="address_check_failed",
                    metadata={"address": address},
                )

    async def check_address_transactions(self, address: str) -> None:
        """Check transactions for a specific address."""
        try:
            # Primary method: Use TronGrid Account API
            await self.check_using_account_api(address)
        except Exception as error:
            self.logger.error(f"Error fetching transactions for {address}: {error}")
            # In a production implementation, you might want to implement fallback methods
            raise

    @with_retry(max_attempts=3, delay_seconds=5)
    async def check_using_account_api(self, address: str) -> None:
        """Check transactions using TronGrid Account API."""
        self.logger.debug(f"Checking transactions for {address} using Account API")

        api_url = f"{self.config.tron_full_node}/v1/accounts/{address}/transactions/trc20"
        params = {
            "contract_address": self.config.usdt_contract_address,
            "limit": 50,
            "order_by": "block_timestamp,desc",
        }

        headers = {}
        if self.config.tron_api_key:
            headers["TRON-PRO-API-KEY"] = self.config.tron_api_key

        timeout = aiohttp.ClientTimeout(total=self.config.api_timeout_seconds)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(api_url, params=params, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise APIError(
                        f"API returned status {response.status}",
                        status_code=response.status,
                        response_text=error_text,
                    )

                data = await response.json()

                if data and "data" in data:
                    await self.process_transaction_data(data["data"], address)

    async def process_transaction_data(
        self, transactions: List[dict], monitor_address: str
    ) -> None:
        """Process transaction data from API response."""
        processed_count = 0
        
        for tx in transactions:
            try:
                # Check if already processed
                if await self.database_adapter.is_transaction_processed(tx["transaction_id"]):
                    continue

                # Process both incoming and outgoing transactions
                if tx["to"] != monitor_address and tx["from"] != monitor_address:
                    continue

                # Check transaction age
                if not self.is_transaction_within_time_range(tx["block_timestamp"]):
                    self.logger.debug(
                        f"Skipping old transaction {tx['transaction_id']} "
                        f"from {datetime.fromtimestamp(tx['block_timestamp'] / 1000)}"
                    )
                    continue

                # Create transaction object
                transaction = TRC20Transaction(
                    tx_id=tx["transaction_id"],
                    from_address=tx["from"],
                    to_address=tx["to"],
                    amount=float(tx["value"]) / 1_000_000,  # USDT has 6 decimals
                    timestamp=tx["block_timestamp"],
                    block_height=tx.get("block_number", 0),
                    contract_address=self.config.usdt_contract_address,
                )

                # Process new transaction
                await self.process_new_transaction(transaction, monitor_address)

                # Mark as processed
                await self.database_adapter.mark_transaction_processed(transaction)
                processed_count += 1

            except Exception as error:
                self.logger.error(
                    f"Error processing transaction {tx.get('transaction_id', 'unknown')}: {error}"
                )
                await self.notification_adapter.send_error_alert(
                    error_message=f"Failed to process transaction: {error}",
                    error_type="transaction_processing_failed",
                    metadata={"transaction_id": tx.get("transaction_id")},
                )

        if processed_count > 0:
            self.logger.info(f"Processed {processed_count} new transactions for {monitor_address}")

    async def process_new_transaction(self, transaction: TRC20Transaction, monitor_address: str) -> None:
        """Process a newly detected transaction."""
        # Determine transaction direction
        if transaction.to_address == monitor_address:
            direction = "incoming"
        else:
            direction = "outgoing"
        
        self.logger.info(
            f"New TRC20 {direction} transaction: {transaction.amount_str} USDT "
            f"from {transaction.from_address} to {transaction.to_address}"
        )

        # Send basic transaction notification
        await self.notification_adapter.send_transaction_alert(
            transaction,
            metadata={
                "processed_at": datetime.now().isoformat(),
                "direction": direction,
                "monitor_address": monitor_address,
            },
        )

        # Send large transaction alert if amount exceeds threshold
        if transaction.amount >= self.config.large_transaction_threshold:
            await self.notification_adapter.send_large_amount_alert(
                transaction,
                self.config.large_transaction_threshold,
                metadata={
                    "processed_at": datetime.now().isoformat(),
                    "direction": direction,
                    "monitor_address": monitor_address,
                },
            )

    def is_transaction_within_time_range(self, timestamp: int) -> bool:
        """Check if transaction is within the allowed time range."""
        now_ms = int(datetime.now().timestamp() * 1000)
        max_age_ms = self.config.max_transaction_age_hours * 60 * 60 * 1000

        return (now_ms - timestamp) <= max_age_ms

    async def start_monitoring(self, run_once: bool = False) -> None:
        """Start continuous monitoring of transactions.

        Args:
            run_once: If True, run once and return. If False, run continuously.
        """
        if not self._initialized:
            await self.initialize()

        if run_once:
            self.logger.info("Running transaction check once")
            await self.check_transactions()
            return

        self.logger.info(
            f"Starting continuous TRC20 monitoring with {self.config.check_interval_seconds}s interval"
        )

        while not self._closed:
            try:
                await self.check_transactions()
            except Exception as error:
                self.logger.error(f"Error in monitoring loop: {error}")
                await self.notification_adapter.send_error_alert(
                    error_message=f"Monitoring loop error: {error}",
                    error_type="monitoring_loop_error",
                )

            # Wait for next iteration
            if not self._closed:
                await asyncio.sleep(self.config.check_interval_seconds)

    async def health_check(self) -> dict:
        """Perform health check of the monitor and its components.
        
        Returns:
            Dictionary with health status of each component
        """
        health = {
            "monitor": "ok",
            "database": "unknown",
            "notifications": "unknown",
            "api_connectivity": "unknown",
        }

        # Check database
        try:
            if await self.database_adapter.health_check():
                health["database"] = "ok"
            else:
                health["database"] = "error"
        except Exception as e:
            health["database"] = f"error: {e}"

        # Check notifications
        try:
            if await self.notification_adapter.health_check():
                health["notifications"] = "ok"
            else:
                health["notifications"] = "error"
        except Exception as e:
            health["notifications"] = f"error: {e}"

        # Check API connectivity
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.config.tron_full_node}/wallet/getnowblock") as response:
                    if response.status == 200:
                        health["api_connectivity"] = "ok"
                    else:
                        health["api_connectivity"] = f"http_status_{response.status}"
        except Exception as e:
            health["api_connectivity"] = f"error: {e}"

        return health

    async def cleanup_old_records(self) -> int:
        """Clean up old processed transaction records.
        
        Returns:
            Number of records deleted
        """
        try:
            count = await self.database_adapter.cleanup_old_records(
                self.config.cleanup_old_records_days
            )
            self.logger.info(f"Cleaned up {count} old transaction records")
            return count
        except Exception as error:
            self.logger.error(f"Error cleaning up old records: {error}")
            await self.notification_adapter.send_error_alert(
                error_message=f"Failed to clean up old records: {error}",
                error_type="cleanup_failed",
            )
            raise