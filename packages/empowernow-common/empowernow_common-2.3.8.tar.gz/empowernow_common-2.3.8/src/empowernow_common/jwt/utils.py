"""Simple, dependency-free helpers to look at JWT structures without verifying.

These functions do *not* validate signatures or claim sets – they are only
meant for routing logic, logging or debugging where cryptographic integrity
is either ensured upstream or not required.
"""

from __future__ import annotations

import base64
import json
from typing import Any, Dict

__all__ = ["peek_header", "peek_payload"]


def _b64url_decode(part: str) -> bytes:
    # Add padding if missing
    padded = part + "=" * (-len(part) % 4)
    return base64.urlsafe_b64decode(padded)


def peek_header(token: str) -> Dict[str, Any]:
    """Return decoded JWT header as dict without verifying signature."""

    try:
        header_b64 = token.split(".", 2)[0]
        return json.loads(_b64url_decode(header_b64))
    except (ValueError, IndexError, json.JSONDecodeError) as exc:
        raise ValueError("invalid JWT") from exc


def peek_payload(token: str) -> Dict[str, Any]:
    """Return decoded JWT payload (claims) as dict without verifying."""

    try:
        payload_b64 = token.split(".", 2)[1]
        return json.loads(_b64url_decode(payload_b64))
    except (ValueError, IndexError, json.JSONDecodeError) as exc:
        raise ValueError("invalid JWT") from exc
