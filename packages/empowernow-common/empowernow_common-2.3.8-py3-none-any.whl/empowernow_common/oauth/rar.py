"""
🛡️ RAR (Rich Authorization Requests) Module - RFC 9396 with AuthZEN Compatibility

Comprehensive RAR implementation with:
- RFC 9396 compliant authorization details
- AuthZEN-friendly payload structure
- Resource and action modeling compatible with both standards
- Fine-grained permission requests with policy evaluation support
- XSS and injection protection

All implementations are production-ready and security-hardened.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from .security import SecurityError, sanitize_string_input, validate_url_security
from ..exceptions import OAuthError

logger = logging.getLogger(__name__)


class RARError(OAuthError):
    """RAR-specific errors"""

    pass


class StandardActionType(Enum):
    """Standard action types compatible with AuthZEN"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    CREATE = "create"
    UPDATE = "update"
    LIST = "list"
    ADMIN = "admin"


class StandardResourceType(Enum):
    """Standard resource types"""

    ACCOUNT = "account"
    PAYMENT = "payment"
    DOCUMENT = "document"
    API = "api"
    DATA = "data"
    SERVICE = "service"


@dataclass
class AuthZENCompatibleResource:
    """🛡️ Resource definition compatible with both RAR and AuthZEN"""

    # AuthZEN-style resource identification
    type: str  # Resource type (account, payment, etc.)
    id: Optional[str] = None  # Resource identifier

    # RAR-style location specification
    locations: Optional[List[str]] = None  # RFC 9396 locations

    # Additional resource attributes
    attributes: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate resource definition"""
        self.type = sanitize_string_input(self.type, 64, "resource_type")

        if self.id:
            self.id = sanitize_string_input(self.id, 256, "resource_id")

        if self.locations:
            validated_locations = []
            for location in self.locations:
                # Validate URLs in locations
                if location.startswith(("http://", "https://")):
                    validated_locations.append(
                        validate_url_security(location, context="resource_location")
                    )
                else:
                    validated_locations.append(
                        sanitize_string_input(location, 512, "resource_location")
                    )
            self.locations = validated_locations

    def to_authzen_resource(self) -> Dict[str, Any]:
        """Convert to AuthZEN resource format"""
        resource = {"type": self.type}

        if self.id:
            resource["id"] = self.id

        if self.attributes:
            resource.update(self.attributes)

        return resource

    def to_rar_fields(self) -> Dict[str, Any]:
        """Convert to RAR field format"""
        fields = {}

        if self.locations:
            fields["locations"] = self.locations

        if self.id:
            fields["identifier"] = self.id

        return fields


@dataclass
class AuthZENCompatibleAction:
    """🛡️ Action definition compatible with both RAR and AuthZEN"""

    name: str  # Action name (read, write, etc.)
    scope: Optional[str] = None  # Action scope
    parameters: Optional[Dict[str, Any]] = None  # Action parameters

    def __post_init__(self):
        """Validate action definition"""
        self.name = sanitize_string_input(self.name, 64, "action_name")

        if self.scope:
            self.scope = sanitize_string_input(self.scope, 128, "action_scope")

    def to_authzen_action(self) -> Dict[str, Any]:
        """Convert to AuthZEN action format"""
        action = {"name": self.name}

        if self.scope:
            action["scope"] = self.scope

        if self.parameters:
            action.update(self.parameters)

        return action


@dataclass
class AuthZENCompatibleContext:
    """🛡️ Context information compatible with AuthZEN"""

    time: Optional[str] = None  # Request time
    location: Optional[str] = None  # Client location
    device: Optional[str] = None  # Device information
    risk_score: Optional[float] = None  # Risk assessment
    custom: Optional[Dict[str, Any]] = None  # Custom context

    def __post_init__(self):
        """Validate context information"""
        if self.location:
            self.location = sanitize_string_input(
                self.location, 128, "context_location"
            )

        if self.device:
            self.device = sanitize_string_input(self.device, 256, "context_device")

        if self.risk_score is not None:
            if (
                not isinstance(self.risk_score, (int, float))
                or not 0 <= self.risk_score <= 1
            ):
                raise RARError("Risk score must be a number between 0 and 1")

    def to_authzen_context(self) -> Dict[str, Any]:
        """Convert to AuthZEN context format"""
        context = {}

        if self.time:
            context["time"] = self.time
        if self.location:
            context["location"] = self.location
        if self.device:
            context["device"] = self.device
        if self.risk_score is not None:
            context["risk_score"] = self.risk_score
        if self.custom:
            context.update(self.custom)

        return context


@dataclass
class SecureAuthorizationDetail:
    """🛡️ RFC 9396 compliant authorization detail with AuthZEN compatibility"""

    # RFC 9396 required fields
    type: str  # Authorization detail type

    # Enhanced fields for AuthZEN compatibility
    resource: Optional[AuthZENCompatibleResource] = None
    actions: Optional[List[Union[str, AuthZENCompatibleAction]]] = None
    context: Optional[AuthZENCompatibleContext] = None

    # RFC 9396 optional fields (legacy support)
    locations: Optional[List[str]] = None  # Deprecated: use resource.locations
    datatypes: Optional[List[str]] = None
    identifier: Optional[str] = None  # Deprecated: use resource.id
    privileges: Optional[List[str]] = None

    # Additional metadata
    description: Optional[str] = None
    priority: Optional[int] = None

    def __post_init__(self):
        """Validate and normalize authorization detail"""
        # Validate type
        self.type = sanitize_string_input(self.type, 64, "authorization_detail_type")

        # Migrate legacy fields to new structure
        if not self.resource and (self.locations or self.identifier):
            self.resource = AuthZENCompatibleResource(
                type=self.type, id=self.identifier, locations=self.locations
            )

        # Validate actions
        if self.actions:
            validated_actions = []
            for action in self.actions:
                if isinstance(action, str):
                    validated_actions.append(AuthZENCompatibleAction(name=action))
                elif isinstance(action, AuthZENCompatibleAction):
                    validated_actions.append(action)
                else:
                    raise RARError(f"Invalid action type: {type(action)}")
            self.actions = validated_actions

        # Validate other fields
        if self.description:
            self.description = sanitize_string_input(
                self.description, 512, "description"
            )

        if self.priority is not None:
            if not isinstance(self.priority, int) or not 1 <= self.priority <= 10:
                raise RARError("Priority must be an integer between 1 and 10")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to RFC 9396 dictionary format"""
        data = {"type": self.type}

        # Add resource information
        if self.resource:
            rar_fields = self.resource.to_rar_fields()
            data.update(rar_fields)

            # Add locations if available
            if self.resource.locations:
                data["locations"] = self.resource.locations

        # Add actions
        if self.actions:
            action_names = []
            for action in self.actions:
                if isinstance(action, AuthZENCompatibleAction):
                    action_names.append(action.name)
                else:
                    action_names.append(str(action))
            data["actions"] = action_names

        # Add legacy fields if present
        if self.datatypes:
            data["datatypes"] = self.datatypes
        if self.privileges:
            data["privileges"] = self.privileges

        # Add metadata
        if self.description:
            data["description"] = self.description
        if self.priority is not None:
            data["priority"] = self.priority

        return data

    def to_authzen_request(self, subject: Dict[str, Any]) -> Dict[str, Any]:
        """Convert to AuthZEN authorization request format"""
        request = {"subject": subject}

        # Add resource
        if self.resource:
            request["resource"] = self.resource.to_authzen_resource()
        else:
            request["resource"] = {"type": self.type}

        # Add actions
        if self.actions and len(self.actions) > 0:
            if len(self.actions) == 1:
                request["action"] = self.actions[0].to_authzen_action()
            else:
                # Multiple actions - create batch request
                request["actions"] = [
                    action.to_authzen_action() for action in self.actions
                ]

        # Add context
        if self.context:
            request["context"] = self.context.to_authzen_context()

        return request

    def get_policy_evaluation_key(self) -> str:
        """Generate unique key for policy evaluation caching"""
        components = [self.type]

        if self.resource:
            components.append(f"resource:{self.resource.type}")
            if self.resource.id:
                components.append(f"id:{self.resource.id}")

        if self.actions:
            action_names = [
                (
                    action.name
                    if isinstance(action, AuthZENCompatibleAction)
                    else str(action)
                )
                for action in self.actions
            ]
            components.append(f"actions:{','.join(sorted(action_names))}")

        return "|".join(components)


class RARBuilder:
    """🛡️ Builder for creating authorization details with validation"""

    def __init__(self):
        self._details: List[SecureAuthorizationDetail] = []

    def add_resource_access(
        self,
        resource_type: str,
        resource_id: str = None,
        actions: List[str] = None,
        locations: List[str] = None,
        **kwargs,
    ) -> "RARBuilder":
        """Add resource access authorization detail"""

        resource = AuthZENCompatibleResource(
            type=resource_type, id=resource_id, locations=locations
        )

        action_objects = []
        if actions:
            for action in actions:
                action_objects.append(AuthZENCompatibleAction(name=action))

        detail = SecureAuthorizationDetail(
            type=resource_type, resource=resource, actions=action_objects, **kwargs
        )

        self._details.append(detail)
        return self

    def add_payment_access(
        self, account_id: str, actions: List[str] = None, amount_limit: float = None
    ) -> "RARBuilder":
        """Add payment-specific authorization detail"""

        context = None
        if amount_limit:
            context = AuthZENCompatibleContext(custom={"amount_limit": amount_limit})

        return self.add_resource_access(
            resource_type="payment_initiation",
            resource_id=account_id,
            actions=actions or ["read", "write"],
            context=context,
        )

    def add_data_access(
        self, data_type: str, scope: str = None, actions: List[str] = None
    ) -> "RARBuilder":
        """Add data access authorization detail"""

        context = None
        if scope:
            context = AuthZENCompatibleContext(custom={"scope": scope})

        return self.add_resource_access(
            resource_type="data_access",
            resource_id=data_type,
            actions=actions or ["read"],
            context=context,
        )

    def build(self) -> List[SecureAuthorizationDetail]:
        """Build the authorization details list"""
        return self._details.copy()

    def create_account_access(
        self, account_id: str, actions: List[str] = None, **kwargs
    ) -> SecureAuthorizationDetail:
        """
        Create account access authorization detail

        Args:
            account_id: Account identifier
            actions: List of allowed actions (default: ["read"])
            **kwargs: Additional parameters

        Returns:
            SecureAuthorizationDetail: Account access authorization detail
        """
        if actions is None:
            actions = ["read"]

        resource = AuthZENCompatibleResource(
            type="account", id=account_id, locations=[f"/accounts/{account_id}"]
        )

        action_objects = []
        for action in actions:
            action_objects.append(AuthZENCompatibleAction(name=action))

        return SecureAuthorizationDetail(
            type="account_access", resource=resource, actions=action_objects, **kwargs
        )

    def create_api_access(
        self, endpoint: str, methods: List[str] = None, **kwargs
    ) -> SecureAuthorizationDetail:
        """
        Create API access authorization detail

        Args:
            endpoint: API endpoint path
            methods: List of HTTP methods (default: ["GET"])
            **kwargs: Additional parameters

        Returns:
            SecureAuthorizationDetail: API access authorization detail
        """
        if methods is None:
            methods = ["GET"]

        resource = AuthZENCompatibleResource(
            type="api", id=endpoint, locations=[endpoint]
        )

        action_objects = []
        for method in methods:
            action_objects.append(AuthZENCompatibleAction(name=method.lower()))

        return SecureAuthorizationDetail(
            type="api_access", resource=resource, actions=action_objects, **kwargs
        )

    def create_payment_access(
        self, amount: float, currency: str = "USD", **kwargs
    ) -> SecureAuthorizationDetail:
        """
        Create payment authorization detail

        Args:
            amount: Payment amount
            currency: Currency code (default: "USD")
            **kwargs: Additional parameters

        Returns:
            SecureAuthorizationDetail: Payment authorization detail
        """
        context = AuthZENCompatibleContext(
            custom={"amount_limit": amount, "currency": currency}
        )

        resource = AuthZENCompatibleResource(type="payment", locations=["/payments"])

        action_objects = [
            AuthZENCompatibleAction(name="create"),
            AuthZENCompatibleAction(name="approve"),
        ]

        return SecureAuthorizationDetail(
            type="payment_access",
            resource=resource,
            actions=action_objects,
            context=context,
            **kwargs,
        )

    def create_data_access(
        self, data_types: List[str], sensitivity: str = "medium", **kwargs
    ) -> SecureAuthorizationDetail:
        """
        Create data access authorization detail

        Args:
            data_types: List of data types to access
            sensitivity: Data sensitivity level
            **kwargs: Additional parameters

        Returns:
            SecureAuthorizationDetail: Data access authorization detail
        """
        context = AuthZENCompatibleContext(
            custom={"sensitivity_level": sensitivity, "data_types": data_types}
        )

        resource = AuthZENCompatibleResource(
            type="data", locations=[f"/data/{dt}" for dt in data_types]
        )

        action_objects = [
            AuthZENCompatibleAction(name="read"),
            AuthZENCompatibleAction(name="process"),
        ]

        return SecureAuthorizationDetail(
            type="data_access",
            resource=resource,
            actions=action_objects,
            context=context,
            **kwargs,
        )


# Factory functions for common authorization patterns
def create_account_access_detail(
    account_id: str, actions: List[str] = None, balance_limit: float = None
) -> SecureAuthorizationDetail:
    """Create account access authorization detail"""
    resource = AuthZENCompatibleResource(type="account", id=account_id)

    action_objects = []
    for action in actions or ["read"]:
        action_objects.append(AuthZENCompatibleAction(name=action))

    context = None
    if balance_limit:
        context = AuthZENCompatibleContext(custom={"balance_limit": balance_limit})

    return SecureAuthorizationDetail(
        type="account_access",
        resource=resource,
        actions=action_objects,
        context=context,
    )


def create_api_access_detail(
    api_endpoint: str, methods: List[str] = None, rate_limit: int = None
) -> SecureAuthorizationDetail:
    """Create API access authorization detail"""
    resource = AuthZENCompatibleResource(type="api", locations=[api_endpoint])

    action_objects = []
    for method in methods or ["GET"]:
        action_objects.append(AuthZENCompatibleAction(name=method.lower()))

    context = None
    if rate_limit:
        context = AuthZENCompatibleContext(custom={"rate_limit": rate_limit})

    return SecureAuthorizationDetail(
        type="api_access", resource=resource, actions=action_objects, context=context
    )
