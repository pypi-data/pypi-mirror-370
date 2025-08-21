"""
🛡️ PDP Integration Modes - Client-Side vs Server-Side Authorization

This module provides configuration options for how the OAuth client integrates
with Policy Decision Points (PDP) for authorization decisions.

Integration Modes:
1. CLIENT_SIDE_FIRST - Client calls PDP directly before OAuth flow
2. SERVER_SIDE_DELEGATED - IdP handles PDP evaluation internally
3. HYBRID_VALIDATION - Client validates first, IdP validates again
4. CLIENT_ONLY - Client-side only (no IdP PDP integration)
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class PDPIntegrationMode(Enum):
    """🛡️ PDP Integration Modes"""

    CLIENT_SIDE_FIRST = "client_side_first"
    """
    Client calls PDP directly before sending requests to IdP.
    - Pros: Early rejection, reduced IdP load, client control
    - Cons: Additional network call, PDP endpoint exposure
    - Use case: High-security environments, fine-grained control
    """

    SERVER_SIDE_DELEGATED = "server_side_delegated"
    """
    IdP handles all PDP evaluation internally.
    - Pros: Centralized policy, simplified client, better caching
    - Cons: Late rejection, higher IdP load, less client visibility
    - Use case: Standard deployments, centralized governance
    """

    HYBRID_VALIDATION = "hybrid_validation"
    """
    Client validates first, IdP validates again for final decision.
    - Pros: Early feedback + authoritative validation
    - Cons: Double PDP calls, complexity
    - Use case: Zero-trust environments, maximum security
    """

    CLIENT_ONLY = "client_only"
    """
    Client-side PDP only, no IdP integration.
    - Pros: Fastest, full client control, offline capable
    - Cons: No centralized enforcement, policy sync complexity
    - Use case: Edge computing, offline scenarios
    """


@dataclass
class PDPIntegrationConfig:
    """🛡️ Configuration for PDP integration behavior"""

    # Core mode setting
    mode: PDPIntegrationMode = PDPIntegrationMode.SERVER_SIDE_DELEGATED

    # PDP endpoint configuration (for client-side modes)
    pdp_endpoint: Optional[str] = None
    pdp_timeout: float = 5.0
    pdp_retries: int = 2

    # Client-side PDP authentication
    pdp_client_id: Optional[str] = None
    pdp_client_secret: Optional[str] = None
    pdp_token_url: Optional[str] = None

    # Caching configuration
    enable_client_cache: bool = True
    cache_ttl_allow: int = 300  # 5 minutes for allow decisions
    cache_ttl_deny: int = 60  # 1 minute for deny decisions

    # Fallback behavior
    fallback_on_pdp_failure: str = "deny"  # "deny", "allow", "proceed"

    # Advanced options
    include_request_context: bool = True
    enable_risk_scoring: bool = False
    log_pdp_decisions: bool = True

    # Hybrid mode specific
    require_both_allow: bool = True  # For hybrid mode
    client_pdp_precedence: bool = False  # Client decision takes precedence

    def validate(self) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []

        # Check PDP endpoint for client-side modes
        client_side_modes = [
            PDPIntegrationMode.CLIENT_SIDE_FIRST,
            PDPIntegrationMode.HYBRID_VALIDATION,
            PDPIntegrationMode.CLIENT_ONLY,
        ]

        if self.mode in client_side_modes and not self.pdp_endpoint:
            errors.append(f"pdp_endpoint required for mode {self.mode.value}")

        # Check authentication for PDP
        if self.pdp_endpoint and self.pdp_client_id and not self.pdp_client_secret:
            errors.append("pdp_client_secret required when pdp_client_id is provided")

        # Check fallback values
        valid_fallbacks = ["deny", "allow", "proceed"]
        if self.fallback_on_pdp_failure not in valid_fallbacks:
            errors.append(f"fallback_on_pdp_failure must be one of {valid_fallbacks}")

        # Check timeouts
        if self.pdp_timeout <= 0:
            errors.append("pdp_timeout must be positive")

        if self.cache_ttl_allow <= 0 or self.cache_ttl_deny <= 0:
            errors.append("cache TTL values must be positive")

        return errors

    def is_client_side_enabled(self) -> bool:
        """Check if client-side PDP evaluation is enabled"""
        return self.mode in [
            PDPIntegrationMode.CLIENT_SIDE_FIRST,
            PDPIntegrationMode.HYBRID_VALIDATION,
            PDPIntegrationMode.CLIENT_ONLY,
        ]

    def is_server_side_enabled(self) -> bool:
        """Check if server-side PDP evaluation is enabled"""
        return self.mode in [
            PDPIntegrationMode.SERVER_SIDE_DELEGATED,
            PDPIntegrationMode.HYBRID_VALIDATION,
        ]

    def should_call_pdp_first(self) -> bool:
        """Check if client should call PDP before OAuth flow"""
        return self.mode in [
            PDPIntegrationMode.CLIENT_SIDE_FIRST,
            PDPIntegrationMode.HYBRID_VALIDATION,
            PDPIntegrationMode.CLIENT_ONLY,
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "mode": self.mode.value,
            "pdp_endpoint": self.pdp_endpoint,
            "pdp_timeout": self.pdp_timeout,
            "pdp_retries": self.pdp_retries,
            "pdp_client_id": self.pdp_client_id,
            "pdp_client_secret": "***" if self.pdp_client_secret else None,
            "pdp_token_url": self.pdp_token_url,
            "enable_client_cache": self.enable_client_cache,
            "cache_ttl_allow": self.cache_ttl_allow,
            "cache_ttl_deny": self.cache_ttl_deny,
            "fallback_on_pdp_failure": self.fallback_on_pdp_failure,
            "include_request_context": self.include_request_context,
            "enable_risk_scoring": self.enable_risk_scoring,
            "log_pdp_decisions": self.log_pdp_decisions,
            "require_both_allow": self.require_both_allow,
            "client_pdp_precedence": self.client_pdp_precedence,
        }


class PDPModeSelector:
    """🛡️ Helper class for selecting appropriate PDP integration mode"""

    @staticmethod
    def for_high_security() -> PDPIntegrationConfig:
        """Configuration for high-security environments"""
        return PDPIntegrationConfig(
            mode=PDPIntegrationMode.HYBRID_VALIDATION,
            pdp_timeout=3.0,
            pdp_retries=3,
            cache_ttl_allow=60,  # Shorter caching for security
            cache_ttl_deny=30,
            fallback_on_pdp_failure="deny",
            require_both_allow=True,
            enable_risk_scoring=True,
            log_pdp_decisions=True,
        )

    @staticmethod
    def for_performance() -> PDPIntegrationConfig:
        """Configuration optimized for performance"""
        return PDPIntegrationConfig(
            mode=PDPIntegrationMode.SERVER_SIDE_DELEGATED,
            enable_client_cache=True,
            cache_ttl_allow=600,  # Longer caching for performance
            cache_ttl_deny=120,
            fallback_on_pdp_failure="proceed",
            include_request_context=False,  # Reduce payload size
        )

    @staticmethod
    def for_client_control() -> PDPIntegrationConfig:
        """Configuration for maximum client control"""
        return PDPIntegrationConfig(
            mode=PDPIntegrationMode.CLIENT_SIDE_FIRST,
            pdp_timeout=2.0,
            pdp_retries=1,  # Fast fail for client control
            enable_client_cache=True,
            fallback_on_pdp_failure="deny",
            include_request_context=True,
            enable_risk_scoring=True,
        )

    @staticmethod
    def for_offline_capable() -> PDPIntegrationConfig:
        """Configuration for offline/edge scenarios"""
        return PDPIntegrationConfig(
            mode=PDPIntegrationMode.CLIENT_ONLY,
            enable_client_cache=True,
            cache_ttl_allow=3600,  # Longer cache for offline
            cache_ttl_deny=300,
            fallback_on_pdp_failure="allow",  # More permissive for offline
            include_request_context=True,
        )

    @staticmethod
    def for_government() -> PDPIntegrationConfig:
        """Configuration for government/FIPS environments"""
        return PDPIntegrationConfig(
            mode=PDPIntegrationMode.HYBRID_VALIDATION,
            pdp_timeout=10.0,  # Allow longer for security validation
            pdp_retries=3,
            cache_ttl_allow=180,  # Government security requirements
            cache_ttl_deny=30,
            fallback_on_pdp_failure="deny",
            require_both_allow=True,
            enable_risk_scoring=True,
            log_pdp_decisions=True,
            include_request_context=True,
        )


# Convenience configurations
DEFAULT_CONFIG = PDPIntegrationConfig()
HIGH_SECURITY_CONFIG = PDPModeSelector.for_high_security()
PERFORMANCE_CONFIG = PDPModeSelector.for_performance()
CLIENT_CONTROL_CONFIG = PDPModeSelector.for_client_control()
OFFLINE_CONFIG = PDPModeSelector.for_offline_capable()
GOVERNMENT_CONFIG = PDPModeSelector.for_government()


def log_pdp_mode_selection(config: PDPIntegrationConfig):
    """Log the selected PDP integration mode for debugging"""
    logger.info(f"🛡️ PDP Integration Mode: {config.mode.value}")
    logger.info(f"   Client-side enabled: {config.is_client_side_enabled()}")
    logger.info(f"   Server-side enabled: {config.is_server_side_enabled()}")
    logger.info(f"   Call PDP first: {config.should_call_pdp_first()}")

    if config.pdp_endpoint:
        logger.info(f"   PDP endpoint: {config.pdp_endpoint}")
        logger.info(f"   PDP timeout: {config.pdp_timeout}s")

    logger.info(f"   Fallback strategy: {config.fallback_on_pdp_failure}")
    logger.info(f"   Caching enabled: {config.enable_client_cache}")
