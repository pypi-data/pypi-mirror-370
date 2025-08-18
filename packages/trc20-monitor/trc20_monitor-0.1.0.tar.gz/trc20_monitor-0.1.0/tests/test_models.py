"""Tests for core models."""

import pytest
from datetime import datetime

from trc20_monitor.core.models import TRC20Transaction, MonitorConfig
from trc20_monitor.core.exceptions import ValidationError, ConfigurationError


class TestTRC20Transaction:
    """Test TRC20Transaction model."""

    def test_transaction_creation(self):
        """Test creating a valid transaction."""
        tx = TRC20Transaction(
            tx_id="a" * 64,  # Valid 64-char hex string
            from_address="TFromAddress123",
            to_address="TToAddress456", 
            amount=100.5,
            timestamp=1640995200000,
            block_height=12345,
            contract_address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
        )

        assert tx.tx_id == "a" * 64
        assert tx.from_address == "TFromAddress123"
        assert tx.to_address == "TToAddress456"
        assert tx.amount == 100.5
        assert tx.timestamp == 1640995200000
        assert tx.block_height == 12345
        assert tx.contract_address == "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

    def test_transaction_validation_empty_tx_id(self):
        """Test transaction validation with empty tx_id."""
        with pytest.raises(ValidationError, match="Transaction ID is required"):
            TRC20Transaction(
                tx_id="",
                from_address="TFromAddress123",
                to_address="TToAddress456",
                amount=100.5,
                timestamp=1640995200000,
            )

    def test_transaction_validation_empty_from_address(self):
        """Test transaction validation with empty from_address."""
        with pytest.raises(ValidationError, match="From address is required"):
            TRC20Transaction(
                tx_id="a" * 64,
                from_address="",
                to_address="TToAddress456",
                amount=100.5,
                timestamp=1640995200000,
            )

    def test_transaction_validation_negative_amount(self):
        """Test transaction validation with negative amount."""
        with pytest.raises(ValidationError, match="Amount must be non-negative"):
            TRC20Transaction(
                tx_id="a" * 64,
                from_address="TFromAddress123",
                to_address="TToAddress456",
                amount=-10.0,
                timestamp=1640995200000,
            )

    def test_transaction_validation_invalid_timestamp(self):
        """Test transaction validation with invalid timestamp."""
        with pytest.raises(ValidationError, match="Timestamp must be positive"):
            TRC20Transaction(
                tx_id="a" * 64,
                from_address="TFromAddress123",
                to_address="TToAddress456",
                amount=100.5,
                timestamp=-1,
            )

    def test_to_dict(self):
        """Test converting transaction to dictionary."""
        tx = TRC20Transaction(
            tx_id="a" * 64,
            from_address="TFromAddress123",
            to_address="TToAddress456",
            amount=100.5,
            timestamp=1640995200000,
            block_height=12345,
            contract_address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
        )

        expected = {
            "tx_id": "a" * 64,
            "from": "TFromAddress123",
            "to": "TToAddress456",
            "amount": 100.5,
            "timestamp": 1640995200000,
            "block_height": 12345,
            "contract_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
        }

        assert tx.to_dict() == expected

    def test_from_dict(self):
        """Test creating transaction from dictionary."""
        data = {
            "tx_id": "a" * 64,
            "from": "TFromAddress123",
            "to": "TToAddress456",
            "amount": 100.5,
            "timestamp": 1640995200000,
            "block_height": 12345,
            "contract_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
        }

        tx = TRC20Transaction.from_dict(data)

        assert tx.tx_id == "a" * 64
        assert tx.from_address == "TFromAddress123"
        assert tx.to_address == "TToAddress456"
        assert tx.amount == 100.5
        assert tx.timestamp == 1640995200000
        assert tx.block_height == 12345
        assert tx.contract_address == "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

    def test_datetime_property(self):
        """Test datetime property conversion."""
        tx = TRC20Transaction(
            tx_id="a" * 64,
            from_address="TFromAddress123",
            to_address="TToAddress456",
            amount=100.5,
            timestamp=1640995200000,  # 2022-01-01 00:00:00 UTC
        )

        expected_datetime = datetime.fromtimestamp(1640995200)
        assert tx.datetime == expected_datetime

    def test_amount_str_property(self):
        """Test amount_str property formatting."""
        tx = TRC20Transaction(
            tx_id="a" * 64,
            from_address="TFromAddress123",
            to_address="TToAddress456",
            amount=100.123456,
            timestamp=1640995200000,
        )

        assert tx.amount_str == "100.123456"


class TestMonitorConfig:
    """Test MonitorConfig model."""

    def test_config_creation(self):
        """Test creating a valid configuration."""
        config = MonitorConfig(
            monitor_addresses=["TAddress1", "TAddress2"],
            tron_full_node="https://api.trongrid.io",
            usdt_contract_address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
        )

        assert config.monitor_addresses == ["TAddress1", "TAddress2"]
        assert config.tron_full_node == "https://api.trongrid.io"
        assert config.usdt_contract_address == "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
        assert config.max_transaction_age_hours == 24  # default
        assert config.check_interval_seconds == 60  # default
        assert config.large_transaction_threshold == 1000.0  # default

    def test_config_validation_empty_addresses(self):
        """Test configuration validation with empty addresses."""
        with pytest.raises(ConfigurationError, match="At least one monitor address is required"):
            MonitorConfig(monitor_addresses=[])

    def test_config_validation_invalid_age_hours(self):
        """Test configuration validation with invalid age hours."""
        with pytest.raises(ConfigurationError, match="max_transaction_age_hours must be positive"):
            MonitorConfig(
                monitor_addresses=["TAddress1"],
                max_transaction_age_hours=0
            )

    def test_config_validation_invalid_interval(self):
        """Test configuration validation with invalid interval."""
        with pytest.raises(ConfigurationError, match="check_interval_seconds must be positive"):
            MonitorConfig(
                monitor_addresses=["TAddress1"],
                check_interval_seconds=0
            )

    def test_config_validation_negative_threshold(self):
        """Test configuration validation with negative threshold."""
        with pytest.raises(ConfigurationError, match="large_transaction_threshold must be non-negative"):
            MonitorConfig(
                monitor_addresses=["TAddress1"],
                large_transaction_threshold=-100.0
            )

    def test_config_from_dict(self):
        """Test creating configuration from dictionary."""
        config_data = {
            "monitor_addresses": ["TAddress1", "TAddress2"],
            "tron_full_node": "https://custom.trongrid.io",
            "max_transaction_age_hours": 48,
            "check_interval_seconds": 30,
            "large_transaction_threshold": 5000.0,
        }

        config = MonitorConfig.from_dict(config_data)

        assert config.monitor_addresses == ["TAddress1", "TAddress2"]
        assert config.tron_full_node == "https://custom.trongrid.io"
        assert config.max_transaction_age_hours == 48
        assert config.check_interval_seconds == 30
        assert config.large_transaction_threshold == 5000.0

    def test_config_from_env(self, monkeypatch):
        """Test creating configuration from environment variables."""
        # Set environment variables
        monkeypatch.setenv("MONITOR_ADDRESSES", "TAddr1,TAddr2,TAddr3")
        monkeypatch.setenv("TRON_FULL_NODE", "https://test.trongrid.io")
        monkeypatch.setenv("TRON_API_KEY", "test_api_key")
        monkeypatch.setenv("MAX_TRANSACTION_AGE_HOURS", "12")
        monkeypatch.setenv("CHECK_INTERVAL_SECONDS", "120")
        monkeypatch.setenv("LARGE_TRANSACTION_THRESHOLD", "2000.0")

        config = MonitorConfig.from_env()

        assert config.monitor_addresses == ["TAddr1", "TAddr2", "TAddr3"]
        assert config.tron_full_node == "https://test.trongrid.io"
        assert config.tron_api_key == "test_api_key"
        assert config.max_transaction_age_hours == 12
        assert config.check_interval_seconds == 120
        assert config.large_transaction_threshold == 2000.0

    def test_config_from_env_missing_addresses(self, monkeypatch):
        """Test configuration from env with missing addresses."""
        # Clear environment
        monkeypatch.delenv("MONITOR_ADDRESSES", raising=False)
        
        with pytest.raises(ConfigurationError, match="MONITOR_ADDRESSES environment variable is required"):
            MonitorConfig.from_env()

    def test_config_from_env_with_empty_addresses(self, monkeypatch):
        """Test configuration from env with empty address values."""
        monkeypatch.setenv("MONITOR_ADDRESSES", "TAddr1,,TAddr2,")
        
        config = MonitorConfig.from_env()
        
        # Empty strings should be filtered out
        assert config.monitor_addresses == ["TAddr1", "TAddr2"]