# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-08-08

### Added
- Initial release of TRC20 Monitor
- Core monitoring functionality for TRC20 transactions
- Pluggable database adapters (Memory, SQLite)
- Pluggable notification adapters (Console, Webhook, File)
- Async/await support throughout
- Command-line interface
- Comprehensive test suite
- Full documentation and examples
- Health monitoring and statistics
- Graceful shutdown and error handling
- Configuration from environment variables and JSON files

### Features
- Monitor multiple Tron addresses simultaneously
- Prevent duplicate transaction processing
- Large amount transaction alerts
- Configurable transaction age filtering
- Robust error handling with retries
- Worker process for continuous monitoring
- Enterprise-ready architecture