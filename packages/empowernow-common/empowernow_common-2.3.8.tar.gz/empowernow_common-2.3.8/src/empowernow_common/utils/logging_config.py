import logging
import re
import json
from datetime import datetime, timezone
import os as _os
from typing import Any
from enum import Enum

from ..settings import settings

_EMOJI_PATTERN = re.compile("[\U0001f300-\U0001f6ff\U0001f900-\U0001faff]")

__all__ = [
    "setup_default_logging",
    "enable_json_logging",
    "get_logger",
    "EmojiDowngradeFilter",
    "EmojiStripFilter",
    "LogEvent",
]


class EmojiDowngradeFilter(logging.Filter):
    """Downgrades INFO log records containing emoji to DEBUG level."""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno == logging.INFO and _EMOJI_PATTERN.search(
            record.getMessage()
        ):
            record.levelno = logging.DEBUG
            record.levelname = "DEBUG"
        return True


class EmojiStripFilter(logging.Filter):
    """Remove emoji characters completely from log records (message only)."""

    def filter(self, record: logging.LogRecord) -> bool:
        # Only mutate msg; args remain untouched as we rebuild message string.
        cleaned = _EMOJI_PATTERN.sub("", record.getMessage())
        record.msg = cleaned
        record.args = ()
        return True


def setup_default_logging(
    level: int = logging.WARNING, *, strip_emojis: bool = False
) -> None:
    """Configure root logger with emoji filter and simple format.

    Apps can call this early (or rely on empowernow_common __init__).
    """
    no_emoji_env = _os.getenv("EMPOWERNOW_NO_EMOJI", "0").lower() in {"1", "true", "yes"}

    root = logging.getLogger()
    if not any(isinstance(f, EmojiDowngradeFilter) for f in root.filters):
        root.addFilter(EmojiDowngradeFilter())
    if (strip_emojis or no_emoji_env) and not any(
        isinstance(f, EmojiStripFilter) for f in root.filters
    ):
        root.addFilter(EmojiStripFilter())
    if settings.log_json_default:
        enable_json_logging(level=level)
    else:
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )


# ---------------- Structured JSON Logger ------------------


class JsonLogFormatter(logging.Formatter):
    """Simple JSON log formatter compatible with ECS/Otel."""

    def format(self, record: logging.LogRecord) -> str:
        log_dict = {
            "timestamp": datetime.fromtimestamp(
                record.created, timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_dict["exception"] = self.formatException(record.exc_info)
        if isinstance(record.args, dict):
            log_dict.update(record.args)
        # Include any extra keys passed via logger.extra
        for key, value in record.__dict__.items():
            if key not in (
                "message",
                "asctime",
                "levelname",
                "name",
                "msg",
                "args",
                "exc_info",
                "exc_text",
            ):
                log_dict[key] = value
        return json.dumps(log_dict, ensure_ascii=False)


def enable_json_logging(level: int = logging.INFO) -> None:
    """Switch root logger to JSON formatting."""
    root = logging.getLogger()
    # remove existing handlers
    for h in list(root.handlers):
        root.removeHandler(h)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())
    root.addHandler(handler)
    root.setLevel(level)


# ------------------------------------------------------------------
# Public thin-wrapper – single source of truth for obtaining loggers.
# ------------------------------------------------------------------


def get_logger(name: str, **kwargs: Any) -> logging.Logger:  # noqa: D401 – helper
    """Return a standard `logging.Logger` (JSON formatted if `setup_default_logging` was called).

    This wrapper exists to de-duplicate `empowernow_common.logging.get_logger`.
    Future versions will fully remove the legacy module; meanwhile this keeps
    backward-compat parity while new code should `from empowernow_common.utils.logging_config import get_logger`.
    """

    return logging.getLogger(name)


# ------------------------------------------------------------------
# Standardised log-event identifiers (previously in legacy logging module)
# ------------------------------------------------------------------


class LogEvent(str, Enum):
    """Canonical event IDs emitted by EmpowerNow services."""

    AUTH_START = "auth_start"
    AUTH_SUCCESS = "auth_success"
    AUTH_ERROR = "auth_error"
    TOKEN_INTROSPECTION = "token_introspection"
    PDP_EVALUATE = "pdp_evaluate"
    PDP_DECISION_ALLOW = "pdp_allow"
    PDP_DECISION_DENY = "pdp_deny"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    RATE_LIMIT_HIT = "rate_limit_hit"
