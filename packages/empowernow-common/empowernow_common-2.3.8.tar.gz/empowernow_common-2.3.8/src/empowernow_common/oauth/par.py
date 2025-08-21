"""
🛡️ PAR (Pushed Authorization Requests) Module - RFC 9126

Comprehensive PAR implementation with:
- Secure request object creation
- PKCE challenge generation (S256/plain)
- Parameter validation and sanitization
- Authorization URL building
- Code exchange with PKCE verification

All implementations are production-ready and security-hardened.
"""

import base64
import hashlib
import json
import logging
import secrets
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from .security import (
    SecurityError,
    validate_url_security,
    sanitize_string_input,
    MAX_SCOPE_LENGTH,
)
from ..exceptions import OAuthError

logger = logging.getLogger(__name__)


class PARError(OAuthError):
    """PAR-specific errors"""

    pass


@dataclass
class PARRequest:
    """🛡️ Secure Pushed Authorization Request"""

    client_id: str
    redirect_uri: str
    response_type: str = "code"
    scope: Optional[str] = None
    state: Optional[str] = None
    code_challenge: Optional[str] = None
    code_challenge_method: Optional[str] = None
    authorization_details: Optional[List[Dict[str, Any]]] = None

    # Additional security parameters
    nonce: Optional[str] = None
    max_age: Optional[int] = None
    acr_values: Optional[str] = None

    def __post_init__(self):
        """Validate PAR request parameters"""
        # Validate client_id
        self.client_id = sanitize_string_input(self.client_id, 256, "client_id")

        # Validate redirect_uri
        self.redirect_uri = validate_url_security(
            self.redirect_uri, context="redirect_uri"
        )

        # Validate response_type
        valid_response_types = {
            "code",
            "token",
            "id_token",
            "code token",
            "code id_token",
            "token id_token",
            "code token id_token",
        }
        if self.response_type not in valid_response_types:
            raise PARError(f"Invalid response_type: {self.response_type}")

        # Validate scope
        if self.scope:
            self.scope = sanitize_string_input(
                self.scope, MAX_SCOPE_LENGTH, "scope", allow_special_chars=True
            )

        # Validate state (PKCE)
        if self.state:
            if len(self.state) < 8 or len(self.state) > 128:
                raise PARError("State parameter must be 8-128 characters")
            self.state = sanitize_string_input(self.state, 128, "state")

        # Validate PKCE parameters
        if self.code_challenge:
            if self.code_challenge_method not in ["S256", "plain"]:
                raise PARError("Invalid code_challenge_method")
            if len(self.code_challenge) < 43 or len(self.code_challenge) > 128:
                raise PARError("Invalid code_challenge length")

        # Validate nonce
        if self.nonce:
            self.nonce = sanitize_string_input(self.nonce, 64, "nonce")

        # Validate max_age
        if self.max_age is not None:
            if not isinstance(self.max_age, int) or self.max_age < 0:
                raise PARError("Invalid max_age value")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for request payload"""
        data = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": self.response_type,
        }

        if self.scope:
            data["scope"] = self.scope
        if self.state:
            data["state"] = self.state
        if self.code_challenge:
            data["code_challenge"] = self.code_challenge
            data["code_challenge_method"] = self.code_challenge_method
        if self.nonce:
            data["nonce"] = self.nonce
        if self.max_age is not None:
            data["max_age"] = str(self.max_age)
        if self.acr_values:
            data["acr_values"] = self.acr_values

        # Add authorization details if present
        if self.authorization_details:
            data["authorization_details"] = json.dumps(self.authorization_details)

        return data


@dataclass
class PARResponse:
    """🛡️ Secure PAR response"""

    request_uri: str
    expires_in: int

    def __post_init__(self):
        """Validate PAR response"""
        # Validate request_uri format (RFC 9126)
        if not self.request_uri.startswith("urn:"):
            raise PARError("Invalid request_uri format")

        # Validate expires_in
        if not isinstance(self.expires_in, int) or self.expires_in <= 0:
            raise PARError("Invalid expires_in value")

        # Request URI should be reasonable length
        if len(self.request_uri) > 512:
            raise PARError("Request URI too long")

    @property
    def is_expired(self) -> bool:
        """Check if PAR request has expired (would need timestamp tracking)"""
        # In production, you'd track creation time
        return False


def generate_pkce_challenge(method: str = "S256") -> Tuple[str, str]:
    """
    🛡️ Generate secure PKCE challenge pair

    Args:
        method: Challenge method (S256 or plain)

    Returns:
        Tuple[str, str]: (code_verifier, code_challenge)

    Raises:
        PARError: If generation fails
    """
    if method not in ["S256", "plain"]:
        raise PARError(f"Unsupported PKCE method: {method}")

    # Generate secure code verifier (RFC 7636)
    # 43-128 characters, URL-safe
    verifier_bytes = secrets.token_urlsafe(32)  # 43 characters
    code_verifier = verifier_bytes

    if method == "S256":
        # SHA256 hash and base64url encode
        verifier_hash = hashlib.sha256(code_verifier.encode("ascii")).digest()
        code_challenge = (
            base64.urlsafe_b64encode(verifier_hash).decode("ascii").rstrip("=")
        )
    else:  # plain
        code_challenge = code_verifier

    return code_verifier, code_challenge


class PARManager:
    """🛡️ PAR management for OAuth clients"""

    def __init__(self):
        """Initialize PAR manager"""
        self._pkce_verifiers: Dict[str, str] = {}  # state -> verifier mapping

    def create_par_request(
        self,
        client_id: str,
        redirect_uri: str,
        scope: Optional[str] = None,
        state: Optional[str] = None,
        authorization_details: Optional[List[Dict[str, Any]]] = None,
        enable_pkce: bool = True,
        **kwargs,
    ) -> Tuple[PARRequest, Optional[str]]:
        """
        Create PAR request with optional PKCE

        Args:
            client_id: OAuth client ID
            redirect_uri: OAuth redirect URI
            scope: OAuth scope
            state: OAuth state parameter
            authorization_details: RAR authorization details
            enable_pkce: Whether to enable PKCE
            **kwargs: Additional parameters

        Returns:
            Tuple[PARRequest, Optional[str]]: (par_request, code_verifier)
        """
        # Generate state if not provided
        if not state:
            state = secrets.token_urlsafe(32)

        # Generate PKCE challenge if enabled
        code_verifier = None
        code_challenge = None
        code_challenge_method = None

        if enable_pkce:
            code_verifier, code_challenge = generate_pkce_challenge("S256")
            code_challenge_method = "S256"

            # Store verifier for later use
            self._pkce_verifiers[state] = code_verifier

        # Create PAR request
        par_request = PARRequest(
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            authorization_details=authorization_details,
            **kwargs,
        )

        return par_request, code_verifier

    def build_authorization_url(
        self, authorization_url: str, client_id: str, request_uri: str, **kwargs
    ) -> str:
        """
        Build authorization URL using PAR request URI

        Args:
            authorization_url: Base authorization URL
            client_id: OAuth client ID
            request_uri: PAR request URI
            **kwargs: Additional parameters

        Returns:
            str: Authorization URL
        """
        # Validate authorization URL
        validate_url_security(authorization_url, context="authorization_url")

        # Build authorization URL with request_uri
        params = {"client_id": client_id, "request_uri": request_uri}

        # Add any additional parameters
        for key, value in kwargs.items():
            if value is not None:
                params[key] = str(value)

        # URL encode parameters
        from urllib.parse import urlencode

        query_string = urlencode(params)

        authorization_url_final = f"{authorization_url}?{query_string}"

        # Validate final URL
        validate_url_security(authorization_url_final, context="authorization_url")

        return authorization_url_final

    def get_pkce_verifier(self, state: str) -> Optional[str]:
        """
        Get PKCE verifier for state

        Args:
            state: OAuth state parameter

        Returns:
            Optional[str]: PKCE verifier if found
        """
        return self._pkce_verifiers.get(state)

    def consume_pkce_verifier(self, state: str) -> Optional[str]:
        """
        Get and remove PKCE verifier for state

        Args:
            state: OAuth state parameter

        Returns:
            Optional[str]: PKCE verifier if found
        """
        return self._pkce_verifiers.pop(state, None)

    def validate_authorization_code_params(
        self, authorization_code: str, state: str, redirect_uri: str
    ) -> Dict[str, str]:
        """
        Validate authorization code exchange parameters

        Args:
            authorization_code: Authorization code from callback
            state: State parameter from callback
            redirect_uri: Original redirect URI

        Returns:
            Dict[str, str]: Validated parameters for token exchange
        """
        # Validate inputs
        authorization_code = sanitize_string_input(
            authorization_code, 512, "authorization_code"
        )
        state = sanitize_string_input(state, 128, "state")
        redirect_uri = validate_url_security(redirect_uri, context="redirect_uri")

        # Prepare token request parameters
        token_params = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": redirect_uri,
        }

        # Add PKCE verifier if available
        code_verifier = self.consume_pkce_verifier(state)
        if code_verifier:
            token_params["code_verifier"] = code_verifier
            logger.debug("🛡️ PKCE verifier added to token exchange")

        return token_params


class PKCEManager:
    """🛡️ PKCE (Proof Key for Code Exchange) utility"""

    @staticmethod
    def generate_challenge_pair(method: str = "S256") -> Tuple[str, str]:
        """
        Generate PKCE challenge pair

        Args:
            method: Challenge method (S256 or plain)

        Returns:
            Tuple[str, str]: (code_verifier, code_challenge)
        """
        return generate_pkce_challenge(method)

    @staticmethod
    def validate_verifier(verifier: str, challenge: str, method: str = "S256") -> bool:
        """
        Validate PKCE verifier against challenge

        Args:
            verifier: Code verifier
            challenge: Code challenge
            method: Challenge method

        Returns:
            bool: True if verifier is valid
        """
        try:
            if method == "S256":
                # SHA256 hash and base64url encode
                verifier_hash = hashlib.sha256(verifier.encode("ascii")).digest()
                computed_challenge = (
                    base64.urlsafe_b64encode(verifier_hash).decode("ascii").rstrip("=")
                )
                return computed_challenge == challenge
            elif method == "plain":
                return verifier == challenge
            else:
                return False
        except Exception:
            return False
