"""empowernow_common.client – Async-first friendly façade

This sub-package is the modern, minimal surface replacing the former
1 500-line `simple.py`.  It intentionally exposes only a handful of
operations and delegates all heavy-lifting to `empowernow_common.oauth`
modules.  Power-users can still reach the full feature set via the
lower-level packages (oauth.*, authzen.*, etc.).

Road-map
────────
* 2024-Q2:  Provide token acquisition & PAR/RAR helpers (this file).
* 2024-Q3:  Uplift to complete RFC coverage then deprecate `simple.py`.
"""

from __future__ import annotations

import logging
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from ..oauth.client import (
    HardenedOAuth,
    SecureOAuthConfig,
    HardenedToken,
    PARResponse,
    SecureAuthorizationDetail,
)

logger = logging.getLogger(__name__)

# avoid heavy optional deps at runtime; only import for type checkers
if TYPE_CHECKING:
    from ..cache import CacheBackend, InMemoryCacheBackend, RedisCacheBackend
else:
    from ..cache import InMemoryCacheBackend, CacheBackend  # runtime for default cache


class OAuthClient:
    """Async-first thin wrapper around :class:`HardenedOAuth`."""

    def __init__(
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
        authorization_url: str,
        *,
        scope: str | None = None,
        par_endpoint: str | None = None,
        ciba_endpoint: str | None = None,
        introspection_url: str | None = None,
        revocation_url: str | None = None,
        user_agent: str = "EmpowerNow-OAuthClient/1.0",
        cache_backend: "CacheBackend[Any]" | None = None,
    ) -> None:
        cfg = SecureOAuthConfig(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            authorization_url=authorization_url,
            scope=scope,
            par_endpoint=par_endpoint,
            ciba_endpoint=ciba_endpoint,
            introspection_url=introspection_url,
            revocation_url=revocation_url,
        )
        self._backend = HardenedOAuth(cfg, user_agent=user_agent)
        logger.debug("OAuthClient initialised", extra={"client_id": client_id})

        self._cache: CacheBackend[Any] = cache_backend or InMemoryCacheBackend()

    # ---------------------------------------------------------------------
    # Basic token
    # ---------------------------------------------------------------------

    async def get_token(self) -> HardenedToken:
        """Return an access-token using the **client_credentials** grant."""
        cache_key = "token:client_credentials"
        cached: HardenedToken | None = self._cache.get(cache_key)
        if cached and not cached.is_expired():
            return cached

        token = await self._backend._secure_request_token()  # type: ignore  # internal call

        # store with TTL slightly shorter than actual expiry to avoid edge cases
        ttl = max(30, (token.expires_in or 3600) - 60)
        self._cache.set(cache_key, token, ttl)
        return token

    # ---------------------------------------------------------------------
    # PAR + Authorization helpers
    # ---------------------------------------------------------------------

    async def create_authorization_url(
        self,
        redirect_uri: str,
        *,
        scope: str | None = None,
        authorization_details: Optional[List[SecureAuthorizationDetail]] = None,
    ) -> str:
        """High-level helper that performs PAR then returns the auth URL."""
        par_resp: PARResponse = await self._backend.create_par_request(
            redirect_uri=redirect_uri,
            scope=scope,
            authorization_details=authorization_details,
        )
        return self._backend.build_authorization_url(par_resp)

    # ---------------------------------------------------------------------
    # Convenience DPoP
    # ---------------------------------------------------------------------

    def enable_dpop(self) -> str:
        """Generate and register a DPoP key-pair; returns public-JWK thumbprint."""
        return self._backend.enable_dpop()

    # ---------------------------------------------------------------------
    # Pass-through helpers for advanced flows as the façade expands
    # ---------------------------------------------------------------------

    def backend(self) -> HardenedOAuth:  # advanced users escape-hatch
        return self._backend

    # ------------------------------------------------------------------
    # Revocation helper (security-hardening 4.2)
    # ------------------------------------------------------------------

    async def revoke_cached_token(self) -> None:
        """Revoke the currently cached client-credentials token, if any.

        If no token is cached the call is a no-op.  After a successful
        revocation the cache entry is removed to force a fresh token on the
        next call.
        """

        cache_key = "token:client_credentials"
        token: HardenedToken | None = self._cache.get(cache_key)

        if not token:
            return  # nothing to revoke

        try:
            await self._backend.revoke_token(token.access_token)
        finally:
            self._cache.delete(cache_key)


# ---------------------------------------------------------------------
# Optional sync wrapper – runs coroutines via anyio (item 3.2)
# ---------------------------------------------------------------------


class SyncOAuthClient:
    """Synchronous wrapper around :class:`OAuthClient` using *anyio* helpers.

    Intended for quick scripts or legacy code that isn't async-aware.  Each
    call spins a short-lived event-loop via `anyio.run()`.  Heavy users should
    adopt the async API for throughput.
    """

    def __init__(self, *args, **kwargs):
        self._async = OAuthClient(*args, **kwargs)

    # -----------------------------------------------------------
    # Token helpers
    # -----------------------------------------------------------

    def get_token(self) -> HardenedToken:
        import anyio

        return anyio.run(self._async.get_token)

    # -----------------------------------------------------------
    # Authorization helpers (PAR)
    # -----------------------------------------------------------

    def create_authorization_url(
        self,
        redirect_uri: str,
        *,
        scope: str | None = None,
        authorization_details: Optional[List[SecureAuthorizationDetail]] = None,
    ) -> str:
        import anyio

        return anyio.run(
            self._async.create_authorization_url,
            redirect_uri,
            scope=scope,
            authorization_details=authorization_details,
        )

    # -----------------------------------------------------------
    # DPoP passthrough
    # -----------------------------------------------------------

    def enable_dpop(self) -> str:  # sync already
        return self._async.enable_dpop()

    # Advanced escape-hatch
    def backend(self) -> HardenedOAuth:
        return self._async.backend()


# ---------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------

__all__ = [
    "OAuthClient",
    "SyncOAuthClient",
]
