"""Kafka audit hook for empowernow_common.secret_loader.

Publishes a small JSON event to the topic defined in ``SECRET_AUDIT_KAFKA_TOPIC``
(default: ``platform.secret_access_audit``). Enable by setting
``SECRET_AUDIT_KAFKA_ENABLED=true`` (default). Safe-fails (no raise) if Kafka
is unreachable or ``aiokafka`` is not installed.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid

from empowernow_common.kafka.platform_producer import publish  # reuse shared producer

from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ENABLED = os.getenv("SECRET_AUDIT_KAFKA_ENABLED", "true").lower() in {"1", "true", "yes"}
TOPIC = os.getenv("SECRET_AUDIT_KAFKA_TOPIC", "platform.secret_access_audit")
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092").split(",")
SERVICE_NAME = os.getenv("SERVICE_NAME", os.getenv("HOSTNAME", "unknown-service"))

# ---------------------------------------------------------------------------
# Lazy producer singleton
# ---------------------------------------------------------------------------
# producer functions reused, so we don't need local producer


# ---------------------------------------------------------------------------
# Public audit hook
# ---------------------------------------------------------------------------
async def audit_hook(event: dict):  # noqa: D401
    """Async hook passed to secret_loader; publishes *event* to Kafka."""
    if not ENABLED:
        return
    try:
        event.setdefault("service", SERVICE_NAME)
        event.setdefault("event_id", uuid.uuid4().hex)
        await publish(TOPIC, key=event["event_id"], value=event)
    except Exception as exc:
        logger.debug("Failed to send secret audit event: %s", exc)


# ---------------------------------------------------------------------------
# Auto-register on import
# ---------------------------------------------------------------------------
if ENABLED:
    try:
        from empowernow_common.secret_loader import register_audit_hook  # noqa: WPS433 (runtime import)

        register_audit_hook(lambda e: asyncio.create_task(audit_hook(e)))
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to register Kafka audit hook: %s", exc) 