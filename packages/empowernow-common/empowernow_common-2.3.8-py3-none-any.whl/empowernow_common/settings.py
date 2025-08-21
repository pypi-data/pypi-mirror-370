"""Central SDK settings.

Loads configuration from environment variables (and optionally a YAML file)
and exposes them as a frozen Pydantic model so code can avoid repetitive
``os.getenv`` calls.

Environment precedence: explicit kwargs > YAML file > env vars > defaults.

Example::

    from empowernow_common.settings import settings
    if settings.async_logging:
        start_async_logging()
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from pydantic_settings import BaseSettings  # type: ignore
    from pydantic import Field, field_validator
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "pydantic-settings is required for EmpowerNowSettings (pydantic v2)."
    ) from exc

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore


class EmpowerNowSettings(BaseSettings):
    # ------------------------------------------------------------------
    # Core toggles
    # ------------------------------------------------------------------

    async_logging: bool = Field(default_factory=lambda: os.getenv("ASYNC_LOGGING", "0") in {"1", "true", "yes"})
    enable_authentication: bool = Field(default_factory=lambda: os.getenv("ENABLE_AUTHENTICATION", "1") not in {"0", "false", "no"})

    # Logging
    log_json_default: bool = Field(default_factory=lambda: os.getenv("LOG_JSON", "0") in {"1", "true", "yes"})

    # FIPS toggles
    openssl_fips: bool = Field(default_factory=lambda: os.getenv("OPENSSL_FIPS", "0").lower() in {"1", "true", "on"})
    empowernow_fips_mode: bool = Field(default_factory=lambda: os.getenv("EMPOWERNOW_FIPS_MODE", "0").lower() in {"1", "true"})

    # Logging / queue size
    log_queue_size: int = Field(default_factory=lambda: int(os.getenv("LOG_Q_SIZE", "20000")))

    # Security related env toggles surfaced for FIPS checks
    cryptography_openssl_no_legacy: bool = Field(default_factory=lambda: os.getenv("CRYPTOGRAPHY_OPENSSL_NO_LEGACY", "0").lower() in {"1", "true"})
    pythonhashseed: str = Field(default_factory=lambda: os.getenv("PYTHONHASHSEED", "not_set"))

    class Config:
        frozen = True
        env_prefix = "EMPOWERNOW_"
        case_sensitive = False

    # ------------------------------------------------------------------
    # YAML loader (optional)
    # ------------------------------------------------------------------

    @classmethod
    def load(cls, *, yaml_path: str | Path | None = None, **overrides: Any) -> "EmpowerNowSettings":
        data: Dict[str, Any] = {}
        if yaml_path:
            p = Path(yaml_path).expanduser()
            if not p.exists():
                raise FileNotFoundError(p)
            if yaml is None:
                raise ImportError("PyYAML required to load settings from YAML")
            data = yaml.safe_load(p.read_text("utf-8")) or {}
        data.update(overrides)
        return cls(**data)


# Global singleton – applications can override by calling *load()* early.
settings = EmpowerNowSettings()  # type: ignore[var-annotated]

__all__ = ["EmpowerNowSettings", "settings"] 