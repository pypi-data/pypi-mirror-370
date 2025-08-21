"""Extra provider implementations for secret_loader.

Currently only an advanced file provider with audit/permission checks.
"""
from __future__ import annotations

import json
import logging
import os
import stat
from pathlib import Path
from typing import Any, Dict

from . import register_provider, SecretNotFound

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Advanced file provider – exposes dict for multi-field secrets & permission check
# ---------------------------------------------------------------------------

def _file_adv_provider(instance: str, secret_id: str, *_: str):
    mount = os.getenv("FILE_MOUNT_PATH", "/run/secrets")
    candidate = Path(mount) / instance / secret_id
    if not candidate.exists():
        candidate = Path(mount) / secret_id
    if not candidate.exists():
        raise SecretNotFound(f"Secret file not found: {candidate}")

    # Warn on permissive file mode (>600)
    try:
        mode = stat.S_IMODE(candidate.stat().st_mode)
        if mode > 0o600:
            logger.warning(
                "Secret file '%s' permissions too permissive: %o (expected <= 600)",
                candidate,
                mode,
            )
    except Exception:
        pass

    raw = candidate.read_text(encoding="utf-8").rstrip("\n")

    # JSON object? Return as dict
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    # key=value lines -> dict
    if "=" in raw:
        data: Dict[str, Any] = {}
        for line in raw.splitlines():
            if not line.strip() or "=" not in line:
                continue
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip()
        if data:
            return data

    # Fallback single value
    return raw


# register provider under scheme 'filex' (file extended)
register_provider("filex", _file_adv_provider) 