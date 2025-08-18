"""Validation utilities for TRC20 monitoring."""

import re
from typing import Optional, Union

from ..core.exceptions import ValidationError


def validate_address(address: str) -> bool:
    """Validate a Tron address.
    
    Args:
        address: Tron address to validate
        
    Returns:
        True if address is valid, False otherwise
    """
    if not address or not isinstance(address, str):
        return False
        
    # Basic format check
    if len(address) != 34 or not address.startswith("T"):
        return False
        
    # More detailed validation could be added here
    # For now, we'll use a basic pattern match
    pattern = r"^T[A-Za-z0-9]{33}$"
    return bool(re.match(pattern, address))


def validate_amount(amount: Union[int, float, str]) -> bool:
    """Validate a transaction amount.
    
    Args:
        amount: Amount to validate
        
    Returns:
        True if amount is valid, False otherwise
    """
    try:
        amount_float = float(amount)
        return amount_float >= 0
    except (ValueError, TypeError):
        return False


def validate_contract(contract_address: str) -> bool:
    """Validate a contract address.
    
    Args:
        contract_address: Contract address to validate
        
    Returns:
        True if contract address is valid, False otherwise
    """
    # Contract addresses follow the same format as regular addresses
    return validate_address(contract_address)


def validate_tx_id(tx_id: str) -> bool:
    """Validate a transaction ID.
    
    Args:
        tx_id: Transaction ID to validate
        
    Returns:
        True if transaction ID is valid, False otherwise
    """
    if not tx_id or not isinstance(tx_id, str):
        return False
        
    # Transaction IDs are 64-character hex strings
    pattern = r"^[a-fA-F0-9]{64}$"
    return bool(re.match(pattern, tx_id))


def validate_timestamp(timestamp: Union[int, str]) -> bool:
    """Validate a timestamp.
    
    Args:
        timestamp: Timestamp to validate (Unix timestamp in milliseconds)
        
    Returns:
        True if timestamp is valid, False otherwise
    """
    try:
        timestamp_int = int(timestamp)
        # Reasonable bounds: after 2020 and before 2040
        min_timestamp = 1577836800000  # 2020-01-01
        max_timestamp = 2208988800000  # 2040-01-01
        return min_timestamp <= timestamp_int <= max_timestamp
    except (ValueError, TypeError):
        return False


def require_valid_address(address: str, field_name: str = "address") -> str:
    """Require a valid Tron address, raising ValidationError if invalid.
    
    Args:
        address: Address to validate
        field_name: Name of the field for error messages
        
    Returns:
        The validated address
        
    Raises:
        ValidationError: If address is invalid
    """
    if not validate_address(address):
        raise ValidationError(f"Invalid Tron {field_name}: {address}")
    return address


def require_valid_amount(amount: Union[int, float, str], field_name: str = "amount") -> float:
    """Require a valid amount, raising ValidationError if invalid.
    
    Args:
        amount: Amount to validate
        field_name: Name of the field for error messages
        
    Returns:
        The validated amount as a float
        
    Raises:
        ValidationError: If amount is invalid
    """
    if not validate_amount(amount):
        raise ValidationError(f"Invalid {field_name}: {amount}")
    return float(amount)


def require_valid_contract(contract_address: str, field_name: str = "contract_address") -> str:
    """Require a valid contract address, raising ValidationError if invalid.
    
    Args:
        contract_address: Contract address to validate
        field_name: Name of the field for error messages
        
    Returns:
        The validated contract address
        
    Raises:
        ValidationError: If contract address is invalid
    """
    if not validate_contract(contract_address):
        raise ValidationError(f"Invalid {field_name}: {contract_address}")
    return contract_address


def require_valid_tx_id(tx_id: str, field_name: str = "transaction_id") -> str:
    """Require a valid transaction ID, raising ValidationError if invalid.
    
    Args:
        tx_id: Transaction ID to validate
        field_name: Name of the field for error messages
        
    Returns:
        The validated transaction ID
        
    Raises:
        ValidationError: If transaction ID is invalid
    """
    if not validate_tx_id(tx_id):
        raise ValidationError(f"Invalid {field_name}: {tx_id}")
    return tx_id


def sanitize_address(address: Optional[str]) -> Optional[str]:
    """Sanitize a Tron address by removing whitespace and validating.
    
    Args:
        address: Address to sanitize
        
    Returns:
        Sanitized address or None if invalid
    """
    if not address:
        return None
        
    # Remove whitespace
    sanitized = address.strip()
    
    # Validate
    if validate_address(sanitized):
        return sanitized
    else:
        return None


def format_amount(amount: Union[int, float], decimals: int = 6) -> str:
    """Format an amount with the specified number of decimals.
    
    Args:
        amount: Amount to format
        decimals: Number of decimal places
        
    Returns:
        Formatted amount string
    """
    return f"{float(amount):.{decimals}f}"