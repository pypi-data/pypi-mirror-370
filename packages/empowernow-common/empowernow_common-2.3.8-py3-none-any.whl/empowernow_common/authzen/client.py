"""Enhanced PDP Client with Policy Enforcement Point capabilities"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union, List, Callable, Awaitable
from enum import Enum
import logging
import asyncio
import time
from datetime import datetime, timedelta

from .models import Subject, Resource, Action, Context, AuthRequest, AuthResponse
from ..exceptions import EmpowerNowError


# Enhanced models for advanced PDP features
@dataclass
class Constraint:
    id: str
    type: str
    parameters: Dict[str, Any]

    def __post_init__(self):
        # Validate constraint types
        valid_types = [
            "scope_downgrade",
            "rate_limit",
            "time_window",
            "ip_restriction",
            "data_filtering",
            "amount_cap",
        ]
        if self.type not in valid_types:
            logging.warning(f"Unknown constraint type: {self.type}")


@dataclass
class Obligation:
    id: str
    type: str
    parameters: Dict[str, Any]
    timing: str = "after"  # before, after, async, immediate
    critical: bool = False

    def __post_init__(self):
        valid_types = [
            "audit_log",
            "notification",
            "delegation_provision",
            "approval_required",
            "data_retention",
        ]
        if self.type not in valid_types:
            logging.warning(f"Unknown obligation type: {self.type}")


@dataclass
class PolicyMatchInfo:
    match_type: str  # direct, role_based, group_based, attribute_based
    match_confidence: float
    matched_criteria: str
    explanation: str


@dataclass
class DecisionFactor:
    factor: str
    description: str
    impact: Optional[str] = None
    policy_id: Optional[str] = None
    confidence: Optional[float] = None


class ConstraintsMode(Enum):
    DISABLED = "disabled"
    SHADOW = "shadow"
    FULL = "full"


@dataclass
class PDPConfig:
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

    # Caching
    enable_response_caching: bool = True
    cache_ttl: int = 300

    # Observability
    enable_metrics: bool = True
    correlation_header: str = "X-Correlation-ID"


class PDPError(EmpowerNowError):
    pass


class ConstraintViolationError(PDPError):
    def __init__(self, constraint: Constraint, message: str):
        self.constraint = constraint
        super().__init__(f"Constraint {constraint.id} violated: {message}")


class CriticalObligationFailure(PDPError):
    def __init__(self, obligation_id: str, error: Exception):
        self.obligation_id = obligation_id
        self.original_error = error
        super().__init__(f"Critical obligation {obligation_id} failed: {error}")


class EnhancedAuthResult:
    """Enhanced authorization result with PEP capabilities"""

    def __init__(
        self,
        decision: bool,
        reason: str = None,
        constraints: List[Constraint] = None,
        obligations: List[Obligation] = None,
        learning_mode: bool = False,
        original_decision: bool = None,
        match_info: List[PolicyMatchInfo] = None,
        decision_factors: List[DecisionFactor] = None,
        correlation_id: str = None,
        raw_context: Dict[str, Any] | None = None,
        decoded_extras: Dict[str, Any] | None = None,
    ):
        self.decision = decision
        self.reason = reason
        self.constraints = constraints or []
        self.obligations = obligations or []
        self.learning_mode = learning_mode
        self.original_decision = original_decision
        self.match_info = match_info or []
        self.decision_factors = decision_factors or []
        self.correlation_id = correlation_id

        # Legacy compatibility
        self.allowed = decision
        self.denied = not decision

        # PEP state tracking
        self._constraints_applied = False
        self._obligations_processed = False
        self._enforcement_log = []

        # Store untouched context for forward-compatibility
        self.raw_context: Dict[str, Any] | None = raw_context

        self.decoded_extras: Dict[str, Any] = decoded_extras or {}

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

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def get_extra(self, key: str, default: Any | None = None) -> Any | None:
        """Return arbitrary key from original context if present.

        This allows callers to retrieve vendor-specific extensions without
        the SDK needing to understand them a priori.
        """
        if self.raw_context is None:
            return default
        return self.raw_context.get(key, default)

    def get_decoded(self, key: str, default: Any | None = None) -> Any | None:
        """Return value produced by context decoders if present."""
        return self.decoded_extras.get(key, default)


# Type definitions for constraint and obligation handlers
ConstraintHandler = Callable[[Any, Constraint], Awaitable[Any]]
ObligationHandler = Callable[[Obligation], Awaitable[Dict[str, Any]]]


class EnhancedPDP:
    """Enhanced PDP Client with Policy Enforcement Point capabilities"""

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        token_url: str,
        scope: str = "",
        config: PDPConfig = None,
    ):
        if config:
            self.config = config
        else:
            self.config = PDPConfig(
                base_url, client_id, client_secret, token_url, scope
            )

        self.logger = logging.getLogger(__name__)

        # PEP capability registries
        self._constraint_handlers: Dict[str, ConstraintHandler] = {}
        self._obligation_handlers: Dict[str, ObligationHandler] = {}

        # Metrics tracking
        self._metrics = {
            "total_requests": 0,
            "constraints_applied": 0,
            "obligations_processed": 0,
            "constraint_violations": 0,
            "obligation_failures": 0,
        }

        # Register default handlers
        self._register_default_handlers()

        # Context decoders – map key -> callable(value) → decoded
        self._context_decoders: Dict[str, Callable[[Any], Any]] = {}

    def _register_default_handlers(self):
        """Register default constraint and obligation handlers"""

        # Default constraint handlers
        self.register_constraint_handler(
            "scope_downgrade", self._handle_scope_downgrade
        )
        self.register_constraint_handler("rate_limit", self._handle_rate_limit)
        self.register_constraint_handler("time_window", self._handle_time_window)
        self.register_constraint_handler("data_filtering", self._handle_data_filtering)

        # Default obligation handlers
        self.register_obligation_handler("audit_log", self._handle_audit_log)
        self.register_obligation_handler("notification", self._handle_notification)
        self.register_obligation_handler(
            "delegation_provision", self._handle_delegation
        )

    def register_constraint_handler(
        self, constraint_type: str, handler: ConstraintHandler
    ):
        """Register a custom constraint handler"""
        self._constraint_handlers[constraint_type] = handler
        self.logger.info(f"Registered constraint handler for type: {constraint_type}")

    def register_obligation_handler(
        self, obligation_type: str, handler: ObligationHandler
    ):
        """Register a custom obligation handler"""
        self._obligation_handlers[obligation_type] = handler
        self.logger.info(f"Registered obligation handler for type: {obligation_type}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.config.enable_metrics:
            self.logger.info("PDP Client Metrics", extra=self._metrics)

    # Legacy compatibility methods
    async def can(self, who, action, what, **context_attrs) -> bool:
        """Simple boolean check - automatically applies constraints"""
        result = await self.check(who, action, what, **context_attrs)
        return result.decision

    async def check(self, who, action, what, **context_attrs) -> EnhancedAuthResult:
        """Enhanced check with automatic PEP enforcement"""
        request = self._build_authz_request(who, action, what, **context_attrs)
        return await self.evaluate_and_enforce(request)

    async def evaluate(self, request) -> EnhancedAuthResult:
        """Basic evaluation without automatic enforcement"""
        # TODO: Implement actual PDP API call
        # This would make the HTTP request to your PDP
        raw_response = await self._call_pdp_api(request)
        return self._parse_enhanced_response(raw_response)

    async def evaluate_and_enforce(
        self, request, main_operation: Callable = None
    ) -> EnhancedAuthResult:
        """Full PEP evaluation with constraint and obligation enforcement"""

        self._metrics["total_requests"] += 1
        correlation_id = self._generate_correlation_id()

        try:
            # 1. Get authorization decision from PDP
            auth_result = await self.evaluate(request)
            auth_result.correlation_id = correlation_id

            if not auth_result.decision:
                return auth_result

            # Ensure modified_request is always defined to avoid lint errors
            modified_request = request

            # 2. Apply constraints if enabled and present
            if (
                self.config.enable_constraints
                and self.config.apply_constraints_automatically
                and auth_result.has_constraints
            ):
                modified_request = await self._apply_constraints(
                    request, auth_result.constraints
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
                    operation_result = await main_operation(modified_request)

                # Then process obligations
                await self._process_obligations(auth_result.obligations)
                auth_result._obligations_processed = True
                self._metrics["obligations_processed"] += 1

            return auth_result

        except Exception as e:
            self.logger.error(
                f"PEP enforcement failed: {str(e)}",
                extra={"correlation_id": correlation_id},
            )
            raise

    async def _apply_constraints(
        self, request: Any, constraints: List[Constraint]
    ) -> Any:
        """Apply constraints to modify the request"""
        modified_request = request

        for constraint in constraints:
            if constraint.type in self._constraint_handlers:
                try:
                    modified_request = await self._constraint_handlers[constraint.type](
                        modified_request, constraint
                    )
                    self.logger.debug(f"Applied constraint: {constraint.id}")

                except Exception as e:
                    self._metrics["constraint_violations"] += 1
                    if self.config.strict_constraint_enforcement:
                        raise ConstraintViolationError(constraint, str(e))
                    else:
                        self.logger.warning(
                            f"Constraint {constraint.id} failed: {str(e)}"
                        )
            else:
                self.logger.warning(
                    f"No handler for constraint type: {constraint.type}"
                )

        return modified_request

    async def _process_obligations(self, obligations: List[Obligation]):
        """Process obligations based on their timing requirements"""

        # Categorize by timing
        before_obligations = [o for o in obligations if o.timing == "before"]
        after_obligations = [o for o in obligations if o.timing == "after"]
        immediate_obligations = [o for o in obligations if o.timing == "immediate"]
        async_obligations = [o for o in obligations if o.timing == "async"]

        # Process before obligations first
        await self._execute_obligations(before_obligations)

        # Process immediate and after obligations
        await asyncio.gather(
            self._execute_obligations(immediate_obligations),
            self._execute_obligations(after_obligations),
        )

        # Queue async obligations for background processing
        for obligation in async_obligations:
            asyncio.create_task(self._execute_obligation(obligation))

    async def _execute_obligations(self, obligations: List[Obligation]):
        """Execute a list of obligations"""
        for obligation in obligations:
            await self._execute_obligation(obligation)

    async def _execute_obligation(self, obligation: Obligation):
        """Execute a single obligation with retry logic"""
        if obligation.type not in self._obligation_handlers:
            self.logger.warning(f"No handler for obligation type: {obligation.type}")
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

                self.logger.debug(f"Fulfilled obligation: {obligation.id}")
                return result

            except Exception as e:
                if attempt == retry_count - 1:  # Last attempt
                    self._metrics["obligation_failures"] += 1
                    if obligation.critical:
                        raise CriticalObligationFailure(obligation.id, e)
                    else:
                        self.logger.error(
                            f"Non-critical obligation failed: {obligation.id}: {str(e)}"
                        )
                else:
                    self.logger.warning(
                        f"Obligation {obligation.id} failed, retrying... ({attempt + 1}/{retry_count})"
                    )
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff

    # Default constraint handlers
    async def _handle_scope_downgrade(
        self, request: Any, constraint: Constraint
    ) -> Any:
        """Handle scope downgrade constraints"""
        params = constraint.parameters

        # Implement scope reduction logic based on your application needs
        if hasattr(request, "scope") and "allowed_scopes" in params:
            request.scope = [s for s in request.scope if s in params["allowed_scopes"]]

        if hasattr(request, "fields") and "allowed_fields" in params:
            request.fields = [
                f for f in request.fields if f in params["allowed_fields"]
            ]

        return request

    async def _handle_rate_limit(self, request: Any, constraint: Constraint) -> Any:
        """Handle rate limiting constraints"""
        # This would typically check against a Redis cache or similar
        # For now, just log the constraint
        self.logger.info(f"Rate limit constraint applied: {constraint.parameters}")
        return request

    async def _handle_time_window(self, request: Any, constraint: Constraint) -> Any:
        """Handle time window constraints"""
        params = constraint.parameters
        current_time = datetime.now()

        if "start_time" in params and "end_time" in params:
            start = datetime.fromisoformat(params["start_time"])
            end = datetime.fromisoformat(params["end_time"])

            if not (start <= current_time <= end):
                raise ConstraintViolationError(
                    constraint, f"Request outside allowed time window: {start} - {end}"
                )

        return request

    async def _handle_data_filtering(self, request: Any, constraint: Constraint) -> Any:
        """Handle data filtering constraints"""
        params = constraint.parameters

        # Add data filters to the request
        if hasattr(request, "filters"):
            request.filters.update(params.get("filter_conditions", {}))

        return request

    # Default obligation handlers
    async def _handle_audit_log(self, obligation: Obligation) -> Dict[str, Any]:
        """Handle audit logging obligations"""
        params = obligation.parameters

        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "obligation_id": obligation.id,
            "event_type": params.get("event_type", "access"),
            "level": params.get("level", "info"),
            "user_id": params.get("user_id"),
            "resource_id": params.get("resource_id"),
            "action": params.get("action"),
        }

        # TODO: Send to actual audit system
        self.logger.info("Audit Log", extra=audit_entry)

        return {"status": "logged", "audit_id": obligation.id}

    async def _handle_notification(self, obligation: Obligation) -> Dict[str, Any]:
        """Handle notification obligations"""
        params = obligation.parameters

        # TODO: Send actual notification
        self.logger.info(
            f"Notification: {params.get('message', 'Authorization event')}"
        )

        return {"status": "sent", "notification_id": obligation.id}

    async def _handle_delegation(self, obligation: Obligation) -> Dict[str, Any]:
        """Handle delegation provisioning obligations"""
        params = obligation.parameters

        # TODO: Call delegation service
        self.logger.info(f"Delegation provision: {params}")

        return {"status": "provisioned", "delegation_id": obligation.id}

    def _build_authz_request(self, who, action, what, **context_attrs):
        """Build authorization request from simple parameters"""
        return {
            "subject": {"id": str(who)} if isinstance(who, (str, int)) else who,
            "action": {"name": str(action)} if isinstance(action, str) else action,
            "resource": {"id": str(what)} if isinstance(what, (str, int)) else what,
            "context": context_attrs,
        }

    async def _call_pdp_api(self, request, *, path: str = "/v1/evaluation"):
        """Make an HTTPS call to the PDP Evaluation endpoint (draft-04 compliant).

        This implementation fulfils the minimal AuthZEN draft-04 requirements:
        • POSTs the four-tuple JSON payload to  <base_url>/v1/evaluation
        • Adds a correlation-id header (configurable) and propagates it back
        • Uses a shared httpx.AsyncClient with connection pooling & timeouts
        • Performs up-to‐three retries on network errors / 5xx responses
        • Translates transport problems into PDPError while defaulting to
          a closed (deny) decision if recovery is impossible.
        """
        import httpx
        import asyncio
        import ssl
        from typing import Dict, Any

        # Lazily create a single AsyncClient – keeps connection pool across calls
        if not hasattr(self, "_http_client") or self._http_client is None:
            # Accept both http and https; validate certs only for https
            verify_ctx: ssl.SSLContext | bool
            if self.config.base_url.startswith("https://"):
                verify_ctx = ssl.create_default_context()
            else:
                verify_ctx = False  # explicit False disables TLS validation for http

            self._http_client = httpx.AsyncClient(
                base_url=self.config.base_url.rstrip("/"),
                timeout=httpx.Timeout(
                    connect=5.0,
                    read=self.config.obligation_timeout,
                    write=5.0,
                    pool=self.config.obligation_timeout,
                ),
                verify=verify_ctx,
                follow_redirects=False,
            )

        # Compose payload from existing dict or Pydantic model
        if hasattr(request, "model_dump"):
            payload: Dict[str, Any] = request.model_dump(mode="json", exclude_none=True)  # type: ignore
        else:
            # _build_authz_request already returns the four-tuple dict
            payload = request  # type: ignore[assignment]

        # Correlation-id header
        correlation_id = self._generate_correlation_id()
        headers = {
            "Content-Type": "application/json",
            self.config.correlation_header: correlation_id,
        }

        # Obtain OAuth2 access token via client credentials flow (cached)
        try:
            token = await self._get_access_token()
            headers["Authorization"] = f"Bearer {token}"
        except Exception as e:
            self.logger.warning(f"could not obtain access token: {e}; falling back to client_secret as bearer")
            headers["Authorization"] = f"Bearer {self.config.client_secret}"

        url_path = path

        last_exc: Exception | None = None
        for attempt in range(3):  # simple retry loop
            try:
                resp = await self._http_client.post(url_path, json=payload, headers=headers)
                # Raise for 4xx/5xx so we can handle below
                resp.raise_for_status()

                # Echo correlation id back onto response (if PDP changed it we still track original)
                resp_correlation = resp.headers.get(self.config.correlation_header, correlation_id)

                data = resp.json()
                # Inject correlation into context for later debugging
                if "context" not in data:
                    data["context"] = {}
                data["context"][self.config.correlation_header] = resp_correlation

                return data
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout, httpx.RemoteProtocolError) as exc:
                last_exc = exc
                await asyncio.sleep(0.3 * (attempt + 1))  # back-off before retry
                continue
            except httpx.HTTPStatusError as exc:
                # 4xx means caller error – do not retry; 5xx may be retryable
                if 500 <= exc.response.status_code < 600 and attempt < 2:
                    last_exc = exc
                    await asyncio.sleep(0.3 * (attempt + 1))
                    continue
                # Convert to PDPError and close decision
                self.logger.error(
                    "PDP HTTP error", extra={"status": exc.response.status_code}
                )
                return {
                    "decision": False,
                    "context": {
                        "reason_admin": {"en": f"PDP HTTP {exc.response.status_code}"},
                        "constraints": [],
                        "obligations": [],
                    },
                }

        # If we fall through retries → deny by default (fail-closed)
        self.logger.error("PDP unreachable after retries", exc_info=last_exc)
        return {
            "decision": False,
            "context": {
                "reason_admin": {"en": "PDP communication failure"},
                "constraints": [],
                "obligations": [],
            },
        }

    def _parse_enhanced_response(
        self, raw_response: Dict[str, Any]
    ) -> EnhancedAuthResult:
        """Parse enhanced PDP response into EnhancedAuthResult"""

        decision = raw_response.get("decision", False)
        context = raw_response.get("context", {})

        # Parse constraints
        constraints = []
        for c in context.get("constraints", []):
            constraints.append(
                Constraint(
                    id=c.get("id"),
                    type=c.get("type"),
                    parameters=c.get("parameters", {}),
                )
            )

        # Parse obligations
        obligations = []
        for o in context.get("obligations", []):
            obligations.append(
                Obligation(
                    id=o.get("id"),
                    type=o.get("type"),
                    parameters=o.get("parameters", {}),
                    timing=o.get("timing", "after"),
                    critical=o.get("critical", False),
                )
            )

        # Parse policy match info
        match_info = []
        for m in context.get("policy_impacts", []):
            match_info.append(
                PolicyMatchInfo(
                    match_type=m.get("match_type", "unknown"),
                    match_confidence=m.get("match_confidence", 0.0),
                    matched_criteria=m.get("matched_criteria", ""),
                    explanation=m.get("explanation", ""),
                )
            )

        # Parse decision factors
        decision_factors = []
        for f in context.get("decision_factors", []):
            decision_factors.append(
                DecisionFactor(
                    factor=f.get("factor"),
                    description=f.get("description"),
                    impact=f.get("impact"),
                    policy_id=f.get("policy_id"),
                    confidence=f.get("confidence"),
                )
            )

        # Run registered context decoders
        decoded_extras: Dict[str, Any] = {}
        for k, decoder in self._context_decoders.items():
            if k in context:
                try:
                    decoded_extras[k] = decoder(context[k])
                except Exception as e:
                    self.logger.warning(f"decoder for context key {k} failed: {e}")

        return EnhancedAuthResult(
            decision=decision,
            reason=context.get("reason_user", {}).get("en", "No reason provided"),
            constraints=constraints,
            obligations=obligations,
            learning_mode=context.get("learning_mode", False),
            original_decision=context.get("original_decision"),
            match_info=match_info,
            decision_factors=decision_factors,
            raw_context=context,
            decoded_extras=decoded_extras,
        )

    def _generate_correlation_id(self) -> str:
        """Generate correlation ID for request tracking"""
        import uuid

        return str(uuid.uuid4())

    async def evaluate_batch(
        self,
        requests: List[Dict[str, Any]],
        *,
        semantics: str = "execute_all",
    ) -> List[EnhancedAuthResult]:
        """Evaluate multiple requests (batch / boxcar) according to AuthZEN 7.x."""

        if semantics not in {"execute_all", "deny_on_first_deny", "permit_on_first_permit"}:
            raise ValueError("invalid evaluation semantics")

        payload = {
            "evaluations": requests,
            "options": {"evaluation_semantics": semantics},
        }

        raw_result = await self._call_pdp_api(payload, path="/v1/evaluations")

        evals = raw_result.get("evaluations", [])
        # When PDP falls back to single response it will return a decision at top level
        if not evals and "decision" in raw_result:
            evals = [raw_result]

        return [self._parse_enhanced_response(item) for item in evals]

    # ------------------------------ search ------------------------------

    async def _search(self, kind: str, payload: Dict[str, Any]):
        """Internal helper to POST to /access/v1/search/<kind>."""
        path = f"/access/v1/search/{kind}"
        return await self._call_pdp_api(payload, path=path)

    async def search_subject(self, action: Dict[str, Any], resource: Dict[str, Any], *, context: Dict[str, Any] | None = None, page_token: str = ""):
        payload = {
            "subject": {"type": "user"},
            "action": action,
            "resource": resource,
        }
        if context:
            payload["context"] = context
        if page_token:
            payload["page"] = {"next_token": page_token}
        return await self._search("subject", payload)

    async def search_resource(self, subject: Dict[str, Any], action: Dict[str, Any], *, context: Dict[str, Any] | None = None, page_token: str = ""):
        payload = {
            "subject": subject,
            "action": action,
            "resource": {"type": "resource"},
        }
        if context:
            payload["context"] = context
        if page_token:
            payload["page"] = {"next_token": page_token}
        return await self._search("resource", payload)

    async def search_action(self, subject: Dict[str, Any], resource: Dict[str, Any], *, context: Dict[str, Any] | None = None, page_token: str = ""):
        payload = {
            "subject": subject,
            "resource": resource,
        }
        if context:
            payload["context"] = context
        if page_token:
            payload["page"] = {"next_token": page_token}
        return await self._search("action", payload)

    # Iterative helper --------------------------------------------------

    async def iter_search_subject(
        self,
        action: Dict[str, Any],
        resource: Dict[str, Any],
        *,
        context: Dict[str, Any] | None = None,
        page_size: int | None = None,  # reserved for future server hints
    ):
        """Async generator that yields all subject search results across pages."""
        next_token: str = ""
        while True:
            resp = await self.search_subject(action, resource, context=context, page_token=next_token)
            for item in resp.get("results", []):
                yield item
            next_token = resp.get("page", {}).get("next_token", "")
            if not next_token:
                break

    # ------------------------------------------------------------------
    # Context decoder plug-in API
    # ------------------------------------------------------------------

    def register_context_decoder(self, key: str, decoder: Callable[[Any], Any]):
        """Register a decoder that transforms a vendor-specific context value.

        Example::
            pdp.register_context_decoder("quota", lambda v: int(v))
        """
        self._context_decoders[key] = decoder

    # ------------------------------------------------------------------
    # OAuth2 token retrieval (client_credentials)
    # ------------------------------------------------------------------

    async def _get_access_token(self) -> str:
        """Retrieve (and cache) an OAuth2 access token via client_credentials."""

        if getattr(self, "_cached_token", None) and self._cached_token_expiry - time.time() > 30:
            return self._cached_token  # type: ignore[attr-defined]

        import httpx, asyncio, json

        if not hasattr(self, "_http_client") or self._http_client is None:
            # create minimal client just for token; reuse later
            self._http_client = httpx.AsyncClient(
                base_url=self.config.base_url.rstrip("/"), timeout=10.0, verify=True
            )

        data = {
            "grant_type": "client_credentials",
            "scope": self.config.scope or "",
        }

        auth = (self.config.client_id, self.config.client_secret)

        resp = await self._http_client.post(self.config.token_url, data=data, auth=auth)
        resp.raise_for_status()
        tok_json = resp.json()
        access_token = tok_json.get("access_token")
        if not access_token:
            raise PDPError("token endpoint did not return access_token")
        expires_in = int(tok_json.get("expires_in", 3600))
        self._cached_token = access_token  # type: ignore[attr-defined]
        self._cached_token_expiry = time.time() + expires_in  # type: ignore[attr-defined]
        return access_token


# Maintain backward compatibility aliases
PolicyClient = EnhancedPDP
AuthzClient = EnhancedPDP
PDPClient = EnhancedPDP
PDP = EnhancedPDP  # Enhanced version replaces the simple one

# Legacy compatibility for AuthResult
AuthResult = EnhancedAuthResult
