"""Deprecated errors module – forwards to *exceptions.py* for backward compat."""

from __future__ import annotations

from enum import Enum

from .exceptions import EmpowerNowError  # re-export


class ErrorCode(str, Enum):
    URL_INVALID = "url_invalid"
    URL_PRIVATE = "url_private"
    TOKEN_EXPIRED = "token_expired"
    TOKEN_TOO_OLD = "token_too_old"
    TOKEN_FUTURE = "token_in_future"


class UrlValidationError(EmpowerNowError):
    """Invalid or unsafe URL."""

    def __init__(self, message: str = "", *, error_code: ErrorCode = None):
        self.error_code: ErrorCode = error_code or ErrorCode.URL_INVALID
        super().__init__(message)


class TokenValidationError(EmpowerNowError):
    """Generic token validation error."""

    def __init__(self, message: str = "", *, error_code: ErrorCode = None):
        self.error_code: ErrorCode = error_code or ErrorCode.TOKEN_EXPIRED
        super().__init__(message)
