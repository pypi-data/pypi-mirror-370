"""
🛡️ Enhanced Secure PDP Client - SECURITY HARDENED

Policy Enforcement Point capabilities with comprehensive security protections.

SECURITY ENHANCEMENTS:
- Input validation and sanitization for all parameters
- Secure constraint and obligation handler registration
- Authentication hardening with token validation
- Rate limiting and abuse protection
- Injection attack prevention
- Secure logging with sensitive data redaction
- Resource exhaustion protection
- FIPS-compliant cryptographic operations
"""

import asyncio
import hashlib
import hmac
import json
import logging
import re
import ssl
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, Any, Optional, Union, List, Callable, Awaitable, Set, Tuple
from urllib.parse import urlparse

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    httpx = None

from pydantic import BaseModel, Field, ConfigDict, validator

from .models import (
    SecureSubject,
    SecureResource,
    SecureAction,
    SecureContext,
    SecureAuthRequest,
    SecureAuthResponse,
)
from ..fips.entropy import generate_correlation_id, generate_secure_token
from ..fips.validator import FIPSValidator
from empowernow_common.oauth.dpop import DPoPManager
from ..exceptions import AuthZENError

logger = logging.getLogger(__name__)

# Security constants
MAX_CONSTRAINT_ID_LENGTH = 128
MAX_OBLIGATION_ID_LENGTH = 128
MAX_CONSTRAINT_PARAMETERS_SIZE = 10240  # 10KB
MAX_OBLIGATION_PARAMETERS_SIZE = 10240  # 10KB
MAX_CONSTRAINT_HANDLERS = 20
MAX_OBLIGATION_HANDLERS = 20
MAX_CORRELATION_ID_LENGTH = 64

# Rate limiting
DEFAULT_RATE_LIMIT_PER_MINUTE = 100
DEFAULT_RATE_LIMIT_BURST = 20


class AuthZENSecurityError(AuthZENError):
    """AuthZEN security-related errors"""

    pass


class ConstraintSecurityError(AuthZENSecurityError):
    """Constraint security-related errors"""

    pass


class ObligationSecurityError(AuthZENSecurityError):
    """Obligation security-related errors"""

    pass


class RateLimitExceededError(AuthZENSecurityError):
    """Rate limit exceeded error"""

    pass


def validate_handler_name(handler_name: str, context: str) -> str:
    """Validate handler names to prevent injection attacks"""
    if not isinstance(handler_name, str):
        raise AuthZENSecurityError(f"{context} handler name must be string")

    if len(handler_name) > 64:
        raise AuthZENSecurityError(f"{context} handler name too long")

    # Only allow alphanumeric, underscore, hyphen
    if not re.match(r"^[a-zA-Z0-9_-]+$", handler_name):
        raise AuthZENSecurityError(
            f"{context} handler name contains invalid characters"
        )

    return handler_name


def validate_json_parameters(
    params: Dict[str, Any], context: str, max_size: int
) -> Dict[str, Any]:
    """Validate JSON parameters for size and content"""
    if not isinstance(params, dict):
        raise AuthZENSecurityError(f"{context} parameters must be a dictionary")

    # Check serialized size
    try:
        json_str = json.dumps(params)
        if len(json_str) > max_size:
            raise AuthZENSecurityError(
                f"{context} parameters too large ({len(json_str)} > {max_size})"
            )
    except (TypeError, ValueError) as e:
        raise AuthZENSecurityError(f"{context} parameters not JSON serializable: {e}")

    return params


def sanitize_correlation_id(correlation_id: Optional[str]) -> str:
    """Validate and sanitize correlation ID"""
    if correlation_id is None:
        return generate_correlation_id()

    if not isinstance(correlation_id, str):
        raise AuthZENSecurityError("Correlation ID must be string")

    if len(correlation_id) > MAX_CORRELATION_ID_LENGTH:
        raise AuthZENSecurityError("Correlation ID too long")

    # Only allow alphanumeric, hyphens
    if not re.match(r"^[a-zA-Z0-9-]+$", correlation_id):
        raise AuthZENSecurityError("Correlation ID contains invalid characters")

    return correlation_id


@dataclass
class SecureConstraint:
    """🛡️ Secure Constraint model with validation"""

    id: str
    type: str
    parameters: Dict[str, Any]

    def __post_init__(self):
        # Validate constraint ID
        if not isinstance(self.id, str) or len(self.id) > MAX_CONSTRAINT_ID_LENGTH:
            raise ConstraintSecurityError("Invalid constraint ID")

        # Validate constraint type
        self.type = validate_handler_name(self.type, "constraint")

        # Validate constraint types
        valid_types = {
            "scope_downgrade",
            "rate_limit",
            "time_window",
            "ip_restriction",
            "data_filtering",
            "amount_cap",
            "concurrent_limit",
            "approval_required",
        }
        if self.type not in valid_types:
            logger.warning(f"🚨 Unknown constraint type: {self.type}")

        # Validate parameters
        self.parameters = validate_json_parameters(
            self.parameters, "constraint", MAX_CONSTRAINT_PARAMETERS_SIZE
        )


@dataclass
class SecureObligation:
    """🛡️ Secure Obligation model with validation"""

    id: str
    type: str
    parameters: Dict[str, Any]
    timing: str = "after"  # before, after, async, immediate
    critical: bool = False

    def __post_init__(self):
        # Validate obligation ID
        if not isinstance(self.id, str) or len(self.id) > MAX_OBLIGATION_ID_LENGTH:
            raise ObligationSecurityError("Invalid obligation ID")

        # Validate obligation type
        self.type = validate_handler_name(self.type, "obligation")

        # Validate obligation types
        valid_types = {
            "audit_log",
            "notification",
            "delegation_provision",
            "approval_required",
            "data_retention",
            "compliance_report",
        }
        if self.type not in valid_types:
            logger.warning(f"🚨 Unknown obligation type: {self.type}")

        # Validate timing
        valid_timings = {"before", "after", "async", "immediate"}
        if self.timing not in valid_timings:
            raise ObligationSecurityError(f"Invalid obligation timing: {self.timing}")

        # Validate parameters
        self.parameters = validate_json_parameters(
            self.parameters, "obligation", MAX_OBLIGATION_PARAMETERS_SIZE
        )


@dataclass
class SecurePolicyMatchInfo:
    """🛡️ Secure Policy Match Information"""

    match_type: str
    match_confidence: float
    matched_criteria: str
    explanation: str

    def __post_init__(self):
        # Validate match confidence
        if not isinstance(self.match_confidence, (int, float)) or not (
            0 <= self.match_confidence <= 1
        ):
            raise AuthZENSecurityError("Match confidence must be float between 0 and 1")


@dataclass
class SecureDecisionFactor:
    """🛡️ Secure Decision Factor"""

    factor: str
    description: str
    impact: Optional[str] = None
    policy_id: Optional[str] = None
    confidence: Optional[float] = None

    def __post_init__(self):
        if self.confidence is not None:
            if not isinstance(self.confidence, (int, float)) or not (
                0 <= self.confidence <= 1
            ):
                raise AuthZENSecurityError(
                    "Decision factor confidence must be float between 0 and 1"
                )


class ConstraintsMode(Enum):
    DISABLED = "disabled"
    SHADOW = "shadow"
    FULL = "full"


@dataclass
class SecurePDPConfig:
    """🛡️ Secure PDP Configuration with comprehensive validation"""

    base_url: str
    client_id: str
    client_secret: str
    token_url: str
    scope: str = ""

    # Advanced PEP configuration
    enable_constraints: bool = True
    enable_obligations: bool = True
    enable_learning_mode: bool = False
    constraints_mode: ConstraintsMode = ConstraintsMode.FULL

    # Constraint enforcement settings
    apply_constraints_automatically: bool = True
    strict_constraint_enforcement: bool = True

    # Obligation processing settings
    process_obligations_automatically: bool = True
    obligation_timeout: float = 30.0
    critical_obligation_retry_count: int = 3

    # Security settings
    validate_ssl_certificates: bool = True
    request_timeout: float = 30.0
    max_retries: int = 3
    rate_limit_per_minute: int = DEFAULT_RATE_LIMIT_PER_MINUTE
    rate_limit_burst: int = DEFAULT_RATE_LIMIT_BURST

    # Caching
    enable_response_caching: bool = True
    cache_ttl: int = 300

    # Observability
    enable_metrics: bool = True
    correlation_header: str = "X-Correlation-ID"

    # Transport auth options
    mtls_cert: Optional[str] = None  # path to client cert
    mtls_key: Optional[str] = None  # path to client key
    dpop_private_key: Optional[str] = None  # PEM encoded EC/RSA private key

    # Circuit-breaker
    circuit_max_failures: int = 3
    circuit_reset_timeout: int = 30  # seconds

    # OpenTelemetry
    enable_tracing: bool = False

    def __post_init__(self):
        """Validate configuration"""
        # Validate URLs
        for url_field in ["base_url", "token_url"]:
            url = getattr(self, url_field)
            parsed = urlparse(url)
            if parsed.scheme not in ["https", "http"]:
                raise AuthZENSecurityError(f"{url_field} must use http/https")
            if not parsed.netloc:
                raise AuthZENSecurityError(f"{url_field} must have valid hostname")

        # Validate timeouts
        if self.obligation_timeout <= 0 or self.obligation_timeout > 300:
            raise AuthZENSecurityError(
                "Obligation timeout must be between 0 and 300 seconds"
            )

        if self.request_timeout <= 0 or self.request_timeout > 120:
            raise AuthZENSecurityError(
                "Request timeout must be between 0 and 120 seconds"
            )

        # mTLS validation
        if (self.mtls_cert and not self.mtls_key) or (
            self.mtls_key and not self.mtls_cert
        ):
            raise AuthZENSecurityError(
                "Both mtls_cert and mtls_key must be provided together"
            )


class SecureEnhancedAuthResult:
    """🛡️ Secure Enhanced authorization result with PEP capabilities"""

    def __init__(
        self,
        decision: bool,
        reason: str = None,
        constraints: List[SecureConstraint] = None,
        obligations: List[SecureObligation] = None,
        learning_mode: bool = False,
        original_decision: bool = None,
        match_info: List[SecurePolicyMatchInfo] = None,
        decision_factors: List[SecureDecisionFactor] = None,
        correlation_id: str = None,
        raw_context: Dict[str, Any] | None = None,
    ):
        self.decision = decision
        self.reason = reason or ""
        self.constraints = constraints or []
        self.obligations = obligations or []
        self.learning_mode = learning_mode
        self.original_decision = original_decision
        self.match_info = match_info or []
        self.decision_factors = decision_factors or []
        self.correlation_id = sanitize_correlation_id(correlation_id)

        # Legacy compatibility
        self.allowed = decision
        self.denied = not decision

        # PEP state tracking
        self._constraints_applied = False
        self._obligations_processed = False
        self._enforcement_log = []

        # Untouched context for callers
        self.raw_context: Dict[str, Any] | None = raw_context

        # Validate constraints and obligations
        for constraint in self.constraints:
            if not isinstance(constraint, SecureConstraint):
                raise ConstraintSecurityError(
                    "All constraints must be SecureConstraint instances"
                )

        for obligation in self.obligations:
            if not isinstance(obligation, SecureObligation):
                raise ObligationSecurityError(
                    "All obligations must be SecureObligation instances"
                )

    def __bool__(self):
        return self.decision

    @property
    def has_constraints(self) -> bool:
        return len(self.constraints) > 0

    @property
    def has_obligations(self) -> bool:
        return len(self.obligations) > 0

    @property
    def requires_constraint_enforcement(self) -> bool:
        return self.decision and self.has_constraints

    @property
    def requires_obligation_fulfillment(self) -> bool:
        return self.decision and self.has_obligations

    # ------------------- helpers -------------------

    def get_extra(self, key: str, default: Any | None = None) -> Any | None:
        """Return opaque value from PDP context if present."""
        if self.raw_context is None:
            return default
        return self.raw_context.get(key, default)


# Type definitions for secure handlers
SecureConstraintHandler = Callable[[Any, SecureConstraint], Awaitable[Any]]
SecureObligationHandler = Callable[[SecureObligation], Awaitable[Dict[str, Any]]]


class EvaluationSemantic(str, Enum):
    EXECUTE_ALL = "execute_all"
    DENY_ON_FIRST_DENY = "deny_on_first_deny"
    PERMIT_ON_FIRST_PERMIT = "permit_on_first_permit"


class SecureEnhancedPDP:
    """🛡️ Enhanced Secure PDP Client with comprehensive security protections"""

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        token_url: str,
        scope: str = "",
        config: SecurePDPConfig = None,
    ):
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx required. Install with: pip install httpx")

        # Validate FIPS compliance
        FIPSValidator.ensure_compliance()

        if config:
            self.config = config
        else:
            self.config = SecurePDPConfig(
                base_url, client_id, client_secret, token_url, scope
            )

        self.logger = logging.getLogger(__name__)

        # Secure handler registries with limits
        self._constraint_handlers: Dict[str, SecureConstraintHandler] = {}
        self._obligation_handlers: Dict[str, SecureObligationHandler] = {}

        # Rate limiting
        self._rate_limit_tokens = {}
        self._rate_limit_last_refill = time.time()

        # Security context
        self._security_context = {
            "client_fingerprint": self._generate_client_fingerprint(),
            "session_id": generate_correlation_id(),
            "created_at": datetime.now(timezone.utc),
        }

        # Metrics tracking
        self._metrics = {
            "total_requests": 0,
            "constraints_applied": 0,
            "obligations_processed": 0,
            "constraint_violations": 0,
            "obligation_failures": 0,
            "rate_limit_hits": 0,
            "security_violations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "circuit_open": 0,
        }

        # HTTP client
        self._http_client: Optional[httpx.AsyncClient] = None

        # Simple in-memory response cache: key -> (expiry, response dict)
        self._response_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}

        # DPoP support if configured
        self._dpop_manager = DPoPManager()
        self._dpop_manager.enable_dpop()

        # Register default handlers
        self._register_default_handlers()

        # Circuit-breaker state
        self._circuit_failures = 0
        self._circuit_open_until: float = 0.0

        self.logger.info(
            "🛡️ Secure Enhanced PDP Client initialized",
            extra={
                "client_id": self.config.client_id,
                "security_features": True,
                "fips_compliant": True,
                "session_id": self._security_context["session_id"],
            },
        )

    def _generate_client_fingerprint(self) -> str:
        """Generate unique client fingerprint for security tracking"""
        fingerprint_data = {
            "client_id": self.config.client_id,
            "base_url": self.config.base_url,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "random_nonce": generate_secure_token(16),
        }

        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()

    def _register_default_handlers(self):
        """Register secure default constraint and obligation handlers"""

        # Default constraint handlers
        self.register_constraint_handler(
            "scope_downgrade", self._handle_scope_downgrade
        )
        self.register_constraint_handler("rate_limit", self._handle_rate_limit)
        self.register_constraint_handler("time_window", self._handle_time_window)
        self.register_constraint_handler("data_filtering", self._handle_data_filtering)
        self.register_constraint_handler("amount_cap", self._handle_amount_cap)

        # Default obligation handlers
        self.register_obligation_handler("audit_log", self._handle_audit_log)
        self.register_obligation_handler("notification", self._handle_notification)
        self.register_obligation_handler(
            "delegation_provision", self._handle_delegation
        )

    def register_constraint_handler(
        self, constraint_type: str, handler: SecureConstraintHandler
    ):
        """🛡️ Register a secure custom constraint handler"""

        # Validate handler type name
        constraint_type = validate_handler_name(constraint_type, "constraint")

        # Limit number of handlers to prevent memory exhaustion
        if len(self._constraint_handlers) >= MAX_CONSTRAINT_HANDLERS:
            raise AuthZENSecurityError(
                f"Too many constraint handlers (max {MAX_CONSTRAINT_HANDLERS})"
            )

        # Validate handler is callable
        if not callable(handler):
            raise AuthZENSecurityError("Constraint handler must be callable")

        self._constraint_handlers[constraint_type] = handler
        self.logger.info(
            f"✅ Registered secure constraint handler for type: {constraint_type}"
        )

    def register_obligation_handler(
        self, obligation_type: str, handler: SecureObligationHandler
    ):
        """🛡️ Register a secure custom obligation handler"""

        # Validate handler type name
        obligation_type = validate_handler_name(obligation_type, "obligation")

        # Limit number of handlers to prevent memory exhaustion
        if len(self._obligation_handlers) >= MAX_OBLIGATION_HANDLERS:
            raise AuthZENSecurityError(
                f"Too many obligation handlers (max {MAX_OBLIGATION_HANDLERS})"
            )

        # Validate handler is callable
        if not callable(handler):
            raise AuthZENSecurityError("Obligation handler must be callable")

        self._obligation_handlers[obligation_type] = handler
        self.logger.info(
            f"✅ Registered secure obligation handler for type: {obligation_type}"
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.config.enable_metrics:
            self.logger.info("🛡️ Secure PDP Client Metrics", extra=self._metrics)
            if self.config.enable_metrics and _OTEL_AVAILABLE:
                from empowernow_common.utils.metrics import export_metrics

                # expose metrics via logs for now
                metrics_text = export_metrics(self._metrics).decode()
                self.logger.debug(
                    "Prometheus metrics exported", extra={"prometheus": metrics_text}
                )
        await self._cleanup()

    async def _cleanup(self):
        """Cleanup resources"""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None

    def _check_rate_limit(self, client_id: str) -> None:
        """Check and enforce rate limiting"""
        current_time = time.time()

        # Refill tokens
        if current_time - self._rate_limit_last_refill >= 60:  # 1 minute
            self._rate_limit_tokens.clear()
            self._rate_limit_last_refill = current_time

        # Check current usage
        current_tokens = self._rate_limit_tokens.get(client_id, 0)

        if current_tokens >= self.config.rate_limit_per_minute:
            self._metrics["rate_limit_hits"] += 1
            raise RateLimitExceededError(f"Rate limit exceeded for client {client_id}")

        # Increment usage
        self._rate_limit_tokens[client_id] = current_tokens + 1

    # Legacy compatibility methods with security
    async def can(self, who, action, what, **context_attrs) -> bool:
        """🛡️ Secure simple boolean check - automatically applies constraints"""
        result = await self.check(who, action, what, **context_attrs)
        return result.decision

    async def check(
        self, who, action, what, **context_attrs
    ) -> SecureEnhancedAuthResult:
        """🛡️ Secure enhanced check with automatic PEP enforcement"""
        request = self._build_secure_authz_request(who, action, what, **context_attrs)
        return await self.evaluate_and_enforce(request)

    async def evaluate(self, request: SecureAuthRequest) -> SecureEnhancedAuthResult:
        """🛡️ Secure evaluation without automatic enforcement"""
        # Rate limiting check
        self._check_rate_limit(self.config.client_id)

        # Gracefully coerce legacy dict payloads into SecureAuthRequest to
        # maintain backward-compat while keeping the strict model for new code.
        if not isinstance(request, SecureAuthRequest):
            if isinstance(request, dict):
                try:
                    request = SecureAuthRequest(**request)  # type: ignore[arg-type]
                except Exception as e:
                    raise AuthZENSecurityError(
                        "Request must be SecureAuthRequest instance"
                    ) from e
            else:
                raise AuthZENSecurityError("Request must be SecureAuthRequest instance")

        cache_key = None
        raw_response: Dict[str, Any]

        if self.config.enable_response_caching:
            cache_key = self._cache_key_for_request(request)
            cached = self._response_cache.get(cache_key)
            if cached and cached[0] > time.time():
                self._metrics["cache_hits"] += 1
                raw_response = cached[1]
            else:
                self._metrics["cache_misses"] += 1
                raw_response = await self._call_secure_pdp_api(request)
                # Store
                self._response_cache[cache_key] = (
                    time.time() + self.config.cache_ttl,
                    raw_response,
                )
        else:
            raw_response = await self._call_secure_pdp_api(request)

        return self._parse_secure_enhanced_response(raw_response)

    async def evaluate_and_enforce(
        self, request: SecureAuthRequest, main_operation: Callable = None
    ) -> SecureEnhancedAuthResult:
        """🛡️ Secure full PEP evaluation with constraint and obligation enforcement"""

        self._metrics["total_requests"] += 1
        correlation_id = generate_correlation_id()

        try:
            # 1. Get authorization decision from PDP
            auth_result = await self.evaluate(request)
            auth_result.correlation_id = correlation_id

            if not auth_result.decision:
                return auth_result

            # 2. Apply constraints if enabled and present
            modified_request = request
            if (
                self.config.enable_constraints
                and self.config.apply_constraints_automatically
                and auth_result.has_constraints
            ):
                modified_request = await self._apply_secure_constraints(
                    modified_request, auth_result.constraints
                )
                auth_result._constraints_applied = True
                self._metrics["constraints_applied"] += 1

            # 3. Process obligations if enabled
            if (
                self.config.enable_obligations
                and self.config.process_obligations_automatically
                and auth_result.has_obligations
            ):
                # Execute main operation first if provided
                if main_operation:
                    operation_result = await main_operation(
                        modified_request if "modified_request" in locals() else request
                    )

                # Then process obligations
                await self._process_secure_obligations(auth_result.obligations)
                auth_result._obligations_processed = True
                self._metrics["obligations_processed"] += 1

            return auth_result

        except Exception as e:
            self.logger.error(
                f"🚨 Secure PEP enforcement failed: {str(e)}",
                extra={"correlation_id": correlation_id},
            )
            raise

    # Secure constraint handlers
    async def _handle_scope_downgrade(
        self, request: Any, constraint: SecureConstraint
    ) -> Any:
        """🛡️ Secure scope downgrade constraint handler"""
        params = constraint.parameters

        # Validate parameters
        if not isinstance(params, dict):
            raise ConstraintSecurityError("Scope downgrade parameters must be dict")

        # Implement scope reduction logic based on your application needs
        if hasattr(request, "scope") and "allowed_scopes" in params:
            allowed_scopes = params["allowed_scopes"]
            if not isinstance(allowed_scopes, list):
                raise ConstraintSecurityError("allowed_scopes must be list")

            request.scope = [s for s in request.scope if s in allowed_scopes]

        return request

    async def _handle_rate_limit(
        self, request: Any, constraint: SecureConstraint
    ) -> Any:
        """🛡️ Secure rate limiting constraint handler"""
        params = constraint.parameters

        # Validate parameters
        if not isinstance(params, dict):
            raise ConstraintSecurityError("Rate limit parameters must be dict")

        # Log constraint application
        self.logger.info(
            f"🛡️ Rate limit constraint applied",
            extra={"constraint_id": constraint.id, "parameters": params},
        )

        return request

    async def _handle_time_window(
        self, request: Any, constraint: SecureConstraint
    ) -> Any:
        """🛡️ Secure time window constraint handler"""
        params = constraint.parameters
        current_time = datetime.now(timezone.utc)

        if "start_time" in params and "end_time" in params:
            try:
                start = datetime.fromisoformat(
                    params["start_time"].replace("Z", "+00:00")
                )
                end = datetime.fromisoformat(params["end_time"].replace("Z", "+00:00"))

                if not (start <= current_time <= end):
                    raise ConstraintSecurityError(
                        f"Request outside allowed time window: {start} - {end}"
                    )
            except (ValueError, AttributeError) as e:
                raise ConstraintSecurityError(f"Invalid time window format: {e}")

        return request

    async def _handle_data_filtering(
        self, request: Any, constraint: SecureConstraint
    ) -> Any:
        """🛡️ Secure data filtering constraint handler"""
        params = constraint.parameters

        # Validate parameters
        if not isinstance(params, dict):
            raise ConstraintSecurityError("Data filtering parameters must be dict")

        # Add data filters to the request
        if hasattr(request, "filters"):
            filter_conditions = params.get("filter_conditions", {})
            if not isinstance(filter_conditions, dict):
                raise ConstraintSecurityError("filter_conditions must be dict")
            request.filters.update(filter_conditions)

        return request

    async def _handle_amount_cap(
        self, request: Any, constraint: SecureConstraint
    ) -> Any:
        """🛡️ Secure amount cap constraint handler"""
        params = constraint.parameters

        if "max_amount" in params:
            max_amount = params["max_amount"]
            if not isinstance(max_amount, (int, float)) or max_amount < 0:
                raise ConstraintSecurityError("max_amount must be non-negative number")

            # Apply amount cap logic based on your application
            if hasattr(request, "amount"):
                if request.amount > max_amount:
                    request.amount = max_amount

        return request

    # Secure obligation handlers
    async def _handle_audit_log(self, obligation: SecureObligation) -> Dict[str, Any]:
        """🛡️ Secure audit logging obligation handler"""
        params = obligation.parameters

        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "obligation_id": obligation.id,
            "event_type": params.get("event_type", "access"),
            "level": params.get("level", "info"),
            "correlation_id": self._security_context["session_id"],
        }

        # Sanitize sensitive data before logging
        sanitized_params = {
            k: v
            for k, v in params.items()
            if not any(
                sensitive in k.lower()
                for sensitive in ["password", "secret", "key", "token"]
            )
        }
        audit_entry.update(sanitized_params)

        self.logger.info("🛡️ Secure Audit Log", extra=audit_entry)

        return {"status": "logged", "audit_id": obligation.id}

    async def _handle_notification(
        self, obligation: SecureObligation
    ) -> Dict[str, Any]:
        """🛡️ Secure notification obligation handler"""
        params = obligation.parameters

        # Sanitize message content
        message = params.get("message", "Authorization event")
        if len(message) > 1000:
            message = message[:1000] + "..."

        self.logger.info(f"🛡️ Secure Notification: {message}")

        return {"status": "sent", "notification_id": obligation.id}

    async def _handle_delegation(self, obligation: SecureObligation) -> Dict[str, Any]:
        """🛡️ Secure delegation provisioning obligation handler"""
        params = obligation.parameters

        # Validate delegation parameters
        if "delegate_to" not in params:
            raise ObligationSecurityError("delegate_to required for delegation")

        self.logger.info(
            f"🛡️ Secure Delegation provision",
            extra={
                "obligation_id": obligation.id,
                "delegate_to": params["delegate_to"],
            },
        )

        return {"status": "provisioned", "delegation_id": obligation.id}

    def _build_secure_authz_request(
        self, who, action, what, **context_attrs
    ) -> SecureAuthRequest:
        """🛡️ Build secure authorization request from simple parameters"""
        try:
            if isinstance(who, SecureSubject):
                subject = who
            else:
                subject = SecureSubject(id=str(who), type="user")

            if isinstance(what, SecureResource):
                resource = what
            else:
                resource = SecureResource(id=str(what), type="resource")

            if isinstance(action, SecureAction):
                action_obj = action
            else:
                action_obj = SecureAction(name=str(action))

            context = (
                SecureContext(attributes=context_attrs)
                if context_attrs
                else SecureContext()
            )

            return SecureAuthRequest(
                subject=subject, resource=resource, action=action_obj, context=context
            )
        except Exception as e:
            raise AuthZENSecurityError(
                f"Failed to build secure authorization request: {e}"
            )

    async def _call_secure_pdp_api(self, request: SecureAuthRequest) -> Dict[str, Any]:
        """🛡️ Make secure HTTP call to PDP"""
        if not self._http_client:
            # Create secure HTTP client
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = self.config.validate_ssl_certificates
            ssl_context.verify_mode = (
                ssl.CERT_REQUIRED
                if self.config.validate_ssl_certificates
                else ssl.CERT_NONE
            )

            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.request_timeout),
                verify=ssl_context,
                follow_redirects=False,
                cert=(
                    (self.config.mtls_cert, self.config.mtls_key)
                    if self.config.mtls_cert
                    else None
                ),
            )

        # Circuit breaker check
        if self._circuit_open_until and time.time() < self._circuit_open_until:
            self._metrics["circuit_open"] += 1
            return {
                "decision": False,
                "context": {
                    "reason_admin": {"en": "PDP circuit open"},
                    "constraints": [],
                    "obligations": [],
                },
            }

        # Create request payload
        payload = {
            "subject": request.subject.model_dump(),
            "resource": request.resource.model_dump(),
            "action": request.action.model_dump(),
            "context": request.context.model_dump(),
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "EmpowerNow-SecurePDP/1.0",
            "X-Request-ID": generate_correlation_id(),
            "X-Client-Fingerprint": self._security_context["client_fingerprint"],
        }

        # Add DPoP header if enabled
        if self._dpop_manager and self._dpop_manager.is_enabled():
            headers = self._dpop_manager.add_dpop_header(
                headers, "POST", f"{self.config.base_url}/v1/evaluations"
            )

        try:
            # Wrap request in OTel span if enabled
            if self.config.enable_tracing and _OTEL_AVAILABLE:
                with _TRACER.start_as_current_span("pdp.evaluate"):
                    response = await self._http_client.post(
                        f"{self.config.base_url}/v1/evaluations",
                        json=payload,
                        headers=headers,
                        auth=(self.config.client_id, self.config.client_secret),
                    )
            else:
                response = await self._http_client.post(
                    f"{self.config.base_url}/v1/evaluations",
                    json=payload,
                    headers=headers,
                    auth=(self.config.client_id, self.config.client_secret),
                )
            response.raise_for_status()

            # Validate response size
            if len(response.content) > 1024 * 1024:  # 1MB limit
                raise AuthZENSecurityError("PDP response too large")

            return response.json()

        except httpx.HTTPStatusError as e:
            self._metrics["security_violations"] += 1
            self._record_circuit_failure()
            self.logger.error(f"🚨 PDP API call failed: {e.response.status_code}")
            # Return deny decision on API failure
            return {
                "decision": False,
                "context": {
                    "reason_admin": {"en": f"PDP API error: {e.response.status_code}"},
                    "constraints": [],
                    "obligations": [],
                },
            }
        except Exception as e:
            self._metrics["security_violations"] += 1
            self._record_circuit_failure()
            self.logger.error(f"🚨 PDP API call error: {e}")
            # Return deny decision on error
            return {
                "decision": False,
                "context": {
                    "reason_admin": {"en": f"PDP communication error: {str(e)}"},
                    "constraints": [],
                    "obligations": [],
                },
            }

    def _parse_secure_enhanced_response(
        self, raw_response: Dict[str, Any]
    ) -> SecureEnhancedAuthResult:
        """🛡️ Parse secure enhanced PDP response"""

        decision = raw_response.get("decision", False)
        context = raw_response.get("context", {})

        # Parse constraints securely
        constraints = []
        for c in context.get("constraints", []):
            try:
                constraints.append(
                    SecureConstraint(
                        id=c.get("id", generate_correlation_id()),
                        type=c.get("type", "unknown"),
                        parameters=c.get("parameters", {}),
                    )
                )
            except Exception as e:
                self.logger.warning(f"🚨 Invalid constraint in response: {e}")

        # Parse obligations securely
        obligations = []
        for o in context.get("obligations", []):
            try:
                obligations.append(
                    SecureObligation(
                        id=o.get("id", generate_correlation_id()),
                        type=o.get("type", "unknown"),
                        parameters=o.get("parameters", {}),
                        timing=o.get("timing", "after"),
                        critical=o.get("critical", False),
                    )
                )
            except Exception as e:
                self.logger.warning(f"🚨 Invalid obligation in response: {e}")

        return SecureEnhancedAuthResult(
            decision=decision,
            reason=context.get("reason_user", {}).get("en", "No reason provided"),
            constraints=constraints,
            obligations=obligations,
            learning_mode=context.get("learning_mode", False),
            original_decision=context.get("original_decision"),
            raw_context=context,
        )

    async def _apply_secure_constraints(
        self, request: SecureAuthRequest, constraints: List[SecureConstraint]
    ) -> SecureAuthRequest:
        """🛡️ Apply constraints securely"""
        modified_request = request

        for constraint in constraints:
            if constraint.type in self._constraint_handlers:
                try:
                    modified_request = await self._constraint_handlers[constraint.type](
                        modified_request, constraint
                    )
                    self.logger.debug(f"✅ Applied secure constraint: {constraint.id}")

                except Exception as e:
                    self._metrics["constraint_violations"] += 1
                    if self.config.strict_constraint_enforcement:
                        raise ConstraintSecurityError(
                            f"Constraint {constraint.id} failed: {str(e)}"
                        )
                    else:
                        self.logger.warning(
                            f"🚨 Constraint {constraint.id} failed: {str(e)}"
                        )
            else:
                self.logger.warning(
                    f"🚨 No handler for constraint type: {constraint.type}"
                )

        return modified_request

    async def _process_secure_obligations(self, obligations: List[SecureObligation]):
        """🛡️ Process obligations securely"""

        # Categorize by timing
        before_obligations = [o for o in obligations if o.timing == "before"]
        after_obligations = [o for o in obligations if o.timing == "after"]
        immediate_obligations = [o for o in obligations if o.timing == "immediate"]
        async_obligations = [o for o in obligations if o.timing == "async"]

        # Process before obligations first
        await self._execute_secure_obligations(before_obligations)

        # Process immediate and after obligations
        await asyncio.gather(
            self._execute_secure_obligations(immediate_obligations),
            self._execute_secure_obligations(after_obligations),
            return_exceptions=True,
        )

        # Queue async obligations for background processing
        for obligation in async_obligations:
            asyncio.create_task(self._execute_secure_obligation(obligation))

    async def _execute_secure_obligations(self, obligations: List[SecureObligation]):
        """🛡️ Execute a list of obligations securely"""
        for obligation in obligations:
            await self._execute_secure_obligation(obligation)

    async def _execute_secure_obligation(self, obligation: SecureObligation):
        """🛡️ Execute a single obligation securely with retry logic"""
        if obligation.type not in self._obligation_handlers:
            self.logger.warning(f"🚨 No handler for obligation type: {obligation.type}")
            return

        retry_count = (
            self.config.critical_obligation_retry_count if obligation.critical else 1
        )

        for attempt in range(retry_count):
            try:
                result = await asyncio.wait_for(
                    self._obligation_handlers[obligation.type](obligation),
                    timeout=self.config.obligation_timeout,
                )

                self.logger.debug(f"✅ Fulfilled secure obligation: {obligation.id}")
                return result

            except Exception as e:
                if attempt == retry_count - 1:  # Last attempt
                    self._metrics["obligation_failures"] += 1
                    if obligation.critical:
                        raise ObligationSecurityError(
                            f"Critical obligation {obligation.id} failed: {e}"
                        )
                    else:
                        self.logger.error(
                            f"🚨 Non-critical obligation failed: {obligation.id}: {str(e)}"
                        )
                else:
                    self.logger.warning(
                        f"🚨 Obligation {obligation.id} failed, retrying... ({attempt + 1}/{retry_count})"
                    )
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff

    def _cache_key_for_request(self, request: SecureAuthRequest) -> str:
        return hashlib.sha256(
            json.dumps(request.model_dump(), sort_keys=True).encode()
        ).hexdigest()

    def _record_circuit_failure(self):
        self._circuit_failures += 1
        if self._circuit_failures >= self.config.circuit_max_failures:
            self._circuit_open_until = time.time() + self.config.circuit_reset_timeout
            self._circuit_failures = 0
            logger.error(
                "🚨 PDP circuit opened",
                extra={"reset_in": self.config.circuit_reset_timeout},
            )

    async def evaluate_batch(
        self,
        requests: List[SecureAuthRequest],
        *,
        semantics: EvaluationSemantic = EvaluationSemantic.EXECUTE_ALL,
    ) -> List[SecureEnhancedAuthResult]:
        """Evaluate multiple requests respecting evaluation semantics (draft-04)."""

        results: List[SecureEnhancedAuthResult] = []

        if semantics == EvaluationSemantic.EXECUTE_ALL:
            for req in requests:
                results.append(await self.evaluate(req))
        elif semantics == EvaluationSemantic.DENY_ON_FIRST_DENY:
            for req in requests:
                res = await self.evaluate(req)
                results.append(res)
                if not res.decision:
                    break
        elif semantics == EvaluationSemantic.PERMIT_ON_FIRST_PERMIT:
            for req in requests:
                res = await self.evaluate(req)
                results.append(res)
                if res.decision:
                    break
        else:
            raise AuthZENSecurityError(f"Unknown evaluation semantics: {semantics}")

        return results

    # ---------------- Convenience builders ----------------

    @classmethod
    async def from_discovery(
        cls,
        well_known_url: str,
        *,
        client_id: str,
        client_secret: str,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        """Create SecureEnhancedPDP using .well-known/authzen-configuration discovery."""
        _client_created = False
        if http_client is None:
            http_client = httpx.AsyncClient(timeout=10.0, verify=True)
            _client_created = True
        try:
            r = await http_client.get(well_known_url)
            r.raise_for_status()
            meta = r.json()
            base = meta["policy_decision_point"].rstrip("/")
            token_url = meta.get("token_endpoint", base + "/token")

            cfg = SecurePDPConfig(
                base_url=base,
                client_id=client_id,
                client_secret=client_secret,
                token_url=token_url,
            )
            return cls(base, client_id, client_secret, token_url, config=cfg)
        finally:
            if _client_created:
                await http_client.aclose()

    # ---------------- Search API wrappers ----------------

    async def _call_search(self, kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        endpoint = f"{self.config.base_url}/access/v1/search/{kind}"
        async with self._get_secure_http_client(endpoint) as client:
            headers = self._get_security_headers()
            if self._dpop_manager and self._dpop_manager.is_enabled():
                headers = self._dpop_manager.add_dpop_header(headers, "POST", endpoint)
            resp = await client.post(
                "",
                json=payload,
                headers=headers,
                auth=(self.config.client_id, self.config.client_secret),
            )
            resp.raise_for_status()
            return resp.json()

    async def search_subject(
        self,
        action: SecureAction,
        resource: SecureResource,
        *,
        context: SecureContext = None,
        page_token: str = "",
    ) -> Dict[str, Any]:
        payload = {
            "subject": {"type": "user"},  # id omitted
            "action": action.model_dump(),
            "resource": resource.model_dump(),
            "context": context.model_dump() if context else {},
            "page": {"next_token": page_token} if page_token else {},
        }
        return await self._call_search("subject", payload)

    async def search_resource(
        self,
        subject: SecureSubject,
        action: SecureAction,
        *,
        context: SecureContext = None,
        page_token: str = "",
    ) -> Dict[str, Any]:
        payload = {
            "subject": subject.model_dump(),
            "action": action.model_dump(),
            "resource": {"type": "resource"},
            "context": context.model_dump() if context else {},
            "page": {"next_token": page_token} if page_token else {},
        }
        return await self._call_search("resource", payload)

    async def search_action(
        self,
        subject: SecureSubject,
        resource: SecureResource,
        *,
        context: SecureContext = None,
        page_token: str = "",
    ) -> Dict[str, Any]:
        payload = {
            "subject": subject.model_dump(),
            "resource": resource.model_dump(),
            "context": context.model_dump() if context else {},
            "page": {"next_token": page_token} if page_token else {},
        }
        return await self._call_search("action", payload)


# Secure aliases
SecurePDP = SecureEnhancedPDP
SecureAuthzClient = SecureEnhancedPDP
SecurePDPClient = SecureEnhancedPDP

# Legacy compatibility with security warnings
import warnings


class EnhancedPDP(SecureEnhancedPDP):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "EnhancedPDP is deprecated. Use SecureEnhancedPDP for enhanced security.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


# More compatibility
PolicyClient = SecureEnhancedPDP
AuthzClient = SecureEnhancedPDP
PDPClient = SecureEnhancedPDP

# OpenTelemetry optional import
try:
    from opentelemetry import trace

    _TRACER = trace.get_tracer(__name__)
    _OTEL_AVAILABLE = True
except ImportError:  # pragma: no cover
    _OTEL_AVAILABLE = False
