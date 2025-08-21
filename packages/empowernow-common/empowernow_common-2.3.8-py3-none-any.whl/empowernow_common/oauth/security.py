"""
🛡️ OAuth Security Module

Comprehensive security utilities for OAuth implementations:
- URL validation and SSRF protection
- Input sanitization and XSS prevention
- FIPS compliance validation
- Secure token generation
- Security fingerprinting

All functions are production-ready with extensive validation.
"""

import hashlib
import hmac
import secrets
import re
import json
import logging
from urllib.parse import urlparse
from typing import Set, Optional, Dict, Any
from dataclasses import dataclass
from empowernow_common.errors import UrlValidationError, TokenValidationError, ErrorCode
from ..exceptions import EmpowerNowError

logger = logging.getLogger(__name__)

# Security constants
MAX_URL_LENGTH = 2048
MAX_INPUT_LENGTH = 4096
MAX_SCOPE_LENGTH = 1024
DANGEROUS_CHARACTERS = {"<", ">", '"', "'", "&", "\n", "\r", "\0"}


class SecurityError(EmpowerNowError):
    """Base security error"""

    pass


class FIPSValidator:
    """🛡️ FIPS 140-2 compliance validator"""

    _fips_algorithms = {
        "jwt_signing": {"RS256", "RS384", "RS512", "ES256", "ES384", "ES512"},
        "dpop_signing": {"ES256", "RS256"},
        "symmetric_encryption": {"AES-256-GCM", "AES-192-GCM", "AES-128-GCM"},
        "key_derivation": {"PBKDF2", "scrypt", "Argon2"},
        "hashing": {"SHA-256", "SHA-384", "SHA-512"},
    }

    _min_key_sizes = {
        "RSA": 2048,
        "EC_P256": 256,
        "EC_P384": 384,
        "EC_P521": 521,
        "AES": 128,
    }

    @classmethod
    def validate_algorithm(cls, algorithm: str, context: str) -> None:
        """Validate algorithm is FIPS-approved"""
        if context not in cls._fips_algorithms:
            raise SecurityError(f"Unknown algorithm context: {context}")

        if algorithm not in cls._fips_algorithms[context]:
            raise SecurityError(
                f"Algorithm {algorithm} not FIPS-approved for {context}"
            )

    @classmethod
    def validate_key_strength(cls, key_type: str, key_size: int) -> None:
        """Validate key meets FIPS strength requirements"""
        if key_type not in cls._min_key_sizes:
            raise SecurityError(f"Unknown key type: {key_type}")

        min_size = cls._min_key_sizes[key_type]
        if key_size < min_size:
            raise SecurityError(
                f"{key_type} key size {key_size} below FIPS minimum {min_size}"
            )


def validate_url_security(
    url: str, allowed_schemes: Set[str] = None, context: str = "URL"
) -> str:
    """
    🛡️ Comprehensive URL validation with SSRF protection

    Args:
        url: URL to validate
        allowed_schemes: Allowed URL schemes (default: https only)
        context: Context for error messages

    Returns:
        str: Validated URL

    Raises:
        SecurityError: If URL is invalid or dangerous
    """
    if not isinstance(url, str):
        raise UrlValidationError(
            f"{context} must be string", error_code=ErrorCode.URL_INVALID
        )

    if len(url) > MAX_URL_LENGTH:
        raise SecurityError(f"{context} too long (max {MAX_URL_LENGTH})")

    # Default to HTTPS only
    if allowed_schemes is None:
        allowed_schemes = {"https"}

    try:
        parsed = urlparse(url)
    except Exception as e:
        raise UrlValidationError(
            f"Invalid {context}: {e}", error_code=ErrorCode.URL_INVALID
        )

    # Validate scheme
    if parsed.scheme not in allowed_schemes:
        raise UrlValidationError(
            f"Invalid {context} scheme: {parsed.scheme}",
            error_code=ErrorCode.URL_INVALID,
        )

    # Validate hostname exists
    if not parsed.netloc:
        raise SecurityError(f"Missing hostname in {context}")

    # SSRF protection - block private/internal addresses
    hostname = parsed.hostname
    if hostname:
        # Block localhost variations
        localhost_patterns = [
            r"^localhost$",
            r"^127\.",
            r"^0\.0\.0\.0$",
            r"^::1$",
            r"^0:0:0:0:0:0:0:1$",
        ]

        for pattern in localhost_patterns:
            if re.match(pattern, hostname.lower()):
                raise UrlValidationError(
                    "Localhost not allowed", error_code=ErrorCode.URL_PRIVATE
                )

        # Block private IP ranges (RFC 1918)
        private_ip_patterns = [
            r"^10\.",
            r"^172\.(1[6-9]|2[0-9]|3[01])\.",
            r"^192\.168\.",
            r"^169\.254\.",  # Link-local
            r"^fc00:",  # IPv6 private
            r"^fe80:",  # IPv6 link-local
        ]

        for pattern in private_ip_patterns:
            if re.match(pattern, hostname.lower()):
                raise UrlValidationError(
                    "Private IP not allowed", error_code=ErrorCode.URL_PRIVATE
                )

    # Validate no dangerous characters
    dangerous_chars = {"<", ">", '"', "'", "`", "\n", "\r", "\0"}
    if any(char in url for char in dangerous_chars):
        raise SecurityError(f"Dangerous characters in {context}")

    return url


def sanitize_string_input(
    value: str, max_length: int, field_name: str, allow_special_chars: bool = False
) -> str:
    """
    🛡️ Sanitize string input with XSS protection

    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        field_name: Field name for error messages
        allow_special_chars: Whether to allow special characters

    Returns:
        str: Sanitized string

    Raises:
        SecurityError: If input is invalid or dangerous
    """
    if not isinstance(value, str):
        raise SecurityError(f"{field_name} must be string")

    if len(value) > max_length:
        raise SecurityError(f"{field_name} too long (max {max_length})")

    if not value.strip():
        raise SecurityError(f"{field_name} cannot be empty")

    # Check for dangerous characters
    if not allow_special_chars:
        if any(char in value for char in DANGEROUS_CHARACTERS):
            raise SecurityError(f"Dangerous characters in {field_name}")

    # Basic XSS protection
    xss_patterns = [
        r"<script[^>]*>",
        r"javascript:",
        r"vbscript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*=",
        r"eval\s*\(",
        r"expression\s*\(",
    ]

    value_lower = value.lower()
    for pattern in xss_patterns:
        if re.search(pattern, value_lower):
            raise SecurityError(f"Potential XSS in {field_name}")

    return value.strip()


def generate_secure_token(length: int = 32) -> str:
    """
    🛡️ Generate cryptographically secure token

    Args:
        length: Token length in bytes

    Returns:
        str: URL-safe base64 encoded token
    """
    if length < 8 or length > 128:
        raise SecurityError("Token length must be 8-128 bytes")

    return secrets.token_urlsafe(length)


def generate_correlation_id() -> str:
    """Generate correlation ID for request tracking"""
    return generate_secure_token(16)


def create_security_fingerprint(
    user_agent: str, client_id: str, additional_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    🛡️ Create security fingerprint for client identification

    Args:
        user_agent: User agent string
        client_id: OAuth client ID
        additional_data: Additional fingerprinting data

    Returns:
        str: Security fingerprint hash
    """
    # Sanitize inputs
    user_agent = sanitize_string_input(
        user_agent, 512, "user_agent", allow_special_chars=True
    )
    client_id = sanitize_string_input(client_id, 256, "client_id")

    # Build fingerprint string
    fingerprint_data = {"user_agent": user_agent, "client_id": client_id}

    if additional_data:
        # Only include safe additional data
        for key, value in additional_data.items():
            if isinstance(value, (str, int, bool)) and len(str(value)) < 256:
                fingerprint_data[key] = value

    # Create deterministic JSON string
    fingerprint_str = json.dumps(
        fingerprint_data, sort_keys=True, separators=(",", ":")
    )

    # Generate SHA-256 hash
    return hashlib.sha256(fingerprint_str.encode()).hexdigest()


def validate_jwt_claims(
    claims: Dict[str, Any],
    required_claims: Set[str],
    client_id: str,
    max_age_seconds: int = 300,
) -> None:
    """
    🛡️ Validate JWT claims for security

    Args:
        claims: JWT claims to validate
        required_claims: Set of required claim names
        client_id: Expected client ID for audience validation
        max_age_seconds: Maximum age for token validity

    Raises:
        SecurityError: If claims are invalid
    """
    import time

    # Check required claims
    missing_claims = required_claims - set(claims.keys())
    if missing_claims:
        raise SecurityError(f"Missing required claims: {missing_claims}")

    # Validate audience if present
    aud = claims.get("aud")
    if aud:
        if isinstance(aud, list):
            if client_id not in aud:
                raise SecurityError(f"Client ID not in audience")
        elif aud != client_id:
            raise SecurityError(f"Invalid audience")

    # Validate expiration
    exp = claims.get("exp")
    if exp:
        if not isinstance(exp, int):
            raise SecurityError("Invalid expiration claim")

        current_time = int(time.time())
        if current_time >= exp:
            raise SecurityError("Token has expired")

    # Validate not before
    nbf = claims.get("nbf")
    if nbf:
        if not isinstance(nbf, int):
            raise SecurityError("Invalid not-before claim")

        current_time = int(time.time())
        if current_time < nbf:
            raise SecurityError("Token not yet valid")

    # Validate issued at with max age
    iat = claims.get("iat")
    if iat:
        if not isinstance(iat, int):
            raise SecurityError("Invalid issued-at claim")

        current_time = int(time.time())
        age = current_time - iat
        if age > max_age_seconds:
            raise SecurityError(f"Token too old (age: {age}s, max: {max_age_seconds}s)")

        # Prevent future tokens (with clock skew tolerance)
        if iat > (current_time + 60):
            raise SecurityError("Token issued in the future")


@dataclass
class SecurityContext:
    """🛡️ Security context for OAuth operations"""

    client_fingerprint: str
    request_id: str
    user_agent: str
    client_id: str
    created_at: float

    @classmethod
    def create(
        cls,
        user_agent: str,
        client_id: str,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> "SecurityContext":
        """Create new security context"""
        import time

        request_id = generate_correlation_id()
        fingerprint = create_security_fingerprint(
            user_agent, client_id, additional_data
        )

        return cls(
            client_fingerprint=fingerprint,
            request_id=request_id,
            user_agent=user_agent,
            client_id=client_id,
            created_at=time.time(),
        )

    def is_expired(self, max_age_seconds: int = 3600) -> bool:
        """Check if security context has expired"""
        import time

        return (time.time() - self.created_at) > max_age_seconds
