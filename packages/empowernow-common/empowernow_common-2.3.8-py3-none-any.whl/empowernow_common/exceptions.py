"""Centralised exception hierarchy for EmpowerNow SDK."""


class EmpowerNowError(Exception):
    """Base class for all custom exceptions raised by empowernow_common."""

    pass


class OAuthError(EmpowerNowError):
    """Generic OAuth-related error when a more specific subclass is not available."""

    pass


class GrantManagementError(OAuthError):
    """Errors related to OAuth 2.0 Grant Management (RFC 8707)."""

    pass


# ----------------- AuthZEN -----------------


class AuthZENError(EmpowerNowError):
    """Base class for all AuthZEN-specific errors."""

    pass
