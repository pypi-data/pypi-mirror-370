"""
FIPS 140-3 Compliant Entropy and Random Generation

This module provides FIPS-compliant random number generation and entropy management
based on the proven implementation from the EmpowerNow IdP.
"""

import os
import secrets
import logging
from typing import Optional, Union
import hashlib
import time

logger = logging.getLogger(__name__)


class FIPSCompliantRandom:
    """
    FIPS 140-3 compliant random number generation.

    Based on the production-tested implementation from EmpowerNow IdP.
    """

    def __init__(self, validate_entropy: bool = True):
        """
        Initialize FIPS-compliant random generator.

        Args:
            validate_entropy: Whether to validate entropy source on init

        Raises:
            RuntimeError: If entropy source validation fails
        """
        self.validate_entropy = validate_entropy

        if validate_entropy and not self._validate_entropy_source():
            raise RuntimeError("System entropy source not FIPS-compliant")

    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate cryptographically secure random token.

        Args:
            length: Token length in bytes

        Returns:
            str: URL-safe base64 encoded token
        """
        return secrets.token_urlsafe(length)

    def generate_nonce(self, length: int = 16) -> str:
        """
        Generate secure nonce for DPoP and other protocols.

        Args:
            length: Nonce length in bytes

        Returns:
            str: Hexadecimal encoded nonce
        """
        return secrets.token_hex(length)

    def generate_correlation_id(self) -> str:
        """
        Generate correlation ID for request tracing.

        Returns:
            str: UUID-style correlation ID
        """
        # Use secure random bytes to generate UUID-like string
        random_bytes = secrets.token_bytes(16)

        # Format as UUID v4 (random)
        hex_string = random_bytes.hex()
        return f"{hex_string[:8]}-{hex_string[8:12]}-{hex_string[12:16]}-{hex_string[16:20]}-{hex_string[20:]}"

    def generate_state_parameter(self, length: int = 32) -> str:
        """
        Generate OAuth state parameter.

        Args:
            length: State parameter length in bytes

        Returns:
            str: URL-safe state parameter
        """
        return self.generate_secure_token(length)

    def generate_code_verifier(self, length: int = 128) -> str:
        """
        Generate PKCE code verifier.

        Args:
            length: Code verifier length (43-128 characters)

        Returns:
            str: URL-safe code verifier

        Raises:
            ValueError: If length is outside valid range
        """
        if not (43 <= length <= 128):
            raise ValueError(
                "Code verifier length must be between 43 and 128 characters"
            )

        # Generate enough bytes to get desired character count
        byte_length = (length * 3) // 4  # Base64 encoding ratio
        return secrets.token_urlsafe(byte_length)[:length]

    def generate_dpop_jti(self) -> str:
        """
        Generate DPoP JTI (JWT ID) claim.

        Returns:
            str: Unique JTI for DPoP proof
        """
        # Combine timestamp and random data for uniqueness
        timestamp = str(int(time.time() * 1000))  # Millisecond precision
        random_part = secrets.token_hex(8)
        return f"{timestamp}-{random_part}"

    def generate_session_id(self, length: int = 32) -> str:
        """
        Generate secure session identifier.

        Args:
            length: Session ID length in bytes

        Returns:
            str: Hexadecimal session ID
        """
        return secrets.token_hex(length)

    def generate_api_key(self, prefix: str = "enpw", length: int = 32) -> str:
        """
        Generate API key with prefix.

        Args:
            prefix: API key prefix
            length: Random part length in bytes

        Returns:
            str: API key with format {prefix}_{random}
        """
        random_part = secrets.token_urlsafe(length)
        return f"{prefix}_{random_part}"

    def generate_client_secret(self, length: int = 64) -> str:
        """
        Generate OAuth client secret.

        Args:
            length: Secret length in bytes

        Returns:
            str: URL-safe client secret
        """
        return self.generate_secure_token(length)

    def constant_time_compare(self, a: Optional[str], b: Optional[str]) -> bool:
        """
        Constant-time string comparison to prevent timing attacks.

        Args:
            a: First string
            b: Second string

        Returns:
            bool: True if strings are equal
        """
        if a is None or b is None:
            return a is b

        # Use secrets.compare_digest for constant-time comparison
        return secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))

    def _validate_entropy_source(self) -> bool:
        """
        Validate that system entropy meets FIPS requirements.

        Returns:
            bool: True if entropy source is adequate
        """
        try:
            # Check entropy pool health on Linux
            if os.path.exists("/proc/sys/kernel/random/entropy_avail"):
                with open("/proc/sys/kernel/random/entropy_avail", "r") as f:
                    entropy = int(f.read().strip())
                    if entropy < 128:  # Minimum entropy threshold
                        logger.warning(f"Low entropy available: {entropy} bits")
                        return False

            # Test that os.urandom works and produces different values
            test1 = os.urandom(32)
            test2 = os.urandom(32)

            # Basic sanity checks
            if len(test1) != 32 or len(test2) != 32:
                return False

            if test1 == test2:  # Extremely unlikely if working properly
                logger.warning("os.urandom produced identical values")
                return False

            return True

        except Exception as e:
            logger.warning(f"Error validating entropy source: {e}")
            return False


class SecureRandomGenerator:
    """
    Simplified interface for secure random generation.

    Alias for FIPSCompliantRandom for backward compatibility.
    """

    def __init__(self):
        self._generator = FIPSCompliantRandom()

    def generate_token(self, length: int = 32) -> str:
        """Generate secure token."""
        return self._generator.generate_secure_token(length)

    def generate_nonce(self, length: int = 16) -> str:
        """Generate secure nonce."""
        return self._generator.generate_nonce(length)

    def generate_correlation_id(self) -> str:
        """Generate correlation ID."""
        return self._generator.generate_correlation_id()


# Module-level convenience functions
_default_generator = None


def get_default_generator() -> FIPSCompliantRandom:
    """
    Get default FIPS-compliant random generator.

    Returns:
        FIPSCompliantRandom: Default generator instance
    """
    global _default_generator
    if _default_generator is None:
        _default_generator = FIPSCompliantRandom()
    return _default_generator


def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token.

    Args:
        length: Token length in bytes

    Returns:
        str: URL-safe base64 encoded token
    """
    return get_default_generator().generate_secure_token(length)


def generate_nonce(length: int = 16) -> str:
    """
    Generate secure nonce.

    Args:
        length: Nonce length in bytes

    Returns:
        str: Hexadecimal encoded nonce
    """
    return get_default_generator().generate_nonce(length)


def generate_correlation_id() -> str:
    """
    Generate correlation ID for request tracing.

    Returns:
        str: UUID-style correlation ID
    """
    return get_default_generator().generate_correlation_id()
