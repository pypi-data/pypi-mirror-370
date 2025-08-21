"""
AuthZEN Models – Security Hardened

Beautiful, intuitive authorization models with comprehensive security protections.

SECURITY ENHANCEMENTS:
- Input validation and sanitization
- Size limits to prevent DoS attacks
- Type validation for all attributes
- Injection attack protection
- Sensitive data filtering for logs
- FIPS-compliant correlation IDs

Examples:
    # Simple authorization check (with validation)
    request = AuthRequest.simple("alice", "/documents/secret.pdf", "read")

    # Complex authorization with context (validated)
    request = AuthRequest(
        who=Subject.user("alice", department="engineering"),
        what=Resource.file("/docs/secret.pdf", owner="bob"),
        action="read",
        context={"ip": "192.168.1.100", "device": "laptop"}
    )
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union, Set
from pydantic import BaseModel, Field, ConfigDict, validator, field_validator

from ..fips.entropy import generate_correlation_id
from ..exceptions import AuthZENError

logger = logging.getLogger(__name__)

# Security constants
MAX_SUBJECT_ID_LENGTH = 256
MAX_RESOURCE_ID_LENGTH = 512
MAX_ACTION_NAME_LENGTH = 128
MAX_ATTRIBUTE_KEY_LENGTH = 64
MAX_ATTRIBUTE_VALUE_LENGTH = 1024
MAX_ATTRIBUTES_COUNT = 50
MAX_CONTEXT_ATTRIBUTES = 100

# Dangerous patterns to block
INJECTION_PATTERNS = [
    r"<script[^>]*>.*?</script>",  # XSS
    r"javascript:",  # JavaScript protocol
    r"data:.*base64",  # Data URLs
    r"file:///",  # File protocol
    r"\\x[0-9a-fA-F]{2}",  # Hex encoding
    r"%[0-9a-fA-F]{2}",  # URL encoding of dangerous chars
    r"\.\./",  # Path traversal
    r"UNION\s+SELECT",  # SQL injection
    r"OR\s+1\s*=\s*1",  # SQL injection
]

SENSITIVE_FIELD_PATTERNS = [
    r"password",
    r"passwd",
    r"pwd",
    r"secret",
    r"key",
    r"token",
    r"auth",
    r"credential",
    r"private",
    r"confidential",
]

# ---------------- Error Hierarchy ----------------


class AuthZENSecurityError(AuthZENError):
    """AuthZEN security-related errors"""

    pass


class ValidationError(AuthZENSecurityError):
    """Input validation errors"""

    pass


def validate_string_input(
    value: str, field_name: str, max_length: int, allow_empty: bool = False
) -> str:
    """
    🛡️ Comprehensive string validation for security.

    Args:
        value: Input value to validate
        field_name: Field name for error messages
        max_length: Maximum allowed length
        allow_empty: Whether to allow empty strings

    Returns:
        str: Validated and sanitized string

    Raises:
        ValidationError: If input fails security validation
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")

    if not allow_empty and not value.strip():
        raise ValidationError(f"{field_name} cannot be empty")

    if len(value) > max_length:
        raise ValidationError(f"{field_name} exceeds maximum length of {max_length}")

    # Check for injection patterns
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            logger.warning(
                f"🚨 Potential injection attack blocked in {field_name}: {pattern}"
            )
            raise ValidationError(
                f"{field_name} contains potentially dangerous content"
            )

    # Remove null bytes and control characters (except allowed whitespace)
    sanitized = "".join(
        char for char in value if ord(char) >= 32 or char in {"\t", "\n", "\r"}
    )

    return sanitized.strip()


def validate_attributes(
    attributes: Dict[str, Any], context: str, max_count: int = MAX_ATTRIBUTES_COUNT
) -> Dict[str, Any]:
    """
    🛡️ Validate and sanitize attribute dictionaries.

    Args:
        attributes: Attributes to validate
        context: Context for error messages
        max_count: Maximum number of attributes allowed

    Returns:
        Dict[str, Any]: Validated attributes

    Raises:
        ValidationError: If attributes fail security validation
    """
    if not isinstance(attributes, dict):
        raise ValidationError(f"{context} attributes must be a dictionary")

    if len(attributes) > max_count:
        raise ValidationError(f"{context} has too many attributes (max {max_count})")

    validated_attrs = {}

    for key, value in attributes.items():
        # Validate key
        if not isinstance(key, str):
            raise ValidationError(
                f"{context} attribute key must be string, got {type(key)}"
            )

        validated_key = validate_string_input(
            key, f"{context} attribute key", MAX_ATTRIBUTE_KEY_LENGTH
        )

        # Validate value based on type
        if isinstance(value, str):
            validated_value = validate_string_input(
                value,
                f"{context} attribute '{key}'",
                MAX_ATTRIBUTE_VALUE_LENGTH,
                allow_empty=True,
            )
        elif isinstance(value, (int, float, bool)):
            validated_value = value
        elif isinstance(value, list):
            if len(value) > 20:  # Limit array size
                raise ValidationError(f"{context} attribute '{key}' array too large")
            validated_value = [
                (
                    validate_string_input(
                        str(item),
                        f"{context} attribute '{key}' item",
                        MAX_ATTRIBUTE_VALUE_LENGTH,
                    )
                    if isinstance(item, str)
                    else item
                )
                for item in value
            ]
        elif isinstance(value, dict):
            if len(value) > 10:  # Limit nested object size
                raise ValidationError(f"{context} attribute '{key}' object too complex")
            validated_value = validate_attributes(
                value, f"{context} nested attribute '{key}'", 10
            )
        elif value is None:
            validated_value = None
        else:
            # Convert unknown types to string and validate
            validated_value = validate_string_input(
                str(value), f"{context} attribute '{key}'", MAX_ATTRIBUTE_VALUE_LENGTH
            )

        validated_attrs[validated_key] = validated_value

    return validated_attrs


def sanitize_for_logging(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    🛡️ Sanitize data for safe logging by removing sensitive information.

    Args:
        data: Data to sanitize

    Returns:
        Dict[str, Any]: Sanitized data safe for logging
    """
    sanitized = {}

    for key, value in data.items():
        key_lower = key.lower()

        # Check if key contains sensitive patterns
        is_sensitive = any(
            re.search(pattern, key_lower) for pattern in SENSITIVE_FIELD_PATTERNS
        )

        if is_sensitive:
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_for_logging(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_for_logging(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


class SecureSubject(BaseModel):
    """🛡️ Secure Subject model - Who is requesting access?"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",  # Security: Don't allow extra fields
    )

    id: str = Field(..., description="Who this is")
    type: str = Field(default="user", description="What kind of subject")
    attributes: Dict[str, Any] = Field(
        default_factory=dict, description="Extra info about them"
    )

    @field_validator("id")
    @classmethod
    def validate_id(cls, v):
        return validate_string_input(v, "subject_id", MAX_SUBJECT_ID_LENGTH)

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        allowed_types = {"user", "service", "agent", "device", "application"}
        validated = validate_string_input(v, "subject_type", 32)
        if validated not in allowed_types:
            logger.warning(f"🚨 Unknown subject type: {validated}")
        return validated

    @field_validator("attributes")
    @classmethod
    def validate_attributes(cls, v):
        return validate_attributes(v, "subject")

    @classmethod
    def user(cls, user_id: str, **attributes: Any) -> "SecureSubject":
        """Create a secure user subject."""
        return cls(id=user_id, type="user", attributes=attributes)

    @classmethod
    def service(cls, service_id: str, **attributes: Any) -> "SecureSubject":
        """Create a secure service subject."""
        return cls(id=service_id, type="service", attributes=attributes)

    @classmethod
    def agent(cls, agent_id: str, **attributes: Any) -> "SecureSubject":
        """Create a secure AI agent subject."""
        return cls(id=agent_id, type="agent", attributes=attributes)

    def to_log_safe(self) -> Dict[str, Any]:
        """Return log-safe representation with sensitive data redacted"""
        return {
            "id": self.id,
            "type": self.type,
            "attributes": sanitize_for_logging(self.attributes),
        }

    def __str__(self) -> str:
        return f"{self.type}:{self.id}"


class SecureResource(BaseModel):
    """🛡️ Secure Resource model - What is being accessed?"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",  # Security: Don't allow extra fields
    )

    id: str = Field(..., description="What this is")
    type: str = Field(default="resource", description="What kind of resource")
    attributes: Dict[str, Any] = Field(
        default_factory=dict, description="Extra info about it"
    )

    @field_validator("id")
    @classmethod
    def validate_id(cls, v):
        return validate_string_input(v, "resource_id", MAX_RESOURCE_ID_LENGTH)

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        allowed_types = {
            "file",
            "api",
            "database",
            "service",
            "document",
            "account",
            "resource",
        }
        validated = validate_string_input(v, "resource_type", 32)
        if validated not in allowed_types:
            logger.warning(f"🚨 Unknown resource type: {validated}")
        return validated

    @field_validator("attributes")
    @classmethod
    def validate_attributes(cls, v):
        return validate_attributes(v, "resource")

    @classmethod
    def file(cls, file_path: str, **attributes: Any) -> "SecureResource":
        """Create a secure file resource."""
        return cls(id=file_path, type="file", attributes=attributes)

    @classmethod
    def api(cls, api_name: str, **attributes: Any) -> "SecureResource":
        """Create a secure API resource."""
        return cls(id=api_name, type="api", attributes=attributes)

    @classmethod
    def database(cls, db_name: str, **attributes: Any) -> "SecureResource":
        """Create a secure database resource."""
        return cls(id=db_name, type="database", attributes=attributes)

    def to_log_safe(self) -> Dict[str, Any]:
        """Return log-safe representation with sensitive data redacted"""
        return {
            "id": self.id,
            "type": self.type,
            "attributes": sanitize_for_logging(self.attributes),
        }

    def __str__(self) -> str:
        return f"{self.type}:{self.id}"


class SecureAction(BaseModel):
    """🛡️ Secure Action model - What action is being performed?"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",  # Security: Don't allow extra fields
    )

    name: str = Field(..., description="What action")
    id: Optional[str] = Field(None, description="Optional action ID")
    type: Optional[str] = Field(None, description="Optional action type")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Extra info")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return validate_string_input(v, "action_name", MAX_ACTION_NAME_LENGTH)

    @field_validator("id")
    @classmethod
    def validate_id(cls, v):
        if v is not None:
            return validate_string_input(v, "action_id", MAX_ACTION_NAME_LENGTH)
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is not None:
            allowed_types = {"crud", "admin", "financial", "security", "data_access"}
            validated = validate_string_input(v, "action_type", 32)
            if validated not in allowed_types:
                logger.warning(f"🚨 Unknown action type: {validated}")
            return validated
        return v

    @field_validator("attributes")
    @classmethod
    def validate_attributes(cls, v):
        return validate_attributes(v, "action")

    @classmethod
    def read(cls, **attributes: Any) -> "SecureAction":
        """Create a secure read action."""
        return cls(name="read", attributes=attributes)

    @classmethod
    def write(cls, **attributes: Any) -> "SecureAction":
        """Create a secure write action."""
        return cls(name="write", attributes=attributes)

    @classmethod
    def delete(cls, **attributes: Any) -> "SecureAction":
        """Create a secure delete action."""
        return cls(name="delete", attributes=attributes)

    @classmethod
    def execute(cls, **attributes: Any) -> "SecureAction":
        """Create a secure execute action."""
        return cls(name="execute", attributes=attributes)

    def to_log_safe(self) -> Dict[str, Any]:
        """Return log-safe representation with sensitive data redacted"""
        return {
            "name": self.name,
            "id": self.id,
            "type": self.type,
            "attributes": sanitize_for_logging(self.attributes),
        }

    def __str__(self) -> str:
        return self.name


class SecureContext(BaseModel):
    """🛡️ Secure Context model - Extra information about the request."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",  # Security: Don't allow extra fields
    )

    # Common context fields
    time: Optional[datetime] = Field(None, description="When")
    ip: Optional[str] = Field(None, description="From where")
    user_agent: Optional[str] = Field(None, description="What client")

    # All other context goes here
    attributes: Dict[str, Any] = Field(
        default_factory=dict, description="Everything else"
    )

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v):
        if v is not None:
            # Basic IP validation
            import ipaddress

            try:
                ipaddress.ip_address(v)
                return v
            except ValueError:
                # Also allow hostnames
                validated = validate_string_input(v, "ip_address", 255)
                return validated
        return v

    @field_validator("user_agent")
    @classmethod
    def validate_user_agent(cls, v):
        if v is not None:
            return validate_string_input(v, "user_agent", 512)
        return v

    @field_validator("attributes")
    @classmethod
    def validate_attributes(cls, v):
        return validate_attributes(v, "context", MAX_CONTEXT_ATTRIBUTES)

    @classmethod
    def web_request(
        cls,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        **attributes: Any,
    ) -> "SecureContext":
        """Create secure web request context."""
        return cls(
            time=datetime.utcnow(),  # Use UTC for consistency
            ip=ip,
            user_agent=user_agent,
            attributes=attributes,
        )

    @classmethod
    def api_request(cls, **attributes: Any) -> "SecureContext":
        """Create secure API request context."""
        attrs = attributes.copy()
        if "correlation_id" not in attrs:
            attrs["correlation_id"] = generate_correlation_id()
        return cls(time=datetime.utcnow(), attributes=attrs)

    def to_log_safe(self) -> Dict[str, Any]:
        """Return log-safe representation with sensitive data redacted"""
        return {
            "time": self.time.isoformat() if self.time else None,
            "ip": self.ip,
            "user_agent": self.user_agent,
            "attributes": sanitize_for_logging(self.attributes),
        }


class SecureAuthRequest(BaseModel):
    """🛡️ Secure Authorization request - who wants to do what?"""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    # The core question: who wants to do what to which resource?
    subject: SecureSubject = Field(..., description="Who")
    resource: SecureResource = Field(..., description="What")
    action: SecureAction = Field(..., description="How")
    context: SecureContext = Field(
        default_factory=SecureContext, description="Extra info"
    )

    @classmethod
    def simple(
        cls, who: str, what: str, how: str, **context_attrs: Any
    ) -> "SecureAuthRequest":
        """Create simple secure authorization request with just strings."""
        return cls(
            subject=SecureSubject(id=who, type="user"),
            resource=SecureResource(id=what, type="resource"),
            action=SecureAction(name=how),
            context=(
                SecureContext(attributes=context_attrs)
                if context_attrs
                else SecureContext()
            ),
        )

    def to_log_safe(self) -> Dict[str, Any]:
        """Return log-safe representation with sensitive data redacted"""
        return {
            "subject": self.subject.to_log_safe(),
            "resource": self.resource.to_log_safe(),
            "action": self.action.to_log_safe(),
            "context": self.context.to_log_safe(),
        }

    def __str__(self) -> str:
        return f"Can {self.subject} {self.action} {self.resource}?"


class SecureAuthResponse(BaseModel):
    """🛡️ Secure Authorization response - yes or no?"""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    decision: bool = Field(..., description="Allow or deny")
    context: Optional[Dict[str, Any]] = Field(None, description="Why this decision")

    @field_validator("context")
    @classmethod
    def validate_context(cls, v):
        if v is not None:
            return validate_attributes(v, "response_context", 20)
        return v

    @property
    def allowed(self) -> bool:
        """Is this allowed?"""
        return self.decision

    @property
    def denied(self) -> bool:
        """Is this denied?"""
        return not self.decision

    @classmethod
    def allow(
        cls, reason: Optional[str] = None, **context: Any
    ) -> "SecureAuthResponse":
        """Create a secure allow response."""
        ctx = {}
        if reason:
            ctx["reason"] = validate_string_input(reason, "response_reason", 512)
        ctx.update(context)
        return cls(decision=True, context=ctx if ctx else None)

    @classmethod
    def deny(cls, reason: Optional[str] = None, **context: Any) -> "SecureAuthResponse":
        """Create a secure deny response."""
        ctx = {}
        if reason:
            ctx["reason"] = validate_string_input(reason, "response_reason", 512)
        ctx.update(context)
        return cls(decision=False, context=ctx if ctx else None)

    def get_reason(self) -> Optional[str]:
        """Why was this decision made?"""
        if self.context:
            return self.context.get("reason")
        return None

    def to_log_safe(self) -> Dict[str, Any]:
        """Return log-safe representation"""
        return {
            "decision": self.decision,
            "context": sanitize_for_logging(self.context) if self.context else None,
        }

    def __str__(self) -> str:
        status = "ALLOW" if self.decision else "DENY"
        reason = self.get_reason()
        if reason:
            return f"{status}: {reason}"
        return status


# Secure aliases for easier usage
Subject = SecureSubject  # Who is asking?
Resource = SecureResource  # What do they want?
Action = SecureAction  # How do they want to use it?
Context = SecureContext  # When and where?

Request = SecureAuthRequest  # The question
Response = SecureAuthResponse  # The answer

# Beautiful aliases
Who = SecureSubject
What = SecureResource
How = SecureAction
When = SecureContext

# Legacy compatibility with security warnings
import warnings


class AuthRequest(SecureAuthRequest):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "AuthRequest is deprecated. Use SecureAuthRequest for enhanced security.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class AuthResponse(SecureAuthResponse):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "AuthResponse is deprecated. Use SecureAuthResponse for enhanced security.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


# More legacy compatibility
AuthorizationRequest = SecureAuthRequest
AuthorizationResponse = SecureAuthResponse
