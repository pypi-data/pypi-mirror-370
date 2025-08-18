"""Data models for TRC20 monitoring."""

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union

from .exceptions import ConfigurationError, ValidationError


@dataclass
class TRC20Transaction:
    """Represents a TRC20 transaction."""

    tx_id: str
    from_address: str
    to_address: str
    amount: float
    timestamp: int  # Unix timestamp in milliseconds
    block_height: int = 0
    contract_address: Optional[str] = None

    def __post_init__(self):
        """Validate transaction data after initialization."""
        if not self.tx_id:
            raise ValidationError("Transaction ID is required")
        if not self.from_address:
            raise ValidationError("From address is required")
        if not self.to_address:
            raise ValidationError("To address is required")
        if self.amount < 0:
            raise ValidationError("Amount must be non-negative")
        if self.timestamp <= 0:
            raise ValidationError("Timestamp must be positive")

    def to_dict(self) -> Dict[str, Union[str, float, int]]:
        """Convert transaction to dictionary."""
        return {
            "tx_id": self.tx_id,
            "from": self.from_address,
            "to": self.to_address,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "block_height": self.block_height,
            "contract_address": self.contract_address,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, float, int]]) -> "TRC20Transaction":
        """Create transaction from dictionary."""
        return cls(
            tx_id=str(data["tx_id"]),
            from_address=str(data.get("from", "")),
            to_address=str(data.get("to", "")),
            amount=float(data.get("amount", 0)),
            timestamp=int(data.get("timestamp", 0)),
            block_height=int(data.get("block_height", 0)),
            contract_address=data.get("contract_address"),
        )

    @property
    def datetime(self) -> datetime:
        """Get transaction datetime from timestamp."""
        return datetime.fromtimestamp(self.timestamp / 1000)

    @property
    def amount_str(self) -> str:
        """Get formatted amount string."""
        return f"{self.amount:.6f}"

    def __str__(self) -> str:
        """String representation of transaction."""
        return (
            f"TRC20Transaction({self.amount_str} from {self.from_address[:8]}... "
            f"to {self.to_address[:8]}... at {self.datetime.isoformat()})"
        )


@dataclass
class MonitorConfig:
    """Configuration for TRC20 monitoring."""

    # Required settings
    monitor_addresses: List[str]
    
    # Tron network settings
    tron_full_node: str = "https://api.trongrid.io"
    tron_api_key: Optional[str] = None
    
    # Contract settings
    usdt_contract_address: str = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    
    # Monitoring settings
    max_transaction_age_hours: int = 24
    check_interval_seconds: int = 60
    large_transaction_threshold: float = 1000.0
    
    # API settings
    api_timeout_seconds: int = 30
    api_retries: int = 3
    retry_delay_seconds: int = 5
    
    # Database settings (for cleanup)
    cleanup_old_records_days: int = 30

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.monitor_addresses:
            raise ConfigurationError("At least one monitor address is required")
        
        if self.max_transaction_age_hours <= 0:
            raise ConfigurationError("max_transaction_age_hours must be positive")
        
        if self.check_interval_seconds <= 0:
            raise ConfigurationError("check_interval_seconds must be positive")
        
        if self.large_transaction_threshold < 0:
            raise ConfigurationError("large_transaction_threshold must be non-negative")
        
        if self.api_timeout_seconds <= 0:
            raise ConfigurationError("api_timeout_seconds must be positive")
        
        if self.cleanup_old_records_days <= 0:
            raise ConfigurationError("cleanup_old_records_days must be positive")

    @classmethod
    def from_env(cls) -> "MonitorConfig":
        """Create configuration from environment variables."""
        # Parse monitor addresses
        monitor_addresses_str = os.getenv("MONITOR_ADDRESSES", "")
        if not monitor_addresses_str:
            raise ConfigurationError("MONITOR_ADDRESSES environment variable is required")
        
        monitor_addresses = [addr.strip() for addr in monitor_addresses_str.split(",")]
        monitor_addresses = [addr for addr in monitor_addresses if addr]  # Remove empty strings
        
        return cls(
            monitor_addresses=monitor_addresses,
            tron_full_node=os.getenv("TRON_FULL_NODE", "https://api.trongrid.io"),
            tron_api_key=os.getenv("TRON_API_KEY"),
            usdt_contract_address=os.getenv(
                "USDT_CONTRACT_ADDRESS", "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
            ),
            max_transaction_age_hours=int(os.getenv("MAX_TRANSACTION_AGE_HOURS", "24")),
            check_interval_seconds=int(os.getenv("CHECK_INTERVAL_SECONDS", "60")),
            large_transaction_threshold=float(os.getenv("LARGE_TRANSACTION_THRESHOLD", "1000.0")),
            api_timeout_seconds=int(os.getenv("API_TIMEOUT_SECONDS", "30")),
            api_retries=int(os.getenv("API_RETRIES", "3")),
            retry_delay_seconds=int(os.getenv("RETRY_DELAY_SECONDS", "5")),
            cleanup_old_records_days=int(os.getenv("CLEANUP_OLD_RECORDS_DAYS", "30")),
        )

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Union[str, int, float, List[str]]]) -> "MonitorConfig":
        """Create configuration from dictionary."""
        return cls(**config_dict)