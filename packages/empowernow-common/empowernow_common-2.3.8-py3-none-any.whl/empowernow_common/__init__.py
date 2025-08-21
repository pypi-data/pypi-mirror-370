"""
🚀 EmpowerNow Common Package

The world's most comprehensive identity and security library for Python.
Supporting advanced OAuth 2.0/2.1, AuthZEN, FIPS compliance, and more.

Quick Start:
    # Advanced OAuth with auto-registration
    from empowernow_common import AdvancedOAuth, AuthorizationDetail

    oauth = await AdvancedOAuth.auto_register(
        issuer="https://auth.example.com",
        app_name="My App"
    )

    # FIPS-compliant operations
    from empowernow_common import FIPSAlgorithms

    is_approved = FIPSAlgorithms.is_algorithm_approved("RS256", "jwt_signing")
"""

from __future__ import annotations

# 🔒 FIPS 140-3 Compliance (explicit imports)
from .fips import FIPSAlgorithms

# 🚀 Advanced OAuth Client (explicit imports)
from .oauth.client import (
    AdvancedToken,
    OAuthConfig,
    HardenedOAuth,
    OAuth,
    Token,
)
from .oauth.sync import SyncOAuth

# Selected OAuth helper types
from .oauth.security import generate_correlation_id
from .oauth.rar import SecureAuthorizationDetail as AuthorizationDetail
from .oauth.ciba import CIBARequest

# 🎯 AuthZEN – core façade
from .authzen import (
    Subject,
    Who,
    Resource,
    What,
    Action,
    How,
    Context,
    When,
    AuthRequest,
    AuthResponse,
    PDP,
    PDPClient,
    PolicyClient,
    AuthzClient,
    PDPConfig,
    AuthResult,
)

# 🛡️ Utilities
from .utils.logging_config import setup_default_logging, EmojiDowngradeFilter
from .jwt import peek_header, peek_payload
from .oauth.claims import ClaimsMapper
from .idp import IdPConfig, IdPCatalogue
from .identity import UniqueIdentity

# Exceptions re-export
from .exceptions import EmpowerNowError, OAuthError

# -------------------------------------------------------------
# Public initialization helper – kill hidden side-effects 🧹
# -------------------------------------------------------------
# Applications MUST call empowernow_common.init() once at startup
# to enable FIPS checks, default logging, and other opt-in helpers.
# This avoids network / thread side-effects at import-time.

import warnings as _warnings
import logging as _logging

from .settings import EmpowerNowSettings, settings as _global_settings


def init(
    *,
    strict_fips: bool = False,
    enable_default_logging: bool = True,
    settings: EmpowerNowSettings | None = None,
) -> None:
    """Initialize EmpowerNow Common helpers.

    Args:
        strict_fips:  Fail hard if FIPS validation fails (default: False – warn only).
        enable_default_logging:  Configure root logger with sane defaults unless the
            host application already did so (default: True).
        settings:  Optional EmpowerNowSettings object to override global settings.
    """

    # 0) Override global settings early
    if settings is not None:
        globals()["_global_settings"] = settings  # type: ignore[misc]

    # 1) Default logging (uses settings.log_json_default inside)
    if enable_default_logging:
        setup_default_logging()

    # 2) FIPS validation (can be long-running / spawn background task)
    from .fips import FIPSValidator as _FIPSValidator

    try:
        _FIPSValidator.ensure_compliance()

        # Opt-in continuous validation via env vars – keep behaviour unchanged.
        import os

        if os.getenv("EMPOWERNOW_FIPS_CONTINUOUS", "false").lower() in {
            "true",
            "1",
            "yes",
        }:
            from .fips.validator import start_continuous_validation as _start_cont

            interval = int(os.getenv("EMPOWERNOW_FIPS_INTERVAL", "300"))
            _start_cont(interval, strict_fips)

    except RuntimeError as exc:  # pragma: no cover – environment-specific
        if strict_fips:
            raise
        _warnings.warn(str(exc), RuntimeWarning)
        _logging.getLogger(__name__).warning(
            "FIPS validation failed – continuing in non-FIPS mode"
        )


# Explicit version for PyPI release – keep in sync with pyproject.toml
__version__ = "2.3.7"


__all__ = [
    # 🔒 FIPS
    "FIPSAlgorithms",
    "generate_correlation_id",
    # 🚀 OAuth façade
    "AdvancedToken",
    "OAuthConfig",
    # 🎯 AuthZEN façade
    "Subject",
    "Who",
    "Resource",
    "What",
    "Action",
    "How",
    "Context",
    "When",
    "AuthRequest",
    "AuthResponse",
    "PDP",
    "PDPClient",
    "PolicyClient",
    "AuthzClient",
    "PDPConfig",
    "AuthResult",
    # Exceptions
    "EmpowerNowError",
    "OAuthError",
    # Initialiser
    "init",
    # IdP catalogue
    "IdPConfig",
    "IdPCatalogue",
    "UniqueIdentity",
    # JWT helpers
    "peek_header",
    "peek_payload",
    "ClaimsMapper",
    "SyncOAuth",
    # Factory helpers
    "async_oauth",
    "sync_oauth",
    "secure_token",
]

# ------------------------------------------------------------------
# Lightweight factory helpers – keep import-time cost near-zero
# ------------------------------------------------------------------
# No heavy imports at module load – only stdlib / lightweight types
from typing import Any, Dict
from .oauth.client import SecureOAuthConfig, HardenedOAuth, HardenedToken
from contextlib import asynccontextmanager


def _to_config(cfg: SecureOAuthConfig | Dict[str, Any]) -> SecureOAuthConfig:
    if isinstance(cfg, SecureOAuthConfig):
        return cfg
    return SecureOAuthConfig(**cfg)  # type: ignore[arg-type]


@asynccontextmanager
async def async_oauth(**kwargs):  # noqa: D401 – factory returns context manager
    """Async factory yielding a ready-to-use :class:`HardenedOAuth`.

    Always use via::

        async with async_oauth(**cfg) as oauth:
            ...

    This pattern prevents connection-pool leaks if an exception bubbles and
    mirrors best-practice for `httpx.AsyncClient`.
    """

    client = HardenedOAuth(_to_config(kwargs))  # type: ignore[arg-type]
    try:
        yield client
    finally:
        await client.aclose()


def sync_oauth(**kwargs) -> "SyncOAuth":  # noqa: D401 – factory name is verbish
    """Return a **sync** :class:`~empowernow_common.oauth.sync.SyncOAuth` instance."""

    from .oauth.sync import SyncOAuth  # local import to avoid heavy deps at import time

    cfg = _to_config(kwargs)  # type: ignore[arg-type]
    return SyncOAuth(cfg)


def secure_token(**kwargs) -> HardenedToken:  # noqa: D401 – tiny convenience
    """Blocking helper to fetch a single access-token in **one line**.

    The call wraps ::

        SyncOAuth(**kwargs).get_token()

    so callers can replace verbose boilerplate when they just need a quick
    token in scripts or CI jobs.
    """

    from .oauth.sync import SyncOAuth  # local import to keep startup fast

    return SyncOAuth(_to_config(kwargs)).get_token()


# -------------------------------------------------------------
# ⚠️  Deprecated import-time side-effects removed. Users must now
#      call `empowernow_common.init()` explicitly. 2024-Q2 release.
# -------------------------------------------------------------

# Re-export cache backends and ARN helpers so downstream code can do
# ``from empowernow_common import RedisCacheBackend`` without deep paths.

from .cache import CacheBackend, InMemoryCacheBackend, RedisCacheBackend  # noqa: F401

from .arn import (
    parse as parse_arn,
    validate as validate_arn,
    is_user as is_user_arn,
    to_user_id,
)

from .secret_loader import load_secret, register_provider, SecretLoaderError, SecretNotFound  # noqa: E401,F401

__all__ = [
    # cache
    "CacheBackend",
    "InMemoryCacheBackend",
    "RedisCacheBackend",
    # arn
    "parse_arn",
    "validate_arn",
    "is_user_arn",
    "to_user_id",
]
