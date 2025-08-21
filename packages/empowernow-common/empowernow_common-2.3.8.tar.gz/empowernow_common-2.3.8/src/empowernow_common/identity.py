"""Identity helpers (UniqueIdentity).

A compact, deterministic string that uniquely identifies a principal across
multiple IdPs.  Optimised for audit-logs, cache keys and resource ACLs.

Format (canonical):

    auth:{entity_type}:{idp_name}:{subject}

Examples::

    >>> uid = UniqueIdentity(issuer="https://login.microsoftonline.com/contoso", subject="123")
    >>> str(uid)
    'auth:account:login.microsoftonline.com:123'

The helper supports three creation paths:

* direct construction ``UniqueIdentity(issuer, subject)``
* parsing a canonical UID string via :py:meth:`parse`
* deriving from a JWT claims payload via :py:meth:`from_claims`
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

__all__ = ["UniqueIdentity"]


@dataclass(slots=True, frozen=True)
class UniqueIdentity:
    issuer: str
    subject: str
    idp_name: str = "unknown"
    entity_type: str = "account"

    # -------------------------- derived props --------------------------

    @property
    def value(self) -> str:  # noqa: D401 – convenience alias
        """Return canonical *auth:* identifier (without "auth://" schema)."""

        safe_idp = self.idp_name.replace(":", "_").lower()
        return f"auth:{self.entity_type}:{safe_idp}:{self.subject}"

    def __str__(self) -> str:  # noqa: DunderStub
        return self.value

    # -------------------------- constructors --------------------------

    @classmethod
    def from_claims(cls, claims: dict[str, str]) -> "UniqueIdentity":  # type: ignore[type-var]
        """Create from JWT claims (requires at least *iss* and *sub*)."""

        if "iss" not in claims or "sub" not in claims:
            raise ValueError("claims missing 'iss' or 'sub'")
        return cls(
            issuer=claims["iss"],
            subject=claims["sub"],
            idp_name=_idp_from_issuer(claims["iss"]),
        )

    @classmethod
    def parse(cls, uid: str) -> "UniqueIdentity":
        """Parse canonical UID strings produced by :py:meth:`value`."""

        if not uid.startswith("auth:"):
            raise ValueError("UID must start with 'auth:'")
        try:
            _, entity_type, idp_name, subject = uid.split(":", 3)
        except ValueError as exc:
            raise ValueError("invalid unique-id format") from exc
        issuer = f"https://{idp_name}"
        return cls(
            issuer=issuer, subject=subject, idp_name=idp_name, entity_type=entity_type
        )


# ---------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------


_IDP_RE = re.compile(r"^(?P<host>[a-zA-Z0-9.\-]+)(/|$)")


def _idp_from_issuer(issuer: str) -> str:
    """Return host component of the issuer URL or raw ARN segment."""

    # URL issuer
    if "://" in issuer:
        host = urlparse(issuer).netloc
        return host.lower()

    # ARN style: "arn:aws:cognito-idp:...:userpool/us-east-1_XXX"
    if issuer.startswith("arn:"):
        parts = issuer.split(":")
        if len(parts) >= 6:
            return parts[5].split("/")[0]

    # Fallback: strip path/query if present
    m = _IDP_RE.match(issuer)
    return (m.group("host") if m else issuer).lower()
