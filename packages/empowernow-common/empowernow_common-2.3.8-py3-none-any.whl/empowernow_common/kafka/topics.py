"""Canonical Kafka topic registry used by platform_producer.

Applications should import TOPICS and reference keys instead of hardcoding
strings, so topic names can evolve centrally.
"""
from __future__ import annotations

TOPICS = {
    # Audit / security
    "audit.secret_access": "platform.secret_access_audit",

    # CRUD service
    "crud.operations": "crud.operations",
    "crud.metrics": "crud.metrics",

    # PDP service
    "pdp.decisions": "pdp.decisions",

    # Membership service
    "membership.identity": "membership.identities",

    # Future topics can be added here
} 