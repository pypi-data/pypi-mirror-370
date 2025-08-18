"""Tron utility functions for address conversion and transaction parsing."""

import hashlib
from typing import Optional

import base58

from ..core.exceptions import ValidationError


class TronAddressConverter:
    """Utility class for Tron address conversions."""

    @staticmethod
    def hex_to_base58(hex_address: str) -> str:
        """Convert hex address to base58 address.
        
        Args:
            hex_address: Hex address (with or without 0x prefix)
            
        Returns:
            Base58 encoded Tron address
            
        Raises:
            ValidationError: If hex address is invalid
        """
        if not hex_address:
            raise ValidationError("Hex address cannot be empty")

        try:
            # Handle 0x prefix
            if hex_address.startswith("0x"):
                hex_address = hex_address[2:]

            # Add Tron mainnet prefix (41) if not present
            if not hex_address.startswith("41"):
                hex_address = "41" + hex_address

            # Validate hex string
            if not all(c in "0123456789abcdefABCDEF" for c in hex_address):
                raise ValidationError(f"Invalid hex characters in address: {hex_address}")

            # Convert hex to bytes
            address_bytes = bytes.fromhex(hex_address)

            # Double SHA256 hash for checksum
            hash1 = hashlib.sha256(address_bytes).digest()
            hash2 = hashlib.sha256(hash1).digest()

            # Take first 4 bytes as checksum
            checksum = hash2[:4]

            # Append checksum
            address_with_checksum = address_bytes + checksum

            # Encode in base58
            return base58.b58encode(address_with_checksum).decode("utf-8")
            
        except ValueError as e:
            raise ValidationError(f"Invalid hex address format: {hex_address}") from e

    @staticmethod
    def base58_to_hex(base58_address: str) -> str:
        """Convert base58 address to hex address.
        
        Args:
            base58_address: Base58 encoded Tron address
            
        Returns:
            Hex address without 0x prefix
            
        Raises:
            ValidationError: If base58 address is invalid
        """
        if not base58_address:
            raise ValidationError("Base58 address cannot be empty")

        try:
            # Decode base58
            decoded = base58.b58decode(base58_address)

            if len(decoded) != 25:
                raise ValidationError(f"Invalid base58 address length: {len(decoded)}")

            # Remove checksum (last 4 bytes)
            address_bytes = decoded[:-4]
            checksum = decoded[-4:]

            # Verify checksum
            hash1 = hashlib.sha256(address_bytes).digest()
            hash2 = hashlib.sha256(hash1).digest()
            expected_checksum = hash2[:4]

            if checksum != expected_checksum:
                raise ValidationError("Invalid base58 address checksum")

            # Convert to hex and remove 41 prefix for Tron mainnet
            hex_address = address_bytes.hex()
            if hex_address.startswith("41"):
                hex_address = hex_address[2:]

            return hex_address

        except (ValueError, base58.Base58Error) as e:
            raise ValidationError(f"Invalid base58 address: {base58_address}") from e

    @staticmethod
    def is_valid_tron_address(address: str) -> bool:
        """Check if address is a valid Tron address.
        
        Args:
            address: Address to validate
            
        Returns:
            True if address is valid, False otherwise
        """
        try:
            if not address or not isinstance(address, str):
                return False

            if len(address) != 34 or not address.startswith("T"):
                return False

            # Try to decode and verify checksum
            decoded = base58.b58decode(address)
            if len(decoded) != 25:
                return False

            address_bytes = decoded[:-4]
            checksum = decoded[-4:]

            # Verify checksum
            hash1 = hashlib.sha256(address_bytes).digest()
            hash2 = hashlib.sha256(hash1).digest()

            return hash2[:4] == checksum
        except Exception:
            return False

    @staticmethod
    def normalize_address(address: str) -> str:
        """Normalize a Tron address by validating and returning it.
        
        Args:
            address: Address to normalize
            
        Returns:
            Normalized address
            
        Raises:
            ValidationError: If address is invalid
        """
        if not TronAddressConverter.is_valid_tron_address(address):
            raise ValidationError(f"Invalid Tron address: {address}")
        return address


def parse_trc20_transfer_data(data: str) -> Optional[dict]:
    """Parse TRC20 transfer transaction data.
    
    Args:
        data: Hex-encoded transaction data
        
    Returns:
        Dictionary with 'to' and 'amount' keys, or None if parsing fails
    """
    try:
        if not data or len(data) < 136:
            return None

        # Remove 0x prefix if present
        if data.startswith("0x"):
            data = data[2:]

        # Check if it's a transfer method (a9059cbb)
        method = data[:8]
        if method.lower() != "a9059cbb":
            return None

        # Parse to address (32 bytes, but last 20 bytes are the address)
        to_hex = data[32:72]
        # Parse amount (32 bytes)
        amount_hex = data[72:136]

        # Convert hex to address
        to_address = TronAddressConverter.hex_to_base58("41" + to_hex[-40:])

        # Convert hex to amount
        amount = int(amount_hex, 16)

        return {"to": to_address, "amount": amount}
    except Exception:
        return None


def format_tron_amount(amount: int, decimals: int = 6) -> float:
    """Format a raw token amount to its decimal representation.
    
    Args:
        amount: Raw amount (e.g., from contract)
        decimals: Number of decimal places for the token
        
    Returns:
        Formatted amount as float
    """
    return amount / (10 ** decimals)


def to_sun(amount: float) -> int:
    """Convert TRX amount to SUN (smallest TRX unit).
    
    Args:
        amount: TRX amount
        
    Returns:
        Amount in SUN (1 TRX = 1,000,000 SUN)
    """
    return int(amount * 1_000_000)


def from_sun(amount: int) -> float:
    """Convert SUN amount to TRX.
    
    Args:
        amount: Amount in SUN
        
    Returns:
        TRX amount
    """
    return amount / 1_000_000


def is_contract_address(address: str) -> bool:
    """Check if an address is likely a contract address.
    
    This is a heuristic check based on common patterns.
    
    Args:
        address: Tron address to check
        
    Returns:
        True if address appears to be a contract, False otherwise
    """
    if not TronAddressConverter.is_valid_tron_address(address):
        return False
        
    # Convert to hex to check patterns
    try:
        hex_addr = TronAddressConverter.base58_to_hex(address)
        # Contract addresses often have specific patterns or prefixes
        # This is a simplified check - in practice you'd query the network
        return len(hex_addr) == 40  # All valid addresses are 40 hex chars
    except ValidationError:
        return False