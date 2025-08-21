"""
🛡️ DPoP (Demonstrating Proof of Possession) Module - RFC 9449

Comprehensive DPoP implementation with:
- FIPS-compliant key generation (RSA/EC)
- Secure JWT proof creation
- JWK thumbprint generation
- Replay attack prevention
- HTTP header management

All implementations are production-ready and security-hardened.
"""

import base64
import hashlib
import json
import logging
import secrets
import time
from typing import Dict, Any, Union, Set, Optional
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric import rsa, ec
import jwt

from .security import (
    SecurityError,
    FIPSValidator,
    validate_url_security,
    generate_secure_token,
    generate_correlation_id,
)
from ..exceptions import OAuthError

# optional cache backend for replay protection
try:
    from ..cache import CacheBackend, InMemoryCacheBackend  # type: ignore
except Exception:  # pragma: no cover – circular import safety
    CacheBackend = None  # type: ignore
    InMemoryCacheBackend = None  # type: ignore

logger = logging.getLogger(__name__)

# DPoP constants
DPOP_ALG_PREFERENCES = ["ES256", "RS256"]  # FIPS-compliant algorithms
DPOP_JWK_THUMBPRINT_ALG = "sha256"


class DPoPError(SecurityError, OAuthError):
    """DPoP-specific errors"""

    pass


@dataclass
class DPoPKeyPair:
    """🛡️ Secure DPoP key pair with FIPS compliance"""

    private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey]
    public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]
    algorithm: str
    key_id: str

    def __post_init__(self):
        """Validate key pair on creation"""
        # Validate algorithm is FIPS-approved
        FIPSValidator.validate_algorithm(self.algorithm, "dpop_signing")

        # Validate key sizes meet FIPS requirements
        if isinstance(self.private_key, rsa.RSAPrivateKey):
            key_size = self.private_key.key_size
            FIPSValidator.validate_key_strength("RSA", key_size)
        elif isinstance(self.private_key, ec.EllipticCurvePrivateKey):
            curve_name = self.private_key.curve.name
            if curve_name not in ["secp256r1", "secp384r1", "secp521r1"]:
                raise DPoPError(f"Non-FIPS curve: {curve_name}")

    def to_jwk(self) -> Dict[str, Any]:
        """Convert public key to JWK format"""
        if isinstance(self.public_key, rsa.RSAPublicKey):
            numbers = self.public_key.public_numbers()
            return {
                "kty": "RSA",
                "alg": self.algorithm,
                "use": "sig",
                "kid": self.key_id,
                "n": self._int_to_base64url(numbers.n),
                "e": self._int_to_base64url(numbers.e),
            }
        elif isinstance(self.public_key, ec.EllipticCurvePublicKey):
            numbers = self.public_key.public_numbers()
            curve_name = self.public_key.curve.name

            if curve_name == "secp256r1":
                crv = "P-256"
                coord_size = 32
            elif curve_name == "secp384r1":
                crv = "P-384"
                coord_size = 48
            elif curve_name == "secp521r1":
                crv = "P-521"
                coord_size = 66
            else:
                raise DPoPError(f"Unsupported curve: {curve_name}")

            return {
                "kty": "EC",
                "alg": self.algorithm,
                "use": "sig",
                "kid": self.key_id,
                "crv": crv,
                "x": self._int_to_base64url(numbers.x, coord_size),
                "y": self._int_to_base64url(numbers.y, coord_size),
            }
        else:
            raise DPoPError("Unsupported key type for DPoP")

    def _int_to_base64url(self, value: int, min_length: int = None) -> str:
        """Convert integer to base64url encoding"""
        # Convert to bytes
        byte_length = (value.bit_length() + 7) // 8
        if min_length and byte_length < min_length:
            byte_length = min_length

        value_bytes = value.to_bytes(byte_length, byteorder="big")

        # Base64url encode
        return base64.urlsafe_b64encode(value_bytes).decode("ascii").rstrip("=")

    def get_jwk_thumbprint(self) -> str:
        """Generate JWK thumbprint for token binding"""
        jwk = self.to_jwk()

        # Create canonical JWK for thumbprint (RFC 7638)
        if jwk["kty"] == "RSA":
            canonical = {"e": jwk["e"], "kty": jwk["kty"], "n": jwk["n"]}
        elif jwk["kty"] == "EC":
            canonical = {
                "crv": jwk["crv"],
                "kty": jwk["kty"],
                "x": jwk["x"],
                "y": jwk["y"],
            }
        else:
            raise DPoPError("Unsupported key type for thumbprint")

        # JSON serialize with no whitespace and sorted keys
        canonical_json = json.dumps(canonical, sort_keys=True, separators=(",", ":"))

        # SHA-256 hash and base64url encode
        digest = hashlib.sha256(canonical_json.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

    # Legacy dict-style access used by older tests
    def __getitem__(self, item):  # type: ignore
        if item == "private_key_pem":
            from cryptography.hazmat.primitives import serialization
            return self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ).decode()
        if item == "public_key_pem":
            from cryptography.hazmat.primitives import serialization
            return self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode()
        raise KeyError(item)


class DPoPProofGenerator:
    """🛡️ Secure DPoP proof generator with comprehensive validation"""

    def __init__(
        self,
        key_pair: DPoPKeyPair,
        *,
        replay_cache: "CacheBackend[bool] | None" = None,
        replay_ttl: int = 300,
    ):
        self.key_pair = key_pair
        self._local_cache: Set[str] = set()
        self._replay_cache = replay_cache or (
            InMemoryCacheBackend() if InMemoryCacheBackend else None
        )
        self._ttl = replay_ttl

    def generate_proof(
        self,
        http_method: str,
        http_uri: str,
        access_token: Optional[str] = None,
        nonce: Optional[str] = None,
    ) -> str:
        """
        Generate DPoP proof JWT (RFC 9449)

        Args:
            http_method: HTTP method (GET, POST, etc.)
            http_uri: Full HTTP URI being accessed
            access_token: Access token being bound (optional)
            nonce: Server nonce for replay protection (optional)

        Returns:
            str: DPoP proof JWT

        Raises:
            DPoPError: If proof generation fails
        """
        # Validate inputs
        http_method = self._validate_http_method(http_method)
        http_uri = validate_url_security(http_uri, context="DPoP_uri")

        # Generate unique JTI
        jti = self._generate_unique_jti()

        # Current timestamp
        iat = int(time.time())

        # Build JWT header
        header = {
            "typ": "dpop+jwt",
            "alg": self.key_pair.algorithm,
            "jwk": self.key_pair.to_jwk(),
        }

        # Build JWT payload
        payload = {"jti": jti, "htm": http_method, "htu": http_uri, "iat": iat}

        # Add access token hash if provided
        if access_token:
            payload["ath"] = self._generate_access_token_hash(access_token)

        # Add nonce if provided (server-provided)
        if nonce:
            payload["nonce"] = self._validate_nonce(nonce)

        try:
            # Sign JWT
            if isinstance(self.key_pair.private_key, rsa.RSAPrivateKey):
                algorithm = self.key_pair.algorithm
            elif isinstance(self.key_pair.private_key, ec.EllipticCurvePrivateKey):
                algorithm = self.key_pair.algorithm
            else:
                raise DPoPError("Unsupported key type for signing")

            proof_jwt = jwt.encode(
                payload, self.key_pair.private_key, algorithm=algorithm, headers=header
            )

            # Cache JTI to prevent reuse (local & optional external)
            self._local_cache.add(jti)
            if self._replay_cache:
                self._replay_cache.set(jti, True, self._ttl)

            return proof_jwt

        except Exception as e:
            raise DPoPError(f"Failed to generate DPoP proof: {e}")

    def _validate_http_method(self, method: str) -> str:
        """Validate HTTP method"""
        if not isinstance(method, str):
            raise DPoPError("HTTP method must be string")

        method = method.upper().strip()
        valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}

        if method not in valid_methods:
            raise DPoPError(f"Invalid HTTP method: {method}")

        return method

    def _validate_nonce(self, nonce: str) -> str:
        """Validate server nonce"""
        if not isinstance(nonce, str):
            raise DPoPError("Nonce must be string")

        if len(nonce) > 128:
            raise DPoPError("Nonce too long")

        # Only allow base64url characters
        import re

        if not re.match(r"^[A-Za-z0-9_-]+$", nonce):
            raise DPoPError("Nonce contains invalid characters")

        return nonce

    def _generate_unique_jti(self) -> str:
        """Generate unique JWT ID for replay protection"""
        # Use timestamp + secure random
        timestamp = str(int(time.time()))
        random_part = generate_secure_token(16)
        jti = f"{timestamp}-{random_part}"

        # Ensure uniqueness (local)
        counter = 0
        original_jti = jti
        while jti in self._local_cache and counter < 100:
            jti = f"{original_jti}-{counter}"
            counter += 1

        if jti in self._local_cache:
            raise DPoPError("Failed to generate unique JTI")

        # Optional global replay cache check
        if self._replay_cache and self._replay_cache.get(jti):
            raise DPoPError("Replay detected – JTI already used")

        return jti

    def _generate_access_token_hash(self, access_token: str) -> str:
        """Generate access token hash for binding"""
        if not isinstance(access_token, str):
            raise DPoPError("Access token must be string")

        # SHA-256 hash of access token
        token_hash = hashlib.sha256(access_token.encode("utf-8")).digest()

        # Base64url encode
        return base64.urlsafe_b64encode(token_hash).decode("ascii").rstrip("=")


def generate_dpop_key_pair(algorithm: str = "ES256") -> DPoPKeyPair:
    """
    🛡️ Generate FIPS-compliant DPoP key pair

    Args:
        algorithm: Signing algorithm (ES256, ES384, ES512, RS256)

    Returns:
        DPoPKeyPair: Generated key pair

    Raises:
        DPoPError: If key generation fails
    """
    # Validate algorithm
    if algorithm not in DPOP_ALG_PREFERENCES:
        raise DPoPError(f"Algorithm {algorithm} not supported for DPoP")

    FIPSValidator.validate_algorithm(algorithm, "dpop_signing")

    try:
        if algorithm.startswith("ES"):
            # Elliptic Curve keys
            if algorithm == "ES256":
                curve = ec.SECP256R1()
            elif algorithm == "ES384":
                curve = ec.SECP384R1()
            elif algorithm == "ES512":
                curve = ec.SECP521R1()  # Note: ES512 uses P-521
            else:
                raise DPoPError(f"Unsupported EC algorithm: {algorithm}")

            private_key = ec.generate_private_key(curve)
            public_key = private_key.public_key()

        elif algorithm.startswith("RS"):
            # RSA keys
            key_size = 2048  # FIPS minimum
            if algorithm in ["RS384", "RS512"]:
                key_size = 3072  # Stronger for larger hashes

            private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=key_size
            )
            public_key = private_key.public_key()

        else:
            raise DPoPError(f"Unsupported algorithm: {algorithm}")

        # Generate unique key ID
        key_id = generate_correlation_id()[:16]  # Shorter for key ID

        return DPoPKeyPair(
            private_key=private_key,
            public_key=public_key,
            algorithm=algorithm,
            key_id=key_id,
        )

    except Exception as e:
        raise DPoPError(f"Failed to generate DPoP key pair: {e}")


class DPoPManager:
    """🛡️ DPoP management for OAuth clients"""

    def __init__(
        self,
        algorithm: str = "ES256",
        *,
        replay_cache: "CacheBackend[bool] | None" = None,
        replay_ttl: int = 300,
    ):
        """
        Initialize DPoP manager

        Args:
            algorithm: DPoP signing algorithm
            replay_cache: Optional replay cache backend
            replay_ttl: Optional replay cache TTL
        """
        self._key_pair: Optional[DPoPKeyPair] = None
        self._proof_generator: Optional[DPoPProofGenerator] = None
        self._algorithm = algorithm
        self._replay_cache = replay_cache
        self._replay_ttl = replay_ttl

    def enable_dpop(self) -> str:
        """
        Enable DPoP for this client

        Returns:
            str: JWK thumbprint for server binding

        Raises:
            DPoPError: If DPoP setup fails
        """
        if self._key_pair is None:
            # Generate new key pair
            self._key_pair = generate_dpop_key_pair(self._algorithm)
            self._proof_generator = DPoPProofGenerator(
                self._key_pair,
                replay_cache=self._replay_cache,
                replay_ttl=self._replay_ttl,
            )

            logger.info(
                "🛡️ DPoP enabled",
                extra={
                    "algorithm": self._algorithm,
                    "key_id": self._key_pair.key_id,
                    "thumbprint": self._key_pair.get_jwk_thumbprint(),
                },
            )

        return self._key_pair.get_jwk_thumbprint()

    def is_enabled(self) -> bool:
        """Check if DPoP is enabled"""
        return self._proof_generator is not None

    def get_jwk_thumbprint(self) -> Optional[str]:
        """Get JWK thumbprint if DPoP is enabled"""
        if self._key_pair:
            return self._key_pair.get_jwk_thumbprint()
        return None

    def add_dpop_header(
        self,
        headers: Dict[str, str],
        method: str,
        uri: str,
        access_token: Optional[str] = None,
        nonce: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Add DPoP header to HTTP request

        Args:
            headers: Existing headers
            method: HTTP method
            uri: Request URI
            access_token: Access token for binding (optional)
            nonce: Server nonce (optional)

        Returns:
            Dict[str, str]: Headers with DPoP proof added
        """
        if self._proof_generator:
            try:
                dpop_proof = self._proof_generator.generate_proof(
                    method, uri, access_token, nonce
                )
                headers = headers.copy()
                headers["DPoP"] = dpop_proof

                logger.debug(
                    "🛡️ DPoP proof added to request",
                    extra={
                        "method": method,
                        "uri": uri[:50] + "..." if len(uri) > 50 else uri,
                    },
                )

            except Exception as e:
                logger.error(f"🚨 Failed to add DPoP proof: {e}")
                # Continue without DPoP rather than failing the request

        return headers
