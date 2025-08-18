# TRC20 Monitor

Professional TRC20 transaction monitoring for Tron blockchain with pluggable adapters.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start

### Installation

```bash
pip install trc20-monitor
```

### Basic Usage

```python
import asyncio
from trc20_monitor import (
    TRC20Monitor,
    MonitorConfig,
    MemoryDatabaseAdapter,
    ConsoleNotificationAdapter
)

async def main():
    # Configure monitoring
    config = MonitorConfig(
        monitor_addresses=["TYourTronAddress1", "TYourTronAddress2"],
        large_transaction_threshold=1000.0  # Alert for >= 1000 USDT
    )
    
    # Create adapters
    database = MemoryDatabaseAdapter()
    notifications = ConsoleNotificationAdapter()
    
    # Create monitor
    monitor = TRC20Monitor(
        config=config,
        database_adapter=database,
        notification_adapter=notifications
    )
    
    # Run once or continuously
    await monitor.start_monitoring(run_once=True)

asyncio.run(main())
```

### Environment Configuration

```bash
export MONITOR_ADDRESSES="TAddress1,TAddress2,TAddress3"
export TRON_API_KEY="your_trongrid_api_key"
export LARGE_TRANSACTION_THRESHOLD="5000.0"
export CHECK_INTERVAL_SECONDS="60"
```

```python
# Load from environment variables
config = MonitorConfig.from_env()
```

## 🏗️ Architecture

TRC20 Monitor uses a pluggable adapter architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   TRC20Monitor  │────│ DatabaseAdapter  │────│ NotificationAdapter │
│                 │    │                  │    │                     │
│ - Check API     │    │ - Track TXs      │    │ - Send Alerts       │
│ - Process TXs   │    │ - Prevent Dups   │    │ - Format Messages   │
│ - Handle Errors │    │ - Cleanup Old    │    │ - Multiple Channels │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
         │                       │                        │
         └───────────────────────┼────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     Worker Process      │
                    │ - Continuous Running    │
                    │ - Graceful Shutdown     │
                    │ - Health Monitoring     │
                    │ - Statistics Tracking   │
                    └─────────────────────────┘
```

## 📦 Available Adapters

### Database Adapters

- **MemoryDatabaseAdapter**: In-memory storage (development/testing)
- **SQLiteDatabaseAdapter**: SQLite database (single-node production)
- **SQLAlchemyDatabaseAdapter**: PostgreSQL/MySQL (enterprise)

### Notification Adapters

- **ConsoleNotificationAdapter**: Terminal output with colors
- **FileNotificationAdapter**: JSON/text file logging
- **WebhookNotificationAdapter**: HTTP POST notifications
- **MultiNotificationAdapter**: Multiple channels simultaneously

## 🔧 Advanced Configuration

### Custom Database

```python
from trc20_monitor.implementations import SQLiteDatabaseAdapter

# Persistent SQLite storage
database = SQLiteDatabaseAdapter("monitor.db")

# Or PostgreSQL via SQLAlchemy
from trc20_monitor.implementations import SQLAlchemyDatabaseAdapter
database = SQLAlchemyDatabaseAdapter("postgresql://user:pass@localhost/db")
```

### Multiple Notifications

```python
from trc20_monitor.implementations import (
    WebhookNotificationAdapter,
    FileNotificationAdapter,
    MultiNotificationAdapter
)

# Webhook notifications
webhook = WebhookNotificationAdapter([
    "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "https://discord.com/api/webhooks/YOUR/WEBHOOK"
])

# File logging
file_logger = FileNotificationAdapter("transactions.log", log_format="json")

# Combine multiple channels
notifications = MultiNotificationAdapter([webhook, file_logger])
```

### Worker Process

```python
from trc20_monitor.worker import TRC20Worker

# Background worker with health monitoring
worker = TRC20Worker(
    config=config,
    database_adapter=database,
    notification_adapter=notifications
)

# Start continuous monitoring
await worker.start()  # Runs until stopped
```

## 🖥️ Command Line Interface

```bash
# Initialize configuration file
trc20-monitor init

# Run once
trc20-monitor run-once --notification-type console

# Run continuously  
trc20-monitor --config-file config.json --db-type sqlite run

# Available options
trc20-monitor --help
```

## 📊 Features

### ✅ Core Functionality

- **Multi-address monitoring**: Track multiple Tron addresses simultaneously
- **Duplicate prevention**: Automatically prevents reprocessing transactions
- **Large amount alerts**: Configurable threshold for high-value transaction alerts
- **Transaction age filtering**: Ignore old transactions to focus on recent activity
- **Robust error handling**: Graceful degradation and automatic retry mechanisms

### ✅ Production Ready

- **Async/await**: Full asyncio support for high performance
- **Pluggable architecture**: Swap database and notification backends easily
- **Health monitoring**: Built-in health checks for all components
- **Graceful shutdown**: Proper cleanup on termination signals
- **Statistics tracking**: Monitor processing rates and error counts

### ✅ Enterprise Features

- **PostgreSQL support**: Scale to high transaction volumes
- **Webhook notifications**: Integrate with Slack, Discord, PagerDuty, etc.
- **Structured logging**: JSON logs for centralized log management
- **Configuration management**: Environment variables, JSON files, or code-based
- **Test coverage**: Comprehensive test suite with async test support

## 🧪 Testing

```bash
# Install development dependencies
pip install trc20-monitor[dev]

# Run tests
pytest

# With coverage
pytest --cov=trc20_monitor

# Integration tests
pytest -m integration
```

## 📈 Monitoring & Observability

### Health Checks

```python
# Component health status
health = await monitor.health_check()
print(health)
# {
#   "monitor": "ok",
#   "database": "ok", 
#   "notifications": "ok",
#   "api_connectivity": "ok"
# }
```

### Statistics

```python
# Worker statistics
stats = worker.get_stats()
print(f"Uptime: {stats['uptime_seconds']}s")
print(f"Successful checks: {stats['successful_checks']}")
print(f"Failed checks: {stats['failed_checks']}")
```

### Custom Metrics

```python
# Get transaction counts
total = await database.get_transaction_count()
recent = await database.get_recent_transactions(limit=10)

# Address-specific stats  
addr_summary = await database.get_addresses_summary()
```

## 🔐 Security Best Practices

### API Keys

```bash
# Use environment variables for sensitive data
export TRON_API_KEY="your_api_key_here"

# Or use a secrets management system
# Never commit API keys to version control
```

### Network Security

```python
# Configure timeouts and retries
config = MonitorConfig(
    api_timeout_seconds=30,
    api_retries=3,
    retry_delay_seconds=5
)
```

### Input Validation

```python
# All inputs are validated
from trc20_monitor.utils import validate_address

if validate_address("TYourAddress"):
    print("Valid Tron address")
```

## 🚦 Error Handling

The library provides comprehensive error handling:

```python
from trc20_monitor.core.exceptions import (
    TRC20MonitorError,      # Base exception
    ConfigurationError,     # Configuration issues
    ValidationError,        # Input validation errors
    APIError,              # Tron API errors
    DatabaseError,         # Database operation errors
    NotificationError      # Notification sending errors
)

try:
    await monitor.check_transactions()
except APIError as e:
    print(f"API error: {e.status_code} - {e}")
except DatabaseError as e:
    print(f"Database error: {e}")
```

## 📚 Examples

Check the `examples/` directory for complete working examples:

- `basic_usage.py`: Simple monitoring setup
- `with_database.py`: SQLite persistence 
- `webhook_example.py`: Webhook notifications
- `enterprise_setup.py`: Production configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/kun-g/trc20-monitor.git
cd trc20-monitor
pip install -e .[dev]
pre-commit install
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Tron Network](https://tron.network/) for the blockchain infrastructure
- [TronGrid](https://www.trongrid.io/) for API services
- [aiogram](https://aiogram.dev/) for Telegram bot inspiration
- [FastAPI](https://fastapi.tiangolo.com/) for async patterns

## 📞 Support

- 📖 [Documentation](https://trc20-monitor.readthedocs.io/)
- 🐛 [Issues](https://github.com/kun-g/trc20-monitor/issues)
- 💬 [Discussions](https://github.com/kun-g/trc20-monitor/discussions)
- 📧 Email: support@trc20monitor.com

---

**Made with ❤️ for the Tron ecosystem**