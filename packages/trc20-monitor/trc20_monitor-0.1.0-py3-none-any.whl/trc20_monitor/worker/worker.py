"""Background worker for TRC20 monitoring."""

import asyncio
import logging
import signal
from datetime import datetime
from typing import Optional

from ..adapters.database import DatabaseAdapter
from ..adapters.notification import NotificationAdapter
from ..core.exceptions import TRC20MonitorError
from ..core.models import MonitorConfig
from ..core.monitor import TRC20Monitor


class TRC20Worker:
    """Background worker for continuous TRC20 monitoring.
    
    This worker runs the TRC20 monitor in a background process with:
    - Graceful shutdown handling
    - Automatic restart on failures
    - Health monitoring
    - Statistics collection
    """

    def __init__(
        self,
        config: MonitorConfig,
        database_adapter: DatabaseAdapter,
        notification_adapter: NotificationAdapter,
        logger: Optional[logging.Logger] = None,
        enable_graceful_shutdown: bool = True,
    ):
        """Initialize the TRC20 worker.
        
        Args:
            config: Monitor configuration
            database_adapter: Database adapter
            notification_adapter: Notification adapter
            logger: Logger instance
            enable_graceful_shutdown: Enable graceful shutdown on SIGTERM/SIGINT
        """
        self.config = config
        self.database_adapter = database_adapter
        self.notification_adapter = notification_adapter
        self.logger = logger or logging.getLogger(__name__)
        self.enable_graceful_shutdown = enable_graceful_shutdown

        # Initialize monitor
        self.monitor = TRC20Monitor(
            config=config,
            database_adapter=database_adapter,
            notification_adapter=notification_adapter,
            logger=logger,
        )

        # Worker state
        self._running = False
        self._stop_event = asyncio.Event()
        self._start_time = None
        self._shutdown_requested = False

        # Statistics
        self.stats = {
            "start_time": None,
            "check_cycles": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "transactions_processed": 0,
            "last_check_time": None,
            "last_error": None,
            "uptime_seconds": 0,
        }

        # Setup signal handlers for graceful shutdown
        if enable_graceful_shutdown:
            self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        try:
            # Handle SIGTERM and SIGINT for graceful shutdown
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
        except (ValueError, OSError):
            # Signal handling might not be available in some environments
            self.logger.warning("Signal handling not available")

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals."""
        signal_name = signal.Signals(signum).name
        self.logger.info(f"Received {signal_name} signal, initiating graceful shutdown")
        self._shutdown_requested = True
        self._stop_event.set()

    async def start(self) -> None:
        """Start the worker."""
        if self._running:
            raise TRC20MonitorError("Worker is already running")

        self.logger.info("Starting TRC20 worker")
        self._running = True
        self._start_time = datetime.now()
        self.stats["start_time"] = self._start_time.isoformat()

        try:
            # Initialize monitor
            await self.monitor.initialize()

            # Send startup notification
            await self.notification_adapter.send_system_alert(
                message="TRC20 Worker started successfully",
                severity="info",
                metadata={
                    "config": {
                        "monitor_addresses": self.config.monitor_addresses,
                        "check_interval": self.config.check_interval_seconds,
                        "large_transaction_threshold": self.config.large_transaction_threshold,
                    }
                },
            )

            # Start monitoring loop
            await self._monitoring_loop()

        except Exception as e:
            self.logger.error(f"Worker startup failed: {e}")
            await self.notification_adapter.send_error_alert(
                error_message=f"TRC20 Worker startup failed: {e}",
                error_type="worker_startup_failed",
            )
            raise
        finally:
            await self._cleanup()

    async def stop(self, timeout_seconds: int = 30) -> None:
        """Stop the worker gracefully.
        
        Args:
            timeout_seconds: Maximum time to wait for graceful shutdown
        """
        if not self._running:
            return

        self.logger.info("Stopping TRC20 worker")
        self._stop_event.set()

        # Wait for monitoring loop to finish
        try:
            await asyncio.wait_for(self._wait_for_stop(), timeout=timeout_seconds)
        except asyncio.TimeoutError:
            self.logger.warning("Graceful shutdown timeout, forcing stop")

        await self._cleanup()

    async def _wait_for_stop(self) -> None:
        """Wait for the worker to stop."""
        while self._running:
            await asyncio.sleep(0.1)

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        self.logger.info("Starting monitoring loop")

        while not self._stop_event.is_set():
            cycle_start_time = datetime.now()
            self.stats["check_cycles"] += 1
            self.stats["last_check_time"] = cycle_start_time.isoformat()

            try:
                # Perform transaction check
                await self.monitor.check_transactions()

                self.stats["successful_checks"] += 1
                self.logger.debug("Transaction check completed successfully")

                # Optional: Perform periodic cleanup
                if self.stats["check_cycles"] % 100 == 0:  # Every 100 cycles
                    await self._periodic_maintenance()

            except Exception as e:
                self.stats["failed_checks"] += 1
                self.stats["last_error"] = str(e)
                self.logger.error(f"Transaction check failed: {e}")

                # Send error notification (with rate limiting)
                if self.stats["failed_checks"] % 10 == 1:  # Every 10th error
                    await self.notification_adapter.send_error_alert(
                        error_message=f"Monitoring cycle failed: {e}",
                        error_type="monitoring_cycle_failed",
                        metadata={"failed_checks": self.stats["failed_checks"]},
                    )

            # Update uptime
            if self._start_time:
                self.stats["uptime_seconds"] = int((datetime.now() - self._start_time).total_seconds())

            # Wait for next cycle or stop event
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self.config.check_interval_seconds
                )
                # If we get here, stop was requested
                break
            except asyncio.TimeoutError:
                # Normal timeout, continue to next cycle
                continue

        self.logger.info("Monitoring loop stopped")

    async def _periodic_maintenance(self) -> None:
        """Perform periodic maintenance tasks."""
        try:
            # Cleanup old records
            cleanup_count = await self.monitor.cleanup_old_records()
            if cleanup_count > 0:
                self.logger.info(f"Cleaned up {cleanup_count} old transaction records")

            # Health check
            health = await self.monitor.health_check()
            if not all(status == "ok" for status in health.values() if isinstance(status, str) and "error" not in status):
                await self.notification_adapter.send_system_alert(
                    message="Health check detected issues",
                    severity="warning",
                    metadata={"health_status": health},
                )

        except Exception as e:
            self.logger.error(f"Periodic maintenance failed: {e}")

    async def _cleanup(self) -> None:
        """Cleanup resources."""
        if self._running:
            self._running = False

            try:
                # Send shutdown notification
                uptime = self.stats["uptime_seconds"]
                await self.notification_adapter.send_system_alert(
                    message=f"TRC20 Worker shutting down (uptime: {uptime}s)",
                    severity="info",
                    metadata=self.get_stats(),
                )

                # Close monitor
                await self.monitor.close()

            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")

            self.logger.info("TRC20 worker stopped")

    async def get_health_status(self) -> dict:
        """Get current health status of the worker."""
        if not self._running:
            return {"status": "stopped"}

        # Get monitor health
        monitor_health = await self.monitor.health_check()

        return {
            "status": "running",
            "uptime_seconds": self.stats["uptime_seconds"],
            "last_check": self.stats["last_check_time"],
            "successful_checks": self.stats["successful_checks"],
            "failed_checks": self.stats["failed_checks"],
            "last_error": self.stats["last_error"],
            "monitor_health": monitor_health,
        }

    def get_stats(self) -> dict:
        """Get worker statistics."""
        stats = self.stats.copy()
        stats["is_running"] = self._running
        stats["shutdown_requested"] = self._shutdown_requested
        return stats

    async def run_once(self) -> dict:
        """Run monitoring check once and return results.
        
        Returns:
            Dictionary with check results
        """
        if self._running:
            raise TRC20MonitorError("Cannot run once while worker is running")

        self.logger.info("Running single monitoring check")
        
        try:
            # Initialize monitor if needed
            await self.monitor.initialize()

            # Run single check
            start_time = datetime.now()
            await self.monitor.check_transactions()
            end_time = datetime.now()

            duration = (end_time - start_time).total_seconds()

            return {
                "success": True,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "error": None,
            }

        except Exception as e:
            self.logger.error(f"Single check failed: {e}")
            return {
                "success": False,
                "start_time": start_time.isoformat() if 'start_time' in locals() else None,
                "end_time": datetime.now().isoformat(),
                "duration_seconds": None,
                "error": str(e),
            }
        finally:
            # Clean up if we initialized
            await self.monitor.close()

    def is_running(self) -> bool:
        """Check if worker is running."""
        return self._running

    def __str__(self) -> str:
        """String representation of the worker."""
        status = "running" if self._running else "stopped"
        uptime = self.stats["uptime_seconds"]
        return f"TRC20Worker(status={status}, uptime={uptime}s, checks={self.stats['check_cycles']})"