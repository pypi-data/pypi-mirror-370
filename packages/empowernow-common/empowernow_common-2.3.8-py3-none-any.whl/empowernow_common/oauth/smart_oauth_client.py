"""
🛡️ Smart OAuth Client with Configurable PDP Integration

This client provides intelligent OAuth flows with configurable PDP integration:
- CLIENT_SIDE_FIRST: Call PDP before OAuth flow
- SERVER_SIDE_DELEGATED: Let IdP handle PDP internally
- HYBRID_VALIDATION: Both client and server validate
- CLIENT_ONLY: Client-side PDP only

The client automatically adapts its behavior based on the PDPIntegrationConfig.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone

from .pdp_integration_modes import (
    PDPIntegrationMode,
    PDPIntegrationConfig,
    log_pdp_mode_selection,
)
from ..authzen.client import PDPClient, AuthorizationResult
from ..authzen.models import Subject, Resource, Action, Context, AuthorizationRequest
from .client import OAuthClient, OAuthConfig, TokenResponse, OAuthError

logger = logging.getLogger(__name__)


class SmartOAuthClient:
    """🛡️ Smart OAuth client with configurable PDP integration"""

    def __init__(
        self,
        oauth_config: OAuthConfig,
        pdp_config: PDPIntegrationConfig,
        pdp_client: Optional[PDPClient] = None,
    ):
        """
        Initialize smart OAuth client

        Args:
            oauth_config: OAuth client configuration
            pdp_config: PDP integration configuration
            pdp_client: Optional pre-configured PDP client
        """
        self.oauth_config = oauth_config
        self.pdp_config = pdp_config

        # Initialize OAuth client
        self.oauth_client = OAuthClient(oauth_config)

        # Initialize PDP client if needed
        self.pdp_client = pdp_client
        if not self.pdp_client and self.pdp_config.is_client_side_enabled():
            self._initialize_pdp_client()

        # Validate configuration
        config_errors = self.pdp_config.validate()
        if config_errors:
            raise ValueError(f"Invalid PDP configuration: {config_errors}")

        # Log configuration
        log_pdp_mode_selection(self.pdp_config)

    def _initialize_pdp_client(self):
        """Initialize PDP client for client-side evaluation"""
        if not self.pdp_config.pdp_endpoint:
            raise ValueError("PDP endpoint required for client-side evaluation")

        from ..authzen.client import PDPConfig

        pdp_client_config = PDPConfig(
            base_url=self.pdp_config.pdp_endpoint,
            client_id=self.pdp_config.pdp_client_id,
            client_secret=self.pdp_config.pdp_client_secret,
            token_url=self.pdp_config.pdp_token_url,
            timeout=self.pdp_config.pdp_timeout,
            max_retries=self.pdp_config.pdp_retries,
            cache_ttl_allow=self.pdp_config.cache_ttl_allow,
            cache_ttl_deny=self.pdp_config.cache_ttl_deny,
        )

        self.pdp_client = PDPClient(pdp_client_config)
        logger.info(f"🛡️ Initialized PDP client for {self.pdp_config.pdp_endpoint}")

    async def authorize_with_rar(
        self,
        subject_id: str,
        authorization_details: List[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform authorization with Rich Authorization Requests (RAR)

        Args:
            subject_id: Subject identifier
            authorization_details: List of authorization detail objects
            additional_context: Additional context for authorization

        Returns:
            Dict containing authorization result and any constraints
        """
        logger.info(f"🛡️ Starting RAR authorization for subject {subject_id}")
        logger.info(f"   Mode: {self.pdp_config.mode.value}")
        logger.info(f"   Authorization details: {len(authorization_details)} items")

        # Step 1: Client-side PDP evaluation (if configured)
        client_pdp_result = None
        if self.pdp_config.should_call_pdp_first():
            client_pdp_result = await self._evaluate_client_side_pdp(
                subject_id, authorization_details, additional_context
            )

            # Handle client-side denial
            if not client_pdp_result.is_allowed:
                if self.pdp_config.mode == PDPIntegrationMode.CLIENT_ONLY:
                    return self._create_authorization_result(
                        allowed=False,
                        reason="Client-side PDP denied request",
                        pdp_result=client_pdp_result,
                    )
                elif self.pdp_config.mode == PDPIntegrationMode.CLIENT_SIDE_FIRST:
                    return self._create_authorization_result(
                        allowed=False,
                        reason="Pre-authorization check failed",
                        pdp_result=client_pdp_result,
                    )
                # For HYBRID mode, continue to server-side validation

        # Step 2: OAuth flow with IdP (if configured)
        oauth_result = None
        if self.pdp_config.is_server_side_enabled():
            oauth_result = await self._perform_oauth_flow(
                subject_id, authorization_details, additional_context, client_pdp_result
            )

        # Step 3: Combine results based on mode
        return self._combine_authorization_results(client_pdp_result, oauth_result)

    async def _evaluate_client_side_pdp(
        self,
        subject_id: str,
        authorization_details: List[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> AuthorizationResult:
        """Evaluate authorization using client-side PDP"""
        logger.info("🛡️ Performing client-side PDP evaluation")

        try:
            # Convert authorization details to AuthZEN requests
            authzen_requests = self._convert_to_authzen_requests(
                subject_id, authorization_details, additional_context
            )

            # Evaluate with PDP client
            if len(authzen_requests) == 1:
                result = await self.pdp_client.evaluate(authzen_requests[0])
            else:
                result = await self.pdp_client.evaluate_batch(authzen_requests)

            logger.info(
                f"🛡️ Client PDP result: {result.decision} (cached: {result.cached})"
            )
            return result

        except Exception as e:
            logger.error(f"🛡️ Client PDP evaluation failed: {e}")
            return self._handle_pdp_failure(e, "client-side")

    async def _perform_oauth_flow(
        self,
        subject_id: str,
        authorization_details: List[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]] = None,
        client_pdp_result: Optional[AuthorizationResult] = None,
    ) -> Dict[str, Any]:
        """Perform OAuth flow with IdP (which may do its own PDP evaluation)"""
        logger.info("🛡️ Performing OAuth flow with IdP")

        try:
            # Prepare OAuth request with authorization details
            oauth_params = {
                "authorization_details": authorization_details,
                "subject_id": subject_id,
            }

            # Add client PDP context if available
            if client_pdp_result and self.pdp_config.include_request_context:
                oauth_params["client_pdp_context"] = {
                    "decision": client_pdp_result.decision,
                    "cached": client_pdp_result.cached,
                    "duration_ms": client_pdp_result.duration_ms,
                }

            # Add additional context
            if additional_context:
                oauth_params.update(additional_context)

            # Perform OAuth request (this would call your IdP)
            # For now, simulate the OAuth flow
            oauth_response = await self._simulate_oauth_request(oauth_params)

            logger.info(
                f"🛡️ OAuth flow completed: {oauth_response.get('status', 'unknown')}"
            )
            return oauth_response

        except Exception as e:
            logger.error(f"🛡️ OAuth flow failed: {e}")
            raise OAuthError(f"OAuth flow failed: {e}")

    def _convert_to_authzen_requests(
        self,
        subject_id: str,
        authorization_details: List[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> List[AuthorizationRequest]:
        """Convert authorization details to AuthZEN requests"""
        requests = []

        # Create base context
        context_attrs = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "client_id": self.oauth_config.client_id,
        }

        if additional_context:
            context_attrs.update(additional_context)

        # Add risk scoring if enabled
        if self.pdp_config.enable_risk_scoring:
            context_attrs["risk_assessment"] = self._calculate_risk_score(
                additional_context
            )

        base_context = Context(attributes=context_attrs)

        # Convert each authorization detail
        for detail in authorization_details:
            # Create subject
            subject = Subject(
                type="user",
                id=subject_id,
                attributes=detail.get("subject_attributes", {}),
            )

            # Create resource
            resource = Resource(
                type=detail.get("type", "unknown"),
                id=detail.get("identifier", "unknown"),
                attributes=detail.get("resource_attributes", {}),
            )

            # Create actions
            actions = detail.get("actions", ["access"])
            for action_name in actions:
                action = Action(
                    name=action_name, attributes=detail.get("action_attributes", {})
                )

                # Create authorization request
                request = AuthorizationRequest(
                    subject=subject,
                    resource=resource,
                    action=action,
                    context=base_context,
                )

                requests.append(request)

        return requests

    def _calculate_risk_score(
        self, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate risk score for the request"""
        # Simple risk scoring - in production this would be more sophisticated
        risk_factors = {
            "network_risk": 0.1,  # Low risk by default
            "behavioral_risk": 0.1,
            "device_risk": 0.1,
        }

        if context:
            # Adjust risk based on context
            if context.get("ip_address", "").startswith("10."):
                risk_factors["network_risk"] = 0.05  # Internal network

            if context.get("user_agent", "").startswith("curl"):
                risk_factors["behavioral_risk"] = 0.3  # Automated tool

        overall_risk = sum(risk_factors.values()) / len(risk_factors)

        return {
            "overall_score": overall_risk,
            "factors": risk_factors,
            "level": (
                "low"
                if overall_risk < 0.3
                else "medium"
                if overall_risk < 0.7
                else "high"
            ),
        }

    def _handle_pdp_failure(
        self, error: Exception, context: str
    ) -> AuthorizationResult:
        """Handle PDP evaluation failure based on fallback configuration"""
        logger.error(f"🛡️ PDP failure in {context}: {error}")

        fallback = self.pdp_config.fallback_on_pdp_failure

        if fallback == "deny":
            decision = False
            reason = f"PDP failure in {context} - defaulting to deny"
        elif fallback == "allow":
            decision = True
            reason = f"PDP failure in {context} - defaulting to allow"
        else:  # "proceed"
            decision = True
            reason = f"PDP failure in {context} - proceeding without validation"

        from ..authzen.models import AuthorizationResponse

        response = AuthorizationResponse(decision=decision, context={"reason": reason})

        return AuthorizationResult(
            success=False, response=response, error=error, duration_ms=0.0
        )

    def _combine_authorization_results(
        self,
        client_result: Optional[AuthorizationResult],
        oauth_result: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Combine client and server authorization results"""

        if self.pdp_config.mode == PDPIntegrationMode.CLIENT_ONLY:
            return self._create_authorization_result(
                allowed=client_result.is_allowed if client_result else False,
                reason=(
                    client_result.get_reason()
                    if client_result
                    else "No evaluation performed"
                ),
                pdp_result=client_result,
            )

        elif self.pdp_config.mode == PDPIntegrationMode.SERVER_SIDE_DELEGATED:
            return oauth_result or {"allowed": False, "reason": "No OAuth result"}

        elif self.pdp_config.mode == PDPIntegrationMode.CLIENT_SIDE_FIRST:
            if client_result and not client_result.is_allowed:
                return self._create_authorization_result(
                    allowed=False,
                    reason="Client-side pre-authorization failed",
                    pdp_result=client_result,
                )
            return oauth_result or {"allowed": False, "reason": "No OAuth result"}

        elif self.pdp_config.mode == PDPIntegrationMode.HYBRID_VALIDATION:
            client_allowed = client_result.is_allowed if client_result else False
            server_allowed = (
                oauth_result.get("allowed", False) if oauth_result else False
            )

            if self.pdp_config.require_both_allow:
                final_allowed = client_allowed and server_allowed
                reason = "Both client and server validation required"
            else:
                if self.pdp_config.client_pdp_precedence:
                    final_allowed = client_allowed
                    reason = "Client PDP decision takes precedence"
                else:
                    final_allowed = server_allowed
                    reason = "Server PDP decision takes precedence"

            return self._create_authorization_result(
                allowed=final_allowed,
                reason=reason,
                pdp_result=client_result,
                oauth_result=oauth_result,
            )

        return {"allowed": False, "reason": "Unknown integration mode"}

    def _create_authorization_result(
        self,
        allowed: bool,
        reason: str,
        pdp_result: Optional[AuthorizationResult] = None,
        oauth_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create standardized authorization result"""
        result = {
            "allowed": allowed,
            "reason": reason,
            "mode": self.pdp_config.mode.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if pdp_result:
            result["client_pdp"] = {
                "decision": pdp_result.decision,
                "cached": pdp_result.cached,
                "duration_ms": pdp_result.duration_ms,
                "reason": pdp_result.get_reason(),
            }

        if oauth_result:
            result["server_oauth"] = oauth_result

        return result

    async def _simulate_oauth_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate OAuth request - replace with actual implementation"""
        # This would be replaced with actual OAuth flow implementation
        await asyncio.sleep(0.1)  # Simulate network delay

        return {
            "allowed": True,
            "status": "success",
            "access_token": "simulated-token-123",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "read write",
            "server_pdp_decision": True,
            "server_pdp_cached": False,
        }


# Convenience factory functions
def create_client_first_oauth_client(
    oauth_config: OAuthConfig,
    pdp_endpoint: str,
    pdp_client_id: str = None,
    pdp_client_secret: str = None,
) -> SmartOAuthClient:
    """Create OAuth client that calls PDP first"""
    pdp_config = PDPIntegrationConfig(
        mode=PDPIntegrationMode.CLIENT_SIDE_FIRST,
        pdp_endpoint=pdp_endpoint,
        pdp_client_id=pdp_client_id,
        pdp_client_secret=pdp_client_secret,
        fallback_on_pdp_failure="deny",
    )
    return SmartOAuthClient(oauth_config, pdp_config)


def create_server_delegated_oauth_client(oauth_config: OAuthConfig) -> SmartOAuthClient:
    """Create OAuth client that delegates PDP to IdP"""
    pdp_config = PDPIntegrationConfig(mode=PDPIntegrationMode.SERVER_SIDE_DELEGATED)
    return SmartOAuthClient(oauth_config, pdp_config)


def create_hybrid_oauth_client(
    oauth_config: OAuthConfig,
    pdp_endpoint: str,
    pdp_client_id: str = None,
    pdp_client_secret: str = None,
) -> SmartOAuthClient:
    """Create OAuth client with hybrid validation"""
    pdp_config = PDPIntegrationConfig(
        mode=PDPIntegrationMode.HYBRID_VALIDATION,
        pdp_endpoint=pdp_endpoint,
        pdp_client_id=pdp_client_id,
        pdp_client_secret=pdp_client_secret,
        require_both_allow=True,
    )
    return SmartOAuthClient(oauth_config, pdp_config)
