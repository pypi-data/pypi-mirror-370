"""Command-line interface for TRC20 Monitor."""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from .core.models import MonitorConfig
from .implementations.console_notifier import ConsoleNotificationAdapter
from .implementations.file_notifier import FileNotificationAdapter
from .implementations.memory_db import MemoryDatabaseAdapter
from .implementations.sqlite_db import SQLiteDatabaseAdapter
from .worker.worker import TRC20Worker


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Setup logging configuration."""
    log_level = getattr(logging, level.upper())
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        force=True
    )


def create_database_adapter(db_type: str, db_path: Optional[str] = None):
    """Create database adapter based on type."""
    if db_type == "memory":
        return MemoryDatabaseAdapter()
    elif db_type == "sqlite":
        path = db_path or "trc20_monitor.db"
        return SQLiteDatabaseAdapter(path)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


def create_notification_adapter(
    notif_type: str,
    webhook_urls: Optional[list] = None,
    log_file: Optional[str] = None
):
    """Create notification adapter based on type."""
    if notif_type == "console":
        return ConsoleNotificationAdapter()
    elif notif_type == "file":
        path = log_file or "trc20_notifications.log"
        return FileNotificationAdapter(path)
    else:
        raise ValueError(f"Unsupported notification type: {notif_type}")


async def run_monitor_once(args) -> None:
    """Run monitoring check once."""
    print("Running TRC20 monitor once...")
    
    # Create configuration
    if args.config_file:
        config = load_config_from_file(args.config_file)
    else:
        config = MonitorConfig.from_env()
    
    # Create adapters
    db_adapter = create_database_adapter(args.db_type, args.db_path)
    notification_adapter = create_notification_adapter(
        args.notification_type,
        webhook_urls=args.webhook_urls,
        log_file=args.notification_log_file
    )
    
    # Create and run worker
    worker = TRC20Worker(
        config=config,
        database_adapter=db_adapter,
        notification_adapter=notification_adapter,
        enable_graceful_shutdown=False
    )
    
    try:
        result = await worker.run_once()
        if result["success"]:
            print(f"✅ Monitoring check completed successfully in {result['duration_seconds']:.2f}s")
        else:
            print(f"❌ Monitoring check failed: {result['error']}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error running monitor: {e}")
        sys.exit(1)


async def run_monitor_continuous(args) -> None:
    """Run monitoring continuously."""
    print("Starting TRC20 monitor in continuous mode...")
    
    # Create configuration
    if args.config_file:
        config = load_config_from_file(args.config_file)
    else:
        config = MonitorConfig.from_env()
    
    # Create adapters
    db_adapter = create_database_adapter(args.db_type, args.db_path)
    notification_adapter = create_notification_adapter(
        args.notification_type,
        webhook_urls=args.webhook_urls,
        log_file=args.notification_log_file
    )
    
    # Create and start worker
    worker = TRC20Worker(
        config=config,
        database_adapter=db_adapter,
        notification_adapter=notification_adapter,
    )
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        print("\n⏹ Shutting down...")
        await worker.stop()
    except Exception as e:
        print(f"❌ Error running monitor: {e}")
        sys.exit(1)


def load_config_from_file(config_file: str) -> MonitorConfig:
    """Load configuration from JSON file."""
    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    return MonitorConfig.from_dict(config_data)


def init_config() -> None:
    """Initialize configuration file (config.json)."""
    template = {
        "monitor_addresses": [
            "TYourTronAddress1Here",
            "TYourTronAddress2Here"
        ],
        "tron_full_node": "https://api.trongrid.io",
        "tron_api_key": "your_api_key_here",
        "usdt_contract_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
        "max_transaction_age_hours": 24,
        "check_interval_seconds": 60,
        "large_transaction_threshold": 1000.0,
        "api_timeout_seconds": 30,
        "api_retries": 3,
        "retry_delay_seconds": 5,
        "cleanup_old_records_days": 30
    }
    
    output_file = "config.json"
    
    # Check if config.json already exists
    if Path(output_file).exists():
        print(f"❌ Configuration file '{output_file}' already exists")
        print("💡 Remove the existing file first if you want to regenerate it")
        return
    
    with open(output_file, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"✅ Configuration file initialized: {output_file}")
    print("📝 Edit the file with your actual addresses and settings")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TRC20 Monitor - Professional Tron USDT Transaction Monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run once with console notifications
  trc20-monitor run-once --notification-type console
  
  # Run continuously with file logging
  trc20-monitor run --db-type sqlite --notification-type file
  
  # Initialize configuration file
  trc20-monitor init
  
  # Run with custom configuration
  trc20-monitor run --config-file config.json

Environment Variables:
  MONITOR_ADDRESSES        - Comma-separated list of Tron addresses to monitor
  TRON_FULL_NODE          - Tron full node URL (default: https://api.trongrid.io)
  TRON_API_KEY            - TronGrid API key (optional)
  USDT_CONTRACT_ADDRESS   - USDT contract address
  MAX_TRANSACTION_AGE_HOURS - Maximum age of transactions to process (default: 24)
  CHECK_INTERVAL_SECONDS  - Interval between checks in seconds (default: 60)
  LARGE_TRANSACTION_THRESHOLD - Threshold for large transaction alerts (default: 1000.0)
        """
    )
    
    # Global options
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="Logging level")
    parser.add_argument("--log-file", help="Log file path")
    parser.add_argument("--config-file", help="JSON configuration file")
    
    # Database options
    parser.add_argument("--db-type", choices=["memory", "sqlite"], default="sqlite",
                       help="Database type")
    parser.add_argument("--db-path", help="Database file path (for SQLite)")
    
    # Notification options
    parser.add_argument("--notification-type", choices=["console", "file"], 
                       default="console", help="Notification type")
    parser.add_argument("--notification-log-file", help="Notification log file path")
    parser.add_argument("--webhook-urls", nargs="*", help="Webhook URLs for notifications")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run once command
    run_once_parser = subparsers.add_parser("run-once", help="Run monitoring check once")
    
    # Run continuous command
    run_parser = subparsers.add_parser("run", help="Run monitoring continuously")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize configuration file (config.json)")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    
    # Handle commands
    if args.command == "version":
        from . import __version__
        print(f"TRC20 Monitor version {__version__}")
        
    elif args.command == "init":
        init_config()
        
    elif args.command == "run-once":
        asyncio.run(run_monitor_once(args))
        
    elif args.command == "run":
        asyncio.run(run_monitor_continuous(args))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()