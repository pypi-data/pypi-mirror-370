"""FastAPI integration helpers (optional extra).

Requires ``pip install empowernow-common[fastapi]`` which pulls FastAPI and
its dependencies.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional

from fastapi import Depends, HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.routing import APIRouter

from ..idp import IdPCatalogue
from ..oauth.client import HardenedOAuth
from ..cache import InMemoryCacheBackend, CacheBackend
from ..identity import UniqueIdentity
from ..jwt import peek_payload
from ..oauth.claims import ClaimsMapper
from ..settings import settings
from ..utils.logging_config import get_logger, LogEvent
from ..utils.retry import with_retry

__all__ = ["build_auth_dependency", "request_context"]


BearerAuth = HTTPBearer(auto_error=False)
logger = get_logger(__name__)


# Public ------------------------------------------------------------------


def build_auth_dependency(
    catalogue: IdPCatalogue,
    oauth: HardenedOAuth,
    *,
    cache: CacheBackend[Dict[str, Any]] | None = None,
    ttl_skew: int = 60,
    map_claims: bool = True,
    claims_mapper: Callable[[Dict[str, Any]], Dict[str, Any]] | None = None,
) -> Callable:
    """Return a FastAPI dependency for bearer authentication.

    Parameters
    ----------
    catalogue:
        Loaded :class:`IdPCatalogue` instance.
    oauth:
        Shared :class:`HardenedOAuth` client used for introspection.
    cache:
        Optional cache backend (defaults to in-memory).  Introspection results
        are cached until *exp* minus *ttl_skew* seconds.
    ttl_skew:
        Seconds subtracted from *exp* to refresh tokens slightly before they
        actually expire.
    map_claims:
        When *True* applies claims mapping to the introspected token.
    claims_mapper:
        Optional claims mapper function to apply to the introspected token.
    """

    if cache is None:
        cache = InMemoryCacheBackend(enable_gc=True)

    mapper_fn = claims_mapper or ClaimsMapper.normalize

    async def _auth_dependency(
        request: Request,
        cred: HTTPAuthorizationCredentials = Security(BearerAuth),
    ) -> Dict[str, Any]:
        # Anonymous mode --------------------------------------------------
        if not settings.enable_authentication:
            logger.info("authentication skipped (ENABLE_AUTHENTICATION=0)")
            return {"sub": "anonymous", "unique_id": "auth:anon"}

        # Missing credentials --------------------------------------------
        if cred is None:
            logger.warning("no bearer token", extra={"event": LogEvent.AUTH_ERROR})
            raise HTTPException(401, "missing credentials")

        token = cred.credentials.strip()

        # Parse issuer quickly without verification
        try:
            payload_raw = peek_payload(token)
            issuer = payload_raw.get("iss")
            if not issuer:
                raise ValueError
        except Exception:
            raise HTTPException(401, "invalid token structure")

        idp_cfg = catalogue.for_issuer(issuer)
        if idp_cfg is None:
            logger.warning(
                "unknown issuer", extra={"event": LogEvent.AUTH_ERROR, "issuer": issuer}
            )
            raise HTTPException(401, "unknown issuer")

        # Cache layer -----------------------------------------------------
        cached = cache.get(token)
        if cached:
            logger.debug("introspection cache hit", extra={"event": LogEvent.CACHE_HIT})
            return cached

        # Call IdP introspection -----------------------------------------
        async def _call_introspect():
            return await oauth.introspect_token(token)

        try:
            introspected = await with_retry(_call_introspect)
        except Exception as exc:
            logger.error(
                "introspection failed",
                extra={"event": LogEvent.AUTH_ERROR, "err": str(exc)},
            )
            raise HTTPException(502, "token introspection failed") from exc

        if not introspected.get("active"):
            logger.info("inactive token", extra={"event": LogEvent.AUTH_ERROR})
            raise HTTPException(401, "inactive token")

        # Build UniqueIdentity -------------------------------------------
        introspected["unique_id"] = UniqueIdentity(
            issuer=introspected["iss"],
            subject=introspected["sub"],
            idp_name=idp_cfg.name,
        ).value

        # Cache until expiry (minus skew)
        exp = introspected.get("exp", int(time.time()) + 60)
        ttl = max(30, exp - int(time.time()) - ttl_skew)

        # Optional claim normalisation -----------------------------------
        if map_claims:
            try:
                normalized = mapper_fn(introspected)
                introspected["normalized_claims"] = normalized
                request.state.normalized_claims = normalized  # type: ignore[attr-defined]
            except Exception as exc:
                logger.debug("claims mapping failed", exc_info=exc)

        cache.set(token, introspected, ttl=ttl)
        logger.debug(
            "introspection cached", extra={"event": LogEvent.CACHE_MISS, "ttl": ttl}
        )

        return introspected

    # Attach OpenAPI security scheme once on import -----------------------
    _register_openapi_security_scheme()

    return _auth_dependency


# ---------------------------------------------------------------------
# OpenAPI helper
# ---------------------------------------------------------------------


_registered = False


def _register_openapi_security_scheme() -> None:  # pragma: no cover – best-effort
    global _registered
    if _registered:
        return

    try:
        from fastapi.openapi.models import HTTPBearer as _HTTPBearerModel
        from fastapi.openapi.utils import get_openapi
        from fastapi import FastAPI

        # Patch FastAPI.get_openapi globally once
        if hasattr(FastAPI, "_empowernow_openapi_patched"):
            _registered = True
            return

        orig_get_openapi = FastAPI.openapi

        def custom_openapi(self: FastAPI):  # type: ignore[override]
            if self.openapi_schema:
                return self.openapi_schema
            schema = orig_get_openapi(self)
            scheme_name = "EmpowerNowBearer"
            if "securitySchemes" not in schema["components"]:
                schema["components"]["securitySchemes"] = {}
            schema["components"]["securitySchemes"][scheme_name] = _HTTPBearerModel(
                type="http", scheme="bearer"
            ).dict()
            for route in self.routes:
                if getattr(route.endpoint, "_requires_bearer", False):
                    for method in route.methods:
                        schema["paths"][route.path][method.lower()]["security"] = [
                            {scheme_name: []}
                        ]
            self.openapi_schema = schema
            return schema

        FastAPI.openapi = custom_openapi  # type: ignore[assignment]
        FastAPI._empowernow_openapi_patched = True  # type: ignore[attr-defined]
        _registered = True
    except ImportError:
        # FastAPI not available / docs disabled
        pass


# ------------------------------------------------------------------
# Request context extractor
# ------------------------------------------------------------------


_SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "proxy-authorization"}


async def request_context(
    request: Request,
    *,
    include_headers: bool = False,
    include_body: bool = False,
    max_body_bytes: int = 2048,
) -> Dict[str, Any]:
    """Return a context dict suitable for `EnhancedPDP.check()`.

    Parameters
    ----------
    include_headers:
        When *True* includes **masked** request headers.
    include_body:
        When *True* includes raw body bytes capped at *max_body_bytes*.
    max_body_bytes:
        Maximum number of bytes to read from the request body (default 2 KiB).
    """

    ctx: Dict[str, Any] = {
        "ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "query_params": dict(request.query_params) if request.query_params else {},
    }

    if include_headers:
        masked_headers: Dict[str, str] = {}
        for k, v in request.headers.items():
            if k.lower() in _SENSITIVE_HEADERS:
                masked_headers[k] = "***redacted***"
            else:
                masked_headers[k] = v
        ctx["headers"] = masked_headers

    if include_body:
        try:
            body_bytes = await request.body()
            if len(body_bytes) > max_body_bytes:
                body_bytes = body_bytes[:max_body_bytes] + b"..."
            ctx["body"] = body_bytes.decode(errors="replace")
        except Exception as exc:  # pragma: no cover – edge-case
            logger.debug("could not read request body", exc_info=exc)

    return ctx
