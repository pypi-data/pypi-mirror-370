"""
FIPS 140-3 Compliance Module

This module provides FIPS 140-3 compliant cryptographic operations and validation
based on the proven implementation from the EmpowerNow IdP.
"""

from .algorithms import FIPSAlgorithms
from .validator import FIPSValidator, ensure_fips_compliance, is_fips_mode
from .entropy import SecureRandomGenerator, FIPSCompliantRandom

__all__ = [
    "FIPSAlgorithms",
    "FIPSValidator",
    "ensure_fips_compliance",
    "is_fips_mode",
    "SecureRandomGenerator",
    "FIPSCompliantRandom",
    "is_fips_runtime",
]

# ---------------------------------------------------------------------------
# Runtime helper — expose current FIPS mode (backlog 4.1)
# ---------------------------------------------------------------------------


def is_fips_runtime() -> bool:
    """Return *True* if the running OpenSSL backend reports FIPS mode enabled.

    The check is best-effort: if OpenSSL bindings are missing or do not expose
    `openssl_fips_mode()`, we fall back to *False*.
    """

    try:
        import ssl

        # OpenSSL 3.x provides FIPS provider; older versions expose FIPS_mode()
        if hasattr(ssl, "FIPS_mode"):
            return bool(ssl.FIPS_mode())  # type: ignore[attr-defined]

        # cryptography.io helper (OpenSSL 3)
        from cryptography.hazmat.bindings.openssl import binding  # type: ignore

        backend = binding.Binding()
        return backend.lib.EVP_default_properties_is_fips_enabled(None) == 1  # type: ignore[attr-defined]
    except Exception:
        return False
