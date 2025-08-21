"""Synchronous façade around :class:`~empowernow_common.oauth.client.HardenedOAuth`.

Prefer async usage for new applications, but many legacy code-bases are still
fully synchronous.  `SyncOAuth` wraps the async client and converts calls via
``anyio.run`` so the rest of the SDK can remain async-first.

Only the most common operations are exposed; niche flows (PAR, JARM, …) remain
async-only and must be called on ``.async_client`` if needed.
"""

from __future__ import annotations

import anyio
from typing import Any, Dict, Optional

from .client import HardenedOAuth, SecureOAuthConfig, HardenedToken

__all__ = ["SyncOAuth"]


class SyncOAuth:
    """Blocking wrapper around :class:`HardenedOAuth`."""

    def __init__(self, config: SecureOAuthConfig, **kwargs: Any):
        self._async = HardenedOAuth(config, **kwargs)

    # Expose underlying async client for advanced use-cases
    @property
    def async_client(self) -> HardenedOAuth:  # noqa: D401 – property
        return self._async

    # ------------------------------------------------------------------
    # Token operations
    # ------------------------------------------------------------------

    def get_token(self, **params) -> HardenedToken:  # noqa: D401
        return anyio.run(lambda: self._async._secure_request_token(**params))

    def introspect(self, token: str) -> Dict[str, Any]:
        return anyio.run(self._async.introspect_token, token)

    def revoke(self, token: str, token_type_hint: str = "access_token") -> None:
        return anyio.run(self._async.revoke_token, token, token_type_hint)

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------

    def close(self) -> None:
        anyio.run(self._async.aclose) 