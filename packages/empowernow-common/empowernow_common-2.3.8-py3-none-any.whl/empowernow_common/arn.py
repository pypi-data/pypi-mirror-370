"""Empower ARN helper functions.

The platform uses a constrained subset of Amazon-style Amazon Resource
Names to identify subjects, resources and policies in a compact,
string-safe way.

Grammar (v1):
    arn:emp:<type>:<id>[#<fragment>]

* *type*   – lowercase identifier (``user``, ``group``, ``policy`` …).
* *id*     – URL-safe identifier (uuid, slug, numeric id …).
* fragment – optional sub-resource / field path after ``#``.

This module provides two public helpers that BFF / micro-services need:

* ``parse(arn_str)``      → ``{"type": str, "id": str, "fragment": str|None}``
* ``is_user(arn_str)``    → bool  (fast path used in auth headers)
* ``to_user_id(arn)``     → returns *id* only if *type == 'user'*, else ``None``

The implementation is intentionally lightweight and avoids regex for
speed (length << 128 bytes).
"""
from __future__ import annotations

from typing import Optional, Tuple, Dict

__all__ = [
    "parse",
    "validate",
    "is_user",
    "to_user_id",
]

PREFIX = "arn:emp:"


def _split_fragment(arn: str) -> Tuple[str, Optional[str]]:
    if "#" in arn:
        base, frag = arn.split("#", 1)
        return base, frag or None
    return arn, None


def parse(arn: str) -> Dict[str, Optional[str]]:
    """Return components of an Empower ARN.

    Raises ``ValueError`` if string is not a valid ARN.
    """
    typ, _id, frag = _parse_components(arn)
    return {"type": typ, "id": _id, "fragment": frag}


def validate(arn: str) -> bool:  # fast path for middleware
    try:
        _parse_components(arn)
        return True
    except ValueError:
        return False


def is_user(arn: str) -> bool:
    try:
        typ, *_ = _parse_components(arn)
        return typ == "user"
    except ValueError:
        return False


def to_user_id(arn: str) -> Optional[str]:
    try:
        typ, _id, _ = _parse_components(arn)
        return _id if typ == "user" else None
    except ValueError:
        return None


# ---------------- internal helpers ---------------- #

def _parse_components(arn: str) -> Tuple[str, str, Optional[str]]:
    if not arn.startswith(PREFIX):
        raise ValueError("ARN must start with 'arn:emp:'")

    base, frag = _split_fragment(arn)
    parts = base[len(PREFIX) :].split(":", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("ARN must be 'arn:emp:<type>:<id>'")

    typ, _id = parts

    # basic sanity: only lowercase letters + digits for type
    if not typ.isalnum() or not typ.islower():
        raise ValueError("Invalid ARN type")

    # _id can be UUID or other slug, limit length
    if len(_id) > 128:
        raise ValueError("ARN id too long")

    return typ, _id, frag 