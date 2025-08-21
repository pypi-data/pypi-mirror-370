"""Environment-variable helpers.

Currently only exposes :pyfunc:`is_truthy` – converts common boolean-like
string values to ``True``/``False``.
"""

from __future__ import annotations

import os
from typing import Any

__all__ = ["is_truthy"]


_TRUE_VALUES = {"1", "true", "yes", "y", "on"}
_FALSE_VALUES = {"0", "false", "no", "n", "off"}


def is_truthy(value: Any, *, default: bool = False) -> bool:
    """Return *True* if *value* represents a truthy env-var string.

    Accepts booleans, integers, or strings – comparison is case-insensitive.
    If *value* is ``None`` the *default* is returned.
    """

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    if isinstance(value, str):
        v = value.strip().lower()
        if v in _TRUE_VALUES:
            return True
        if v in _FALSE_VALUES:
            return False

    # Fallback – return default
    return default
