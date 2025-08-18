"""Basic usage example for TRC20 Monitor.

This example demonstrates the simplest way to use the TRC20 Monitor package
to monitor USDT transactions on the Tron network.
"""

import asyncio
import os
from typing import List

from trc20_monitor import (
    TRC20Monitor,
    MonitorConfig,
    MemoryDatabaseAdapter,
    ConsoleNotificationAdapter,
    ValidationError,
    ConfigurationError,
)


async def basic_monitoring_example():
    """Basic monitoring example with console output."""
    print("🚀 Starting TRC20 Monitor Basic Example")
    print("=" * 50)
    
    try:
        # Step 1: Configure the monitor
        config = MonitorConfig(
            monitor_addresses=[
                "TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8",  # Example Tron address
                "TLyqzVGLV1srkB7dToTAEqgDSfPtXRJZYH",  # Another example
            ],
            tron_full_node="https://api.trongrid.io",
            # tron_api_key="your_api_key_here",  # Optional, but recommended for rate limits
            usdt_contract_address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
            max_transaction_age_hours=24,
            check_interval_seconds=60,
            large_transaction_threshold=1000.0,  # Alert for transactions >= 1000 USDT
        )
        print(f"✅ Configuration created for {len(config.monitor_addresses)} addresses")

        # Step 2: Create adapters
        # Use memory storage (transactions are not persisted)
        database_adapter = MemoryDatabaseAdapter()
        
        # Use console notifications (print to terminal)
        notification_adapter = ConsoleNotificationAdapter(
            use_colors=True,
            include_metadata=True
        )
        print("✅ Adapters created (memory database + console notifications)")

        # Step 3: Create the monitor
        monitor = TRC20Monitor(
            config=config,
            database_adapter=database_adapter,
            notification_adapter=notification_adapter,
        )
        print("✅ TRC20 Monitor created")

        # Step 4: Initialize the monitor
        await monitor.initialize()
        print("✅ Monitor initialized")

        # Step 5: Run monitoring check once
        print("\n🔍 Running single transaction check...")
        await monitor.check_transactions()
        print("✅ Transaction check completed")

        # Step 6: Check monitor health
        print("\n🏥 Checking system health...")
        health = await monitor.health_check()
        print("Health Status:")
        for component, status in health.items():
            status_icon = "✅" if status == "ok" else "❌"
            print(f"  {status_icon} {component}: {status}")

        # Step 7: Get some statistics
        print("\n📊 Database Statistics:")
        transaction_count = await database_adapter.get_transaction_count()
        print(f"  Total processed transactions: {transaction_count}")

        # Step 8: Clean up
        await monitor.close()
        print("\n✅ Monitor closed successfully")

    except ValidationError as e:
        print(f"❌ Validation Error: {e}")
    except ConfigurationError as e:
        print(f"❌ Configuration Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        raise


async def continuous_monitoring_example():
    """Example of continuous monitoring (runs forever until interrupted)."""
    print("🔄 Starting Continuous TRC20 Monitoring")
    print("Press Ctrl+C to stop...")
    print("=" * 50)

    # Create configuration from environment variables
    try:
        config = MonitorConfig.from_env()
    except ConfigurationError:
        # Fallback to hardcoded config if env vars are not set
        print("⚠️ Environment variables not found, using example configuration")
        config = MonitorConfig(
            monitor_addresses=[
                "TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8",
            ],
            check_interval_seconds=30,  # Check every 30 seconds for demo
        )

    # Create adapters
    database_adapter = MemoryDatabaseAdapter()
    notification_adapter = ConsoleNotificationAdapter()

    # Create monitor
    monitor = TRC20Monitor(
        config=config,
        database_adapter=database_adapter,
        notification_adapter=notification_adapter,
    )

    try:
        # Start continuous monitoring
        await monitor.start_monitoring(run_once=False)
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitor...")
        await monitor.close()
        print("✅ Monitor stopped")


async def environment_config_example():
    """Example showing how to use environment variables for configuration."""
    print("🌍 Environment Configuration Example")
    print("=" * 40)

    # Set example environment variables (normally these would be set in your shell/container)
    example_env = {
        "MONITOR_ADDRESSES": "TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8,TLyqzVGLV1srkB7dToTAEqgDSfPtXRJZYH",
        "TRON_FULL_NODE": "https://api.trongrid.io",
        "TRON_API_KEY": "your_api_key_here",
        "MAX_TRANSACTION_AGE_HOURS": "12",
        "CHECK_INTERVAL_SECONDS": "120",
        "LARGE_TRANSACTION_THRESHOLD": "5000.0",
    }

    # Temporarily set environment variables
    original_env = {}
    for key, value in example_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    try:
        # Create config from environment
        config = MonitorConfig.from_env()
        print("✅ Configuration loaded from environment variables:")
        print(f"  Monitor Addresses: {config.monitor_addresses}")
        print(f"  Tron Node: {config.tron_full_node}")
        print(f"  API Key: {'*' * len(config.tron_api_key) if config.tron_api_key else 'Not set'}")
        print(f"  Check Interval: {config.check_interval_seconds} seconds")
        print(f"  Large Transaction Threshold: {config.large_transaction_threshold} USDT")

    finally:
        # Restore original environment
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value


def print_usage_instructions():
    """Print usage instructions."""
    print("\n" + "=" * 60)
    print("📚 TRC20 Monitor Usage Instructions")
    print("=" * 60)
    print()
    print("1. Set Environment Variables (recommended):")
    print("   export MONITOR_ADDRESSES='TYourAddress1,TYourAddress2'")
    print("   export TRON_API_KEY='your_tron_grid_api_key'")
    print("   export LARGE_TRANSACTION_THRESHOLD='1000.0'")
    print()
    print("2. Or create a configuration file:")
    print("   See config.json.example for the format")
    print()
    print("3. Choose your adapters:")
    print("   - Database: MemoryDatabaseAdapter, SQLiteDatabaseAdapter")
    print("   - Notifications: ConsoleNotificationAdapter, FileNotificationAdapter, WebhookNotificationAdapter")
    print()
    print("4. Run monitoring:")
    print("   - Once: await monitor.check_transactions()")
    print("   - Continuous: await monitor.start_monitoring()")
    print()
    print("5. For production, consider:")
    print("   - Using SQLite or PostgreSQL for persistence")
    print("   - Setting up webhook notifications")
    print("   - Implementing proper logging")
    print("   - Adding monitoring and alerting")
    print()


async def main():
    """Main function to run examples."""
    print("🎯 TRC20 Monitor Examples")
    print("=" * 30)
    print()
    print("Select an example to run:")
    print("1. Basic monitoring (single check)")
    print("2. Continuous monitoring (until Ctrl+C)")
    print("3. Environment configuration demo")
    print("4. Show usage instructions")
    print()

    try:
        choice = input("Enter your choice (1-4): ").strip()
        print()

        if choice == "1":
            await basic_monitoring_example()
        elif choice == "2":
            await continuous_monitoring_example()
        elif choice == "3":
            await environment_config_example()
        elif choice == "4":
            print_usage_instructions()
        else:
            print("❌ Invalid choice. Please run again and select 1-4.")
            return

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())