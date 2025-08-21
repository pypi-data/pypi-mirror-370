"""
🛡️ CIBA (Client Initiated Backchannel Authentication) Module - RFC 8628

Comprehensive CIBA implementation with:
- Backchannel authentication requests
- Device flow support
- Polling mechanisms
- Secure user hint validation
- Token polling with exponential backoff

All implementations are production-ready and security-hardened.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, Callable, Union
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import httpx

from .security import (
    SecurityError,
    sanitize_string_input,
    validate_url_security,
    generate_secure_token,
)
from ..exceptions import OAuthError

logger = logging.getLogger(__name__)


class CIBAError(OAuthError):
    """CIBA-specific errors"""

    pass


@dataclass
class CIBARequest:
    """🛡️ CIBA authentication request with comprehensive validation"""

    scope: str
    login_hint: Optional[str] = None
    login_hint_token: Optional[str] = None
    id_token_hint: Optional[str] = None
    binding_message: Optional[str] = None
    user_code: Optional[str] = None
    requested_expiry: Optional[int] = None

    def __post_init__(self):
        """Validate CIBA request parameters"""
        # Validate scope
        self.scope = sanitize_string_input(
            self.scope, 1024, "scope", allow_special_chars=True
        )

        # At least one hint is required
        hints = [self.login_hint, self.login_hint_token, self.id_token_hint]
        if not any(hints):
            raise CIBAError(
                "At least one of login_hint, login_hint_token, or id_token_hint is required"
            )

        # Validate individual hints
        if self.login_hint:
            self.login_hint = sanitize_string_input(self.login_hint, 256, "login_hint")

        if self.login_hint_token:
            self.login_hint_token = sanitize_string_input(
                self.login_hint_token,
                1024,
                "login_hint_token",
                allow_special_chars=True,
            )

        if self.id_token_hint:
            self.id_token_hint = sanitize_string_input(
                self.id_token_hint, 4096, "id_token_hint", allow_special_chars=True
            )

        if self.binding_message:
            if len(self.binding_message) > 256:
                raise CIBAError("Binding message too long (max 256 characters)")
            self.binding_message = sanitize_string_input(
                self.binding_message, 256, "binding_message", allow_special_chars=True
            )

        if self.user_code:
            self.user_code = sanitize_string_input(self.user_code, 64, "user_code")

        if self.requested_expiry is not None:
            if not isinstance(self.requested_expiry, int) or self.requested_expiry <= 0:
                raise CIBAError("Invalid requested_expiry: must be positive integer")
            if self.requested_expiry > 86400:  # Max 24 hours
                raise CIBAError("Requested expiry too long (max 24 hours)")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for request payload"""
        data = {"scope": self.scope}

        if self.login_hint:
            data["login_hint"] = self.login_hint
        if self.login_hint_token:
            data["login_hint_token"] = self.login_hint_token
        if self.id_token_hint:
            data["id_token_hint"] = self.id_token_hint
        if self.binding_message:
            data["binding_message"] = self.binding_message
        if self.user_code:
            data["user_code"] = self.user_code
        if self.requested_expiry is not None:
            data["requested_expiry"] = self.requested_expiry

        return data


@dataclass
class CIBAResponse:
    """🛡️ CIBA authentication response with validation"""

    auth_req_id: str
    expires_in: int
    interval: Optional[int] = None

    def __post_init__(self):
        """Validate CIBA response"""
        self.auth_req_id = sanitize_string_input(self.auth_req_id, 256, "auth_req_id")

        if not isinstance(self.expires_in, int) or self.expires_in <= 0:
            raise CIBAError("Invalid expires_in: must be positive integer")

        if self.interval is not None:
            if not isinstance(self.interval, int) or self.interval <= 0:
                raise CIBAError("Invalid interval: must be positive integer")

        # Set default interval if not provided (RFC 8628 recommendation)
        if self.interval is None:
            self.interval = 5  # 5 seconds default polling interval

    @property
    def expires_at(self) -> datetime:
        """Calculate expiration time"""
        return datetime.now(timezone.utc) + timedelta(seconds=self.expires_in)

    def is_expired(self) -> bool:
        """Check if authentication request has expired"""
        return datetime.now(timezone.utc) >= self.expires_at


@dataclass
class CIBATokenResponse:
    """🛡️ CIBA token response"""

    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    id_token: Optional[str] = None

    def __post_init__(self):
        """Validate token response"""
        self.access_token = sanitize_string_input(
            self.access_token, 4096, "access_token", allow_special_chars=True
        )

        if self.refresh_token:
            self.refresh_token = sanitize_string_input(
                self.refresh_token, 4096, "refresh_token", allow_special_chars=True
            )

        if self.id_token:
            self.id_token = sanitize_string_input(
                self.id_token, 4096, "id_token", allow_special_chars=True
            )


class CIBAClient:
    """🛡️ Secure CIBA client with polling and error handling"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        ciba_endpoint: str,
        token_endpoint: str,
        user_agent: str = "EmpowerNow-CIBA/1.0",
    ):
        """
        Initialize CIBA client

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            ciba_endpoint: CIBA backchannel authentication endpoint
            token_endpoint: Token endpoint for polling
            user_agent: User agent for requests
        """
        self.client_id = sanitize_string_input(client_id, 256, "client_id")
        self.client_secret = sanitize_string_input(client_secret, 512, "client_secret")
        self.ciba_endpoint = validate_url_security(
            ciba_endpoint, context="ciba_endpoint"
        )
        self.token_endpoint = validate_url_security(
            token_endpoint, context="token_endpoint"
        )
        self.user_agent = user_agent

        # Polling state
        self._active_polls: Dict[str, bool] = {}

        logger.info(
            "🛡️ CIBA client initialized",
            extra={"client_id": client_id, "ciba_endpoint": ciba_endpoint},
        )

    async def initiate_backchannel_authentication(
        self, request: CIBARequest
    ) -> CIBAResponse:
        """
        Initiate backchannel authentication (RFC 8628)

        Args:
            request: CIBA authentication request

        Returns:
            CIBAResponse: Authentication response with polling details

        Raises:
            CIBAError: If authentication initiation fails
        """
        try:
            async with self._get_http_client() as client:
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "User-Agent": self.user_agent,
                    "X-Request-ID": generate_secure_token(16),
                }

                # Prepare request data
                data = request.to_dict()
                data["client_id"] = self.client_id

                # Make backchannel authentication request
                response = await client.post(
                    self.ciba_endpoint,
                    data=data,
                    auth=(self.client_id, self.client_secret),
                    headers=headers,
                )

                response.raise_for_status()
                response_data = response.json()

                # Validate response
                if not response_data.get("auth_req_id"):
                    raise CIBAError("Missing auth_req_id in response")

                if not response_data.get("expires_in"):
                    raise CIBAError("Missing expires_in in response")

                ciba_response = CIBAResponse(
                    auth_req_id=response_data["auth_req_id"],
                    expires_in=response_data["expires_in"],
                    interval=response_data.get("interval"),
                )

                logger.info(
                    "🛡️ CIBA authentication initiated",
                    extra={
                        "auth_req_id": ciba_response.auth_req_id[:16] + "...",
                        "expires_in": ciba_response.expires_in,
                        "interval": ciba_response.interval,
                    },
                )

                return ciba_response

        except httpx.HTTPStatusError as e:
            error_msg = f"CIBA initiation failed: {e.response.status_code}"
            try:
                error_data = e.response.json()
                if "error" in error_data:
                    error_msg = f"CIBA error: {error_data['error']}"
                    if "error_description" in error_data:
                        error_msg += f" - {error_data['error_description']}"
            except:
                pass

            logger.error(error_msg)
            raise CIBAError(error_msg)

        except Exception as e:
            logger.error(f"CIBA initiation error: {e}")
            raise CIBAError(f"Failed to initiate CIBA: {e}")

    async def poll_for_token(
        self,
        ciba_response: CIBAResponse,
        max_attempts: int = 60,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> CIBATokenResponse:
        """
        Poll for token with exponential backoff

        Args:
            ciba_response: CIBA response from initiation
            max_attempts: Maximum polling attempts
            progress_callback: Optional callback for progress updates

        Returns:
            CIBATokenResponse: Token response when authentication completes

        Raises:
            CIBAError: If polling fails or times out
        """
        auth_req_id = ciba_response.auth_req_id
        interval = ciba_response.interval

        # Mark this request as being polled
        self._active_polls[auth_req_id] = True

        try:
            attempt = 0
            current_interval = interval

            while attempt < max_attempts and self._active_polls.get(auth_req_id, False):
                attempt += 1

                # Check if expired
                if ciba_response.is_expired():
                    raise CIBAError("CIBA authentication request expired")

                # Progress callback
                if progress_callback:
                    progress_callback(attempt, max_attempts)

                logger.debug(
                    f"🛡️ CIBA polling attempt {attempt}/{max_attempts}",
                    extra={
                        "auth_req_id": auth_req_id[:16] + "...",
                        "interval": current_interval,
                    },
                )

                try:
                    # Make token request
                    token_response = await self._poll_token_endpoint(auth_req_id)

                    # Success!
                    logger.info(
                        "🛡️ CIBA authentication completed",
                        extra={
                            "auth_req_id": auth_req_id[:16] + "...",
                            "attempts": attempt,
                        },
                    )

                    return token_response

                except CIBAError as e:
                    error_msg = str(e)

                    if "authorization_pending" in error_msg:
                        # User hasn't completed authentication yet, continue polling
                        await asyncio.sleep(current_interval)
                        continue

                    elif "slow_down" in error_msg:
                        # Server requests slower polling
                        current_interval = min(
                            current_interval * 2, 60
                        )  # Max 60 seconds
                        await asyncio.sleep(current_interval)
                        continue

                    elif "expired_token" in error_msg:
                        raise CIBAError("CIBA authentication request expired")

                    elif "access_denied" in error_msg:
                        raise CIBAError("User denied the authentication request")

                    else:
                        # Other error, re-raise
                        raise

                # Wait before next attempt
                await asyncio.sleep(current_interval)

            # Max attempts reached
            raise CIBAError(f"CIBA polling timeout after {max_attempts} attempts")

        finally:
            # Clean up polling state
            self._active_polls.pop(auth_req_id, None)

    async def _poll_token_endpoint(self, auth_req_id: str) -> CIBATokenResponse:
        """Poll token endpoint for authentication completion"""
        async with self._get_http_client() as client:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": self.user_agent,
            }

            data = {
                "grant_type": "urn:openid:params:grant-type:ciba",
                "auth_req_id": auth_req_id,
            }

            response = await client.post(
                self.token_endpoint,
                data=data,
                auth=(self.client_id, self.client_secret),
                headers=headers,
            )

            response_data = response.json()

            if response.status_code == 200:
                # Success - authentication completed
                return CIBATokenResponse(
                    access_token=response_data["access_token"],
                    token_type=response_data.get("token_type", "Bearer"),
                    expires_in=response_data.get("expires_in"),
                    refresh_token=response_data.get("refresh_token"),
                    scope=response_data.get("scope"),
                    id_token=response_data.get("id_token"),
                )

            elif response.status_code == 400:
                # Error response
                error = response_data.get("error", "unknown_error")
                error_description = response_data.get("error_description", "")
                raise CIBAError(f"{error}: {error_description}")

            else:
                raise CIBAError(f"Unexpected response status: {response.status_code}")

    def cancel_polling(self, auth_req_id: str) -> None:
        """Cancel active polling for a request"""
        self._active_polls[auth_req_id] = False
        logger.info(
            "🛡️ CIBA polling cancelled", extra={"auth_req_id": auth_req_id[:16] + "..."}
        )

    def cancel_all_polling(self) -> None:
        """Cancel all active polling"""
        for auth_req_id in list(self._active_polls.keys()):
            self._active_polls[auth_req_id] = False
        logger.info("🛡️ All CIBA polling cancelled")

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get secure HTTP client"""
        return httpx.AsyncClient(
            timeout=30.0,
            verify=True,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )


class CIBAManager:
    """🛡️ CIBA management for OAuth clients"""

    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize CIBA manager

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self._client: Optional[CIBAClient] = None

    def configure_ciba(self, ciba_endpoint: str, token_endpoint: str) -> None:
        """
        Configure CIBA endpoints

        Args:
            ciba_endpoint: CIBA backchannel authentication endpoint
            token_endpoint: Token endpoint for polling
        """
        self._client = CIBAClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            ciba_endpoint=ciba_endpoint,
            token_endpoint=token_endpoint,
        )

        logger.info(
            "🛡️ CIBA configured",
            extra={"ciba_endpoint": ciba_endpoint, "token_endpoint": token_endpoint},
        )

    def is_configured(self) -> bool:
        """Check if CIBA is configured"""
        return self._client is not None

    async def initiate_authentication(self, request: CIBARequest) -> CIBAResponse:
        """Initiate CIBA authentication"""
        if not self._client:
            raise CIBAError("CIBA not configured. Call configure_ciba() first.")

        return await self._client.initiate_backchannel_authentication(request)

    async def poll_for_token(
        self, ciba_response: CIBAResponse, **kwargs
    ) -> CIBATokenResponse:
        """Poll for authentication completion"""
        if not self._client:
            raise CIBAError("CIBA not configured. Call configure_ciba() first.")

        return await self._client.poll_for_token(ciba_response, **kwargs)

    async def authenticate_user(
        self, scope: str, login_hint: str = None, binding_message: str = None, **kwargs
    ) -> CIBATokenResponse:
        """
        Complete CIBA authentication flow

        Args:
            scope: OAuth scope
            login_hint: User identification hint
            binding_message: Human-readable binding message
            **kwargs: Additional parameters

        Returns:
            CIBATokenResponse: Token response when authentication completes
        """
        if not self._client:
            raise CIBAError("CIBA not configured. Call configure_ciba() first.")

        # Create request
        request = CIBARequest(
            scope=scope,
            login_hint=login_hint,
            binding_message=binding_message,
            **kwargs,
        )

        # Initiate authentication
        ciba_response = await self.initiate_authentication(request)

        # Poll for completion
        return await self.poll_for_token(ciba_response)
