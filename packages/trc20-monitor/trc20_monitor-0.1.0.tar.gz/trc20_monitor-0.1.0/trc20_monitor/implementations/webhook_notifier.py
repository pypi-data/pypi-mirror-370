"""Webhook notification adapter for TRC20 monitoring."""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

import aiohttp

from ..adapters.notification import NotificationAdapter
from ..core.exceptions import NotificationError
from ..core.models import TRC20Transaction
from ..utils.retry import with_retry


class WebhookNotificationAdapter(NotificationAdapter):
    """Webhook-based notification adapter for TRC20 monitoring.
    
    This adapter sends HTTP POST requests to configured webhook URLs. It's suitable for:
    - Integration with external systems
    - Slack, Discord, or Teams notifications
    - Custom notification services
    - Microservice architectures
    
    Supports multiple webhooks, retries, and custom headers.
    """

    def __init__(
        self,
        webhook_urls: List[str],
        timeout_seconds: int = 30,
        retry_attempts: int = 3,
        custom_headers: Optional[Dict[str, str]] = None,
        include_metadata: bool = True,
    ):
        """Initialize the webhook notification adapter.
        
        Args:
            webhook_urls: List of webhook URLs to send notifications to
            timeout_seconds: Timeout for HTTP requests
            retry_attempts: Number of retry attempts for failed requests
            custom_headers: Custom HTTP headers to include in requests
            include_metadata: Whether to include metadata in webhook payload
        """
        self.webhook_urls = webhook_urls
        self.timeout_seconds = timeout_seconds
        self.retry_attempts = retry_attempts
        self.custom_headers = custom_headers or {}
        self.include_metadata = include_metadata
        self._lock = asyncio.Lock()
        self._initialized = False
        self._closed = False

        if not webhook_urls:
            raise NotificationError("At least one webhook URL is required")

    async def initialize(self) -> None:
        """Initialize the notification adapter."""
        async with self._lock:
            if not self._initialized:
                # Validate webhook URLs
                for url in self.webhook_urls:
                    if not url.startswith(("http://", "https://")):
                        raise NotificationError(f"Invalid webhook URL: {url}")

                self._initialized = True
                self._closed = False

    async def close(self) -> None:
        """Close the notification adapter."""
        async with self._lock:
            self._closed = True

    async def send_transaction_alert(
        self,
        transaction: TRC20Transaction,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send a basic transaction alert."""
        if self._closed:
            raise NotificationError("Webhook notification adapter is closed")

        payload = {
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
            payload["metadata"] = metadata

        await self._send_webhook_payload(payload)

    async def send_large_amount_alert(
        self,
        transaction: TRC20Transaction,
        threshold: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send an alert for large amount transactions."""
        if self._closed:
            raise NotificationError("Webhook notification adapter is closed")

        payload = {
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
            payload["metadata"] = metadata

        await self._send_webhook_payload(payload)

    async def send_error_alert(
        self,
        error_message: str,
        error_type: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send an error alert."""
        if self._closed:
            raise NotificationError("Webhook notification adapter is closed")

        payload = {
            "type": "error_alert",
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "message": self.format_error_message(error_message, error_type),
        }

        if self.include_metadata and metadata:
            payload["metadata"] = metadata

        await self._send_webhook_payload(payload)

    async def send_system_alert(
        self,
        message: str,
        severity: str = "info",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Send a system-level alert."""
        if self._closed:
            raise NotificationError("Webhook notification adapter is closed")

        payload = {
            "type": "system_alert",
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "message": message,
        }

        if self.include_metadata and metadata:
            payload["metadata"] = metadata

        await self._send_webhook_payload(payload)

    @with_retry(max_attempts=3, delay_seconds=2)
    async def _send_webhook_payload(self, payload: Dict[str, Any]) -> None:
        """Send payload to all configured webhooks."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "TRC20-Monitor/1.0",
            **self.custom_headers,
        }

        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = []
            for url in self.webhook_urls:
                task = self._send_to_webhook(session, url, payload, headers)
                tasks.append(task)

            # Wait for all webhooks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check for any failures
            failures = [result for result in results if isinstance(result, Exception)]
            if failures:
                failure_count = len(failures)
                total_count = len(self.webhook_urls)
                raise NotificationError(
                    f"Failed to send to {failure_count}/{total_count} webhooks: {failures[0]}"
                )

    async def _send_to_webhook(
        self,
        session: aiohttp.ClientSession,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
    ) -> None:
        """Send payload to a single webhook URL."""
        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status >= 400:
                    response_text = await response.text()
                    raise NotificationError(
                        f"Webhook {url} returned status {response.status}: {response_text}"
                    )
        except aiohttp.ClientError as e:
            raise NotificationError(f"Failed to send webhook to {url}: {e}") from e

    async def health_check(self) -> bool:
        """Check if the notification system is healthy."""
        if self._closed:
            return False

        try:
            # Send a test payload to all webhooks
            test_payload = {
                "type": "health_check",
                "timestamp": datetime.now().isoformat(),
                "message": "TRC20 Monitor health check",
            }

            await self._send_webhook_payload(test_payload)
            return True
        except Exception:
            return False

    # Additional webhook-specific methods

    def add_webhook_url(self, url: str) -> None:
        """Add a new webhook URL."""
        if not url.startswith(("http://", "https://")):
            raise NotificationError(f"Invalid webhook URL: {url}")
        
        if url not in self.webhook_urls:
            self.webhook_urls.append(url)

    def remove_webhook_url(self, url: str) -> bool:
        """Remove a webhook URL.
        
        Returns:
            True if URL was removed, False if it wasn't found
        """
        try:
            self.webhook_urls.remove(url)
            return True
        except ValueError:
            return False

    def get_webhook_urls(self) -> List[str]:
        """Get list of configured webhook URLs."""
        return self.webhook_urls.copy()

    def set_custom_header(self, key: str, value: str) -> None:
        """Set a custom HTTP header."""
        self.custom_headers[key] = value

    def remove_custom_header(self, key: str) -> None:
        """Remove a custom HTTP header."""
        self.custom_headers.pop(key, None)

    async def test_webhooks(self) -> Dict[str, bool]:
        """Test all configured webhooks.
        
        Returns:
            Dictionary with webhook URL as key and success status as value
        """
        if self._closed:
            raise NotificationError("Webhook notification adapter is closed")

        test_payload = {
            "type": "webhook_test",
            "timestamp": datetime.now().isoformat(),
            "message": "TRC20 Monitor webhook test",
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "TRC20-Monitor/1.0",
            **self.custom_headers,
        }

        results = {}
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            for url in self.webhook_urls:
                try:
                    async with session.post(url, json=test_payload, headers=headers) as response:
                        results[url] = response.status < 400
                except Exception:
                    results[url] = False

        return results

    def __str__(self) -> str:
        """String representation of the webhook notification adapter."""
        return f"WebhookNotificationAdapter(webhooks={len(self.webhook_urls)}, closed={self._closed})"