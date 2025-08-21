"""
🎯 EmpowerNow AuthZEN Package

Beautiful, intuitive authorization models with zero learning curve.
Enhanced with Policy Enforcement Point (PEP) capabilities.

Examples:
    # Natural language aliases
    who = Subject.user("alice")  # or Who.user("alice")
    what = Resource.file("/docs/secret.pdf")  # or What.file(...)
    how = Action.read()  # or How.read()
    when = Context(ip_address="192.168.1.1")  # or When(...)

    # Enhanced PDP with PEP capabilities
    async with EnhancedPDP("https://pdp.example.com", "client", "secret", "token_url") as pdp:
        result = await pdp.check(who, how, what, **when)

        if result.decision:
            print(f"Access granted with {len(result.constraints)} constraints")
            print(f"Processing {len(result.obligations)} obligations")
"""

from .models import (
    Subject,
    Who,
    Resource,
    What,
    Action,
    How,
    Context,
    When,
    AuthRequest,
    AuthResponse,
)

from .client import (
    # Enhanced PDP with PEP capabilities
    EnhancedPDP,
    EnhancedAuthResult,
    PDPConfig,
    PDPError,
    ConstraintViolationError,
    CriticalObligationFailure,
    # Advanced models
    Constraint,
    Obligation,
    PolicyMatchInfo,
    DecisionFactor,
    ConstraintsMode,
    # Legacy compatibility aliases
    PDP,
    PDPClient,
    PolicyClient,
    AuthzClient,
    AuthResult,  # Alias for EnhancedAuthResult
)

__all__ = [
    # 🎨 Beautiful Models (Natural Language)
    "Subject",
    "Who",
    "Resource",
    "What",
    "Action",
    "How",
    "Context",
    "When",
    "AuthRequest",
    "AuthResponse",
    # 🛡️ Enhanced PDP Client (WORLD'S MOST ADVANCED)
    "EnhancedPDP",
    "EnhancedAuthResult",
    "PDPConfig",
    "PDPError",
    "ConstraintViolationError",
    "CriticalObligationFailure",
    # 🎯 Advanced Policy Models
    "Constraint",
    "Obligation",
    "PolicyMatchInfo",
    "DecisionFactor",
    "ConstraintsMode",
    # 🔄 Legacy Compatibility
    "PDP",
    "PDPClient",
    "PolicyClient",
    "AuthzClient",
    "AuthResult",
]
