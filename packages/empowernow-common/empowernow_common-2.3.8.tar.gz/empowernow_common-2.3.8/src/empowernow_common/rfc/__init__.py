"""empowernow_common.rfc – RFC-specific helper mix-ins

This namespace gradually extracts feature-focused helpers from the legacy
`simple.py` module.  Initial slice exposes Pushed-Authorization-Request (PAR)
and Rich-Authorization-Request (RAR) utilities.

Road-map
────────
* 2024-Q2:  expose `.par` & `.rar` wrappers (this commit)
* 2024-Q3:  add `.dpop`, `.ciba`, etc., then deprecate direct access in
  `simple.py`.
"""

from __future__ import annotations

# PAR helpers
from ..oauth.par import (
    PARRequest,
    PARResponse,
    PARError,
    generate_pkce_challenge,
)

# RAR helpers
from ..oauth.rar import (
    SecureAuthorizationDetail,
    RARBuilder,
    RARError,
    StandardActionType,
    StandardResourceType,
)

# DPoP helpers
from ..oauth.dpop import (
    DPoPKeyPair,
    DPoPProofGenerator,
    DPoPError,
    generate_dpop_key_pair,
)

# CIBA helpers
from ..oauth.ciba import (
    CIBARequest,
    CIBAResponse,
    CIBAError,
)

# JARM helpers
from ..oauth.jarm import (
    JARMConfiguration,
    JARMResponseProcessor,
    JARMError,
)

# ---------------------------------------------------------------------------
# Public helper – process_jarm_response
# ---------------------------------------------------------------------------
# This keeps backwards-compatibility with earlier BFF/SDK code that expected
# a convenience function directly in `empowernow_common.rfc`.


def process_jarm_response(response_jwt: str, *, client_id: str | None = None):  # type: ignore[arg-type]
    """Validate & decode a JARM response JWT.

    Internally delegates to :class:`JARMResponseProcessor` with a default
    configuration (no encryption expected).  The optional *client_id* allows
    callers to set the expected ``aud`` claim but is not strictly required.
    """

    processor = JARMResponseProcessor(JARMConfiguration(), client_id or "n/a")
    return processor.process_response(response_jwt)

__all__ = [
    # PAR
    "PARRequest",
    "PARResponse",
    "PARError",
    "generate_pkce_challenge",
    # RAR
    "SecureAuthorizationDetail",
    "RARBuilder",
    "RARError",
    "StandardActionType",
    "StandardResourceType",
    # DPoP
    "DPoPKeyPair",
    "DPoPProofGenerator",
    "DPoPError",
    "generate_dpop_key_pair",
    # CIBA
    "CIBARequest",
    "CIBAResponse",
    "CIBAError",
    # JARM
    "JARMConfiguration",
    "JARMResponseProcessor",
    "JARMError",
    # Convenience
    "process_jarm_response",
]
