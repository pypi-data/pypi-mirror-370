"""Lightweight secret-loading helper.

Usage
-----
>>> from empowernow_common.secret_loader import load_secret
>>> load_secret("file:primary:oidc-client-secret")
"""
from __future__ import annotations

import os
import time
import uuid
from pathlib import Path
from typing import Callable, Dict, Optional

__all__ = [
    "load_secret",
    "register_provider",
    "register_audit_hook",
    "SecretNotFound",
    "SecretLoaderError",
]

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class SecretLoaderError(RuntimeError):
    """Base class for secret-loader errors."""


class SecretNotFound(SecretLoaderError):
    """Raised when a secret cannot be resolved by any provider."""


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------
ProviderFunc = Callable[[str, str, Optional[str]], str]


_PROVIDERS: Dict[str, ProviderFunc] = {}

# Optional global audit hook (set via register_audit_hook)
_GLOBAL_AUDIT_HOOK: Optional[Callable[[dict], None]] = None


def register_audit_hook(hook: Callable[[dict], None]) -> None:
    """Register a process-wide audit hook.

    The *hook* will be called with the event dict every time a secret
    is successfully resolved.  Only one hook can be active at a time; the
    last registration wins.
    """
    global _GLOBAL_AUDIT_HOOK
    _GLOBAL_AUDIT_HOOK = hook


def register_provider(scheme: str, func: ProviderFunc) -> None:
    """Register a provider for a *scheme* (e.g. ``file`` or ``env``)."""

    if ":" in scheme:
        raise ValueError("Scheme must not contain ':'")
    _PROVIDERS[scheme] = func


# ---------------------------------------------------------------------------
# Built-in providers
# ---------------------------------------------------------------------------


def _file_provider(instance: str, secret_id: str, *_: str) -> str:
    """Read a secret from a read-only mounted file.

    Looks under ``$FILE_MOUNT_PATH`` (default ``/run/secrets``) then a
    sub-directory matching *instance*.
    """

    mount = os.getenv("FILE_MOUNT_PATH", "/run/secrets")
    candidate = Path(mount) / instance / secret_id
    if not candidate.exists():
        # Fallback: some setups mount file directly without instance dir
        candidate = Path(mount) / secret_id
    try:
        raw = candidate.read_text(encoding="utf-8").strip()
        # Attempt JSON parse
        import json

        try:
            parsed = json.loads(raw)
            # If JSON is an object with one field 'value', surface that
            if isinstance(parsed, dict) and set(parsed.keys()) == {"value"}:
                return str(parsed["value"])
            # Otherwise return original stringified JSON
            return raw
        except json.JSONDecodeError:
            pass

        # Attempt key=value multi line (use first)
        if "=" in raw:
            for line in raw.splitlines():
                if "=" in line:
                    _, v = line.split("=", 1)
                    return v.strip()

        return raw
    except FileNotFoundError as exc:
        raise SecretNotFound(f"Secret file not found: {candidate}") from exc


def _env_provider(var_name: str, *_: str) -> str:  # type: ignore[override]
    """Return secret from environment variable (dev only)."""

    value = os.getenv(var_name)
    if value is None:
        raise SecretNotFound(f"Environment variable {var_name} not set")
    return value


# Register defaults
register_provider("file", _file_provider)  # type: ignore[arg-type]
register_provider("env", _env_provider)  # type: ignore[arg-type]


# Ensure extra providers are registered
from . import providers  # noqa: E402,F401


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_secret(pointer: str, *, audit_hook: Optional[Callable[[dict], None]] = None) -> str:
    """Resolve *pointer* using the appropriate provider.

    The *pointer* must be in the form ``<scheme>:<rest>``. For *file* and *env*
    schemes we expect:

    • ``file:<instance>:<id>`` → reads ``/$FILE_MOUNT_PATH/<instance>/<id>``
    • ``env:<VAR_NAME>``       → returns value of environment variable
    """
    if ":" not in pointer:
        raise SecretLoaderError("Pointer must contain ':' separating scheme")

    scheme, rest = pointer.split(":", 1)
    provider = _PROVIDERS.get(scheme)
    if provider is None:
        raise SecretLoaderError(f"Unknown secret scheme '{scheme}'")

    # Parse rest for file provider into instance + id
    if scheme == "file":
        try:
            instance, secret_id = rest.split(":", 1)
        except ValueError as exc:
            raise SecretLoaderError("file pointer must be file:<instance>:<id>") from exc
        secret = provider(instance, secret_id)  # type: ignore[arg-type]
        _audit(audit_hook or _GLOBAL_AUDIT_HOOK, scheme, f"{instance}:{secret_id}")
        return secret

    if scheme == "env":
        secret = provider(rest)  # type: ignore[arg-type]
        _audit(audit_hook or _GLOBAL_AUDIT_HOOK, scheme, rest)
        return secret

    # Generic fallback: provider receives *rest* and embeds its own parsing
    secret = provider(rest)  # type: ignore[arg-type]
    _audit(audit_hook or _GLOBAL_AUDIT_HOOK, scheme, rest)
    return secret


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _audit(hook: Optional[Callable[[dict], None]], scheme: str, identifier: str) -> None:
    if hook is None:
        return
    event = {
        "event": "secret_resolved",
        "scheme": scheme,
        "id": identifier,
        "timestamp": time.time(),
        "trace_id": uuid.uuid4().hex,
    }
    try:
        hook(event)
    except Exception:
        # Never break caller if audit fails
        pass 