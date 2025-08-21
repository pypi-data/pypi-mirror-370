from __future__ import annotations

"""
EmpowerNow OAuth Client – Modular Architecture

Clean, maintainable OAuth 2.1 client that orchestrates focused modules:
- security: Core security functions
- dpop: DPoP (Demonstrating Proof of Possession)
- par: PAR (Pushed Authorization Requests) & PKCE
- jarm: JARM (JWT Secured Authorization Response Mode)
- jar: JAR (JWT Secured Authorization Request)
- rar: RAR (Rich Authorization Requests)
- ciba: CIBA (Client Initiated Backchannel Authentication)

Each module is focused, testable, and maintainable.
"""

import httpx
import json
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from base64 import urlsafe_b64encode
from jose import jwt as jose_jwt  # python-jose
from cryptography.hazmat.primitives import serialization
from enum import Enum
import anyio
from typing import TYPE_CHECKING

# Import from focused modules
from .security import (
    SecurityError,
    SecurityContext,
    validate_url_security,
    sanitize_string_input,
    generate_secure_token,
)
from .dpop import DPoPManager, DPoPError
from .par import PARManager, PARError, PARResponse
from .jarm import JARMManager, JARMError
from .jar import JARManager, JARError as JARAuthError, generate_jar_signing_key
from .ciba import CIBAManager, CIBARequest, CIBAError
from .rar import (
    SecureAuthorizationDetail,
    RARError,
    RARBuilder,
    AuthZENCompatibleResource,
    AuthZENCompatibleAction,
    AuthZENCompatibleContext,
    StandardActionType,
    StandardResourceType,
    create_account_access_detail,
    create_api_access_detail,
)
from .network import RetryPolicy, DEFAULT_RETRY_POLICY

# Optional: only import cryptography when mTLS is enabled to avoid heavy dependency upfront
try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
except ImportError:  # pragma: no cover – cryptography optional until mTLS enabled
    x509 = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class SecureOAuthConfig:
    """🛡️ Secure OAuth configuration"""

    client_id: str
    client_secret: str
    token_url: str
    authorization_url: str

    # Optional endpoints
    par_endpoint: Optional[str] = None
    ciba_endpoint: Optional[str] = None
    introspection_url: Optional[str] = None
    revocation_url: Optional[str] = None

    # Default scope
    scope: Optional[str] = None
    
    # Token endpoint authentication method (RFC 7591)
    token_endpoint_auth_method: str = "client_secret_basic"

    def __post_init__(self):
        """Validate configuration"""
        self.client_id = sanitize_string_input(self.client_id, 256, "client_id")
        # Allow empty client_secret only for public clients (token_endpoint_auth_method == none)
        if self.token_endpoint_auth_method == "none":
            # normalize to empty string; no Basic/Post secret should be sent by caller
            self.client_secret = ""
        else:
            self.client_secret = sanitize_string_input(
                self.client_secret, 512, "client_secret"
            )
        self.token_url = validate_url_security(self.token_url, context="token_url")
        self.authorization_url = validate_url_security(
            self.authorization_url, context="authorization_url"
        )

        if self.par_endpoint:
            self.par_endpoint = validate_url_security(
                self.par_endpoint, context="par_endpoint"
            )

        if self.ciba_endpoint:
            self.ciba_endpoint = validate_url_security(
                self.ciba_endpoint, context="ciba_endpoint"
            )
            
        # Validate token endpoint authentication method
        valid_auth_methods = {
            "client_secret_basic",
            "client_secret_post", 
            "private_key_jwt",
            "none"
        }
        if self.token_endpoint_auth_method not in valid_auth_methods:
            raise ValueError(
                f"Invalid token_endpoint_auth_method: {self.token_endpoint_auth_method}. "
                f"Must be one of: {', '.join(sorted(valid_auth_methods))}"
            )


@dataclass
class HardenedToken:
    """🛡️ Secure OAuth token with comprehensive metadata"""

    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    id_token: Optional[str] = None

    # Security metadata
    client_fingerprint: Optional[str] = None
    issued_at: Optional[datetime] = None
    token_binding: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate token data"""
        self.access_token = sanitize_string_input(
            self.access_token, 4096, "access_token", allow_special_chars=True
        )

        if not self.issued_at:
            self.issued_at = datetime.now(timezone.utc)

    def is_expired(self) -> bool:
        """Check if token is expired"""
        if not self.expires_in or not self.issued_at:
            return False

        expiry_time = self.issued_at + timedelta(seconds=self.expires_in)
        return datetime.now(timezone.utc) >= expiry_time

    def is_dpop_bound(self) -> bool:
        """Check if token is DPoP-bound"""
        return (
            self.token_binding
            and self.token_binding.get("method") == "dpop"
            and "jwk_thumbprint" in self.token_binding
        )


@dataclass
class PrivateKeyJWTConfig:
    signing_key: Any
    signing_alg: str = "RS256"
    assertion_ttl: int = 300  # seconds
    kid: Optional[str] = None

    def to_jwt(self, client_id: str, token_url: str) -> str:
        now = int(time.time())
        payload = {
            "iss": client_id,
            "sub": client_id,
            "aud": token_url,
            "iat": now,
            "exp": now + self.assertion_ttl,
            "jti": generate_secure_token(16),
        }

        headers = {"kid": self.kid} if self.kid else None
        return jose_jwt.encode(payload, self.signing_key, algorithm=self.signing_alg, headers=headers)


class HardenedOAuth:
    """🛡️ Enterprise-grade OAuth client with modular security features"""

    def __init__(
        self,
        config: Optional[SecureOAuthConfig] = None,
        user_agent: str = "EmpowerNow-SecureOAuth/2.0",
        *,
        retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
        # Alternative initialization with individual parameters
        issuer_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_endpoint_auth_method: str = "client_secret_basic",
        fips_mode: bool = False,
        timeout_seconds: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize secure OAuth client

        Args:
            config: OAuth configuration (if provided)
            user_agent: User agent string for requests
            issuer_url: Alternative - OAuth issuer URL for OIDC discovery
            client_id: Alternative - OAuth client ID  
            client_secret: Alternative - OAuth client secret
            token_endpoint_auth_method: Token endpoint auth method
            fips_mode: Enable FIPS mode (currently unused, for compatibility)
            timeout_seconds: Request timeout (currently unused, for compatibility)
            max_retries: Retry attempts (currently unused, for compatibility)
        """
        # Handle alternative initialization with individual parameters
        if config is None:
            if not issuer_url or not client_id:
                raise ValueError("Either config must be provided, or issuer_url and client_id must be specified")
            
            # Create config from individual parameters
            # Use standard OAuth endpoints based on issuer URL
            issuer_base = issuer_url.rstrip('/')
            
            config = SecureOAuthConfig(
                client_id=client_id,
                client_secret=client_secret or "",
                token_url=f"{issuer_base}/token",
                authorization_url=f"{issuer_base}/authorize",
                token_endpoint_auth_method=token_endpoint_auth_method,
            )
        
        self.config = config
        self.user_agent = user_agent

        # Create security context
        self._security_context = SecurityContext.create(
            user_agent=user_agent, client_id=config.client_id
        )

        # Initialize feature modules
        self._dpop_manager = DPoPManager()
        self._par_manager = PARManager()
        self._jarm_manager = JARMManager(config.client_id)
        self._jar_manager = JARManager(config.client_id)
        self._ciba_manager = CIBAManager(config.client_id, config.client_secret)

        # mTLS settings (runtime configurable)
        self._mtls_cert: Optional[str] = None
        self._mtls_key: Optional[str] = None

        # PKJWT
        self._pkjwt_config: Optional[PrivateKeyJWTConfig] = None

        self._retry_policy = retry_policy

        # Connection pooling – one AsyncClient per instance
        self._http_client: Optional[httpx.AsyncClient] = None
        # DPoP nonce holder (set on 401 with use_dpop_nonce)
        self._dpop_nonce: Optional[str] = None

        logger.info(
            "🛡️ Secure OAuth client initialized",
            extra={
                "client_id": config.client_id,
                "security_fingerprint": self._security_context.client_fingerprint[:16]
                + "...",
            },
        )

    # ==================== MTLS METHODS ====================

    def enable_mtls(
        self, cert_path: str, key_path: str, *, hot_reload: bool = False
    ) -> None:
        """Enable Mutual-TLS client authentication.

        Args:
            cert_path: Path to PEM-encoded client certificate (chain allowed).
            key_path:  Path to PEM-encoded private key.
        """

        if not Path(cert_path).exists():
            raise FileNotFoundError(f"Client certificate not found: {cert_path}")
        if not Path(key_path).exists():
            raise FileNotFoundError(f"Client key not found: {key_path}")

        cert_path = Path(cert_path).expanduser().resolve()
        key_path = Path(key_path).expanduser().resolve()

        self._mtls_cert = str(cert_path)
        self._mtls_key = str(key_path)

        # Track mtime for hot-reload
        self._mtls_cert_mtime = cert_path.stat().st_mtime  # type: ignore
        self._mtls_key_mtime = key_path.stat().st_mtime  # type: ignore
        self._mtls_hot_reload = hot_reload

        # Lazy import cryptography for thumbprint generation
        if x509:
            try:
                with open(cert_path, "rb") as f:
                    cert_data = f.read()
                cert_obj = x509.load_pem_x509_certificate(cert_data, default_backend())
                digest = cert_obj.fingerprint(hashes.SHA256())
                # base64url-encode thumbprint
                thumb_b64 = urlsafe_b64encode(digest).rstrip(b"=").decode()
                self._mtls_cert_thumbprint = thumb_b64  # type: ignore
            except Exception as e:  # pragma: no cover – thumbprint best-effort
                logger.warning(f"Could not compute certificate thumbprint: {e}")
                self._mtls_cert_thumbprint = None  # type: ignore
        else:
            self._mtls_cert_thumbprint = None  # type: ignore

        logger.info(
            "🛡️ mTLS enabled for OAuth client",
            extra={
                "cert": self._mtls_cert,
                "has_thumbprint": bool(self._mtls_cert_thumbprint),
            },
        )

    def is_mtls_enabled(self) -> bool:
        """Return True if Mutual-TLS is configured."""
        return bool(self._mtls_cert and self._mtls_key)

    # ==================== INTERNAL MTLS HOT-RELOAD ====================

    def _maybe_reload_mtls_credentials(self):
        if not (self.is_mtls_enabled() and getattr(self, "_mtls_hot_reload", False)):
            return

        cert_path = Path(self._mtls_cert)
        key_path = Path(self._mtls_key)

        if cert_path.stat().st_mtime != getattr(
            self, "_mtls_cert_mtime", 0
        ) or key_path.stat().st_mtime != getattr(self, "_mtls_key_mtime", 0):
            logger.info("🔄 Detected updated mTLS certificate/key – reloading")
            # Update stored mtimes
            self._mtls_cert_mtime = cert_path.stat().st_mtime  # type: ignore
            self._mtls_key_mtime = key_path.stat().st_mtime  # type: ignore

            # Recompute thumbprint
            if x509:
                try:
                    with open(cert_path, "rb") as f:
                        cert_obj = x509.load_pem_x509_certificate(
                            f.read(), default_backend()
                        )
                    digest = cert_obj.fingerprint(hashes.SHA256())
                    self._mtls_cert_thumbprint = (
                        urlsafe_b64encode(digest).rstrip(b"=").decode()
                    )
                except Exception as e:
                    logger.warning(f"Could not recompute cert thumbprint: {e}")

    # ==================== DPoP METHODS ====================

    def enable_dpop(self, algorithm: str = "ES256") -> str:
        """Enable DPoP (Demonstrating Proof of Possession)"""
        return self._dpop_manager.enable_dpop()

    async def get_dpop_bound_token(self, **kwargs) -> HardenedToken:
        """Get DPoP-bound access token (async)."""
        if not self._dpop_manager.is_enabled():
            raise DPoPError("DPoP not enabled. Call enable_dpop() first.")

        return await self.get_token(**kwargs)

    # ==================== PAR METHODS ====================

    async def create_par_request(
        self,
        redirect_uri: str,
        scope: Optional[str] = None,
        authorization_details: Optional[List[SecureAuthorizationDetail]] = None,
        **kwargs,
    ) -> PARResponse:
        """Create Pushed Authorization Request"""
        if not self.config.par_endpoint:
            raise PARError("PAR not configured - missing par_endpoint")

        # Create PAR request using manager
        par_request, code_verifier = self._par_manager.create_par_request(
            client_id=self.config.client_id,
            redirect_uri=redirect_uri,
            scope=scope or self.config.scope,
            authorization_details=(
                [detail.to_dict() for detail in authorization_details]
                if authorization_details
                else None
            ),
            **kwargs,
        )

        # Send PAR request
        client = await self._get_secure_http_client(self.config.par_endpoint)

        headers = self._get_security_headers()
        headers = self._dpop_manager.add_dpop_header(
            headers, "POST", self.config.par_endpoint
        )

        response = await client.post(
            self.config.par_endpoint,
            data=par_request.to_dict(),
            auth=(self.config.client_id, self.config.client_secret),
            headers=headers,
        )
        response.raise_for_status()

        par_data = response.json()
        return PARResponse(
            request_uri=par_data["request_uri"], expires_in=par_data["expires_in"]
        )

    def build_authorization_url(self, par_response: PARResponse, **kwargs) -> str:
        """Build authorization URL using PAR request URI"""
        return self._par_manager.build_authorization_url(
            authorization_url=self.config.authorization_url,
            client_id=self.config.client_id,
            request_uri=par_response.request_uri,
            **kwargs,
        )

    # ==================== JARM METHODS ====================

    def enable_jarm(self, response_mode: str = "jwt", **kwargs) -> None:
        """Enable JARM (JWT Secured Authorization Response Mode)"""
        self._jarm_manager.enable_jarm(response_mode=response_mode, **kwargs)

    def process_jarm_response(self, response_data) -> Dict[str, Any]:
        """Process JARM authorization response"""
        return self._jarm_manager.process_response(response_data)

    # ==================== JAR METHODS ====================

    def configure_jar(
        self, signing_algorithm: str = "RS256", signing_key=None, **kwargs
    ) -> None:
        """Configure JAR (JWT Secured Authorization Request)"""
        if not signing_key:
            # Generate a new signing key
            signing_key = generate_jar_signing_key(signing_algorithm)

        self._jar_manager.configure_jar(
            signing_algorithm=signing_algorithm, signing_key=signing_key, **kwargs
        )

    def create_jar_request_object(
        self, authorization_params: Dict[str, Any], audience: str, expires_in: int = 600
    ) -> str:
        """Create JAR request object"""
        if not self._jar_manager.is_configured():
            raise JARAuthError("JAR not configured. Call configure_jar() first.")

        return self._jar_manager.create_request_object(
            authorization_params=authorization_params,
            audience=audience,
            expires_in=expires_in,
        )

    # ==================== CORE TOKEN METHODS ====================

    async def get_token(self, **params) -> HardenedToken:  # noqa: D401 – async public
        """Return an access token (async).  Preferred in new code."""

        return await self._secure_request_token(**params)

    async def exchange_authorization_code(
        self, authorization_code: str, state: str, redirect_uri: str, **kwargs
    ) -> HardenedToken:
        """Exchange authorization code for tokens with PKCE validation"""
        # Validate parameters using PAR manager
        token_params = self._par_manager.validate_authorization_code_params(
            authorization_code, state, redirect_uri
        )
        token_params.update(kwargs)

        # Make token request
        return await self._secure_request_token(**token_params)

    # ==================== COMPLETE SECURE FLOWS ====================

    async def secure_authorization_flow(
        self,
        redirect_uri: str,
        scope: Optional[str] = None,
        authorization_details: Optional[List[SecureAuthorizationDetail]] = None,
        **kwargs,
    ) -> Tuple[str, str]:
        """Complete secure authorization flow with PAR + PKCE"""
        par_response = await self.create_par_request(
            redirect_uri=redirect_uri,
            scope=scope,
            authorization_details=authorization_details,
            **kwargs,
        )

        authorization_url = self.build_authorization_url(par_response)
        state = generate_secure_token(32)  # In practice, extract from PAR

        return authorization_url, state

    async def secure_authorization_flow_with_jarm(
        self,
        redirect_uri: str,
        scope: Optional[str] = None,
        authorization_details: Optional[List[SecureAuthorizationDetail]] = None,
        **kwargs,
    ) -> Tuple[str, str]:
        """Complete secure authorization flow with PAR + PKCE + JARM"""
        if not self._jarm_manager.is_enabled():
            raise JARMError("JARM not enabled. Call enable_jarm() first.")

        # Add JARM response mode
        kwargs["response_mode"] = self._jarm_manager.get_response_mode()

        return await self.secure_authorization_flow(
            redirect_uri=redirect_uri,
            scope=scope,
            authorization_details=authorization_details,
            **kwargs,
        )

    async def secure_authorization_flow_with_jar_and_jarm(
        self,
        redirect_uri: str,
        scope: Optional[str] = None,
        authorization_details: Optional[List[SecureAuthorizationDetail]] = None,
        **kwargs,
    ) -> Tuple[str, str]:
        """Complete secure authorization flow with JAR + PAR + PKCE + JARM"""
        if not self._jar_manager.is_configured():
            raise JARAuthError("JAR not configured. Call configure_jar() first.")

        if not self._jarm_manager.is_enabled():
            raise JARMError("JARM not enabled. Call enable_jarm() first.")

        # Build authorization parameters
        auth_params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": redirect_uri,
            "scope": scope or self.config.scope,
            "response_mode": self._jarm_manager.get_response_mode(),
        }

        # Add authorization details if provided
        if authorization_details:
            auth_params["authorization_details"] = [
                detail.to_dict() for detail in authorization_details
            ]

        # Add any additional parameters
        auth_params.update(kwargs)

        # Create JAR request object
        request_object = self.create_jar_request_object(
            authorization_params=auth_params, audience=self.config.authorization_url
        )

        # Use request object in authorization URL
        # URL-encode request object to ensure cross-IdP compatibility
        from urllib.parse import urlencode
        query = urlencode({"client_id": self.config.client_id, "request": request_object})
        authorization_url = f"{self.config.authorization_url}?{query}"
        state = generate_secure_token(32)

        logger.info(
            "🛡️ Advanced secure authorization flow initiated",
            extra={
                "jar_enabled": True,
                "jarm_enabled": True,
                "authorization_url_ready": True,
            },
        )

        return authorization_url, state

    # ==================== CIBA METHODS ====================

    def configure_ciba(
        self, ciba_endpoint: str = None, token_endpoint: str = None
    ) -> None:
        """Configure CIBA (Client Initiated Backchannel Authentication)"""
        ciba_endpoint = ciba_endpoint or self.config.ciba_endpoint
        token_endpoint = token_endpoint or self.config.token_url

        if not ciba_endpoint:
            raise CIBAError("CIBA endpoint required")

        if not token_endpoint:
            raise CIBAError("Token endpoint required")

        self._ciba_manager.configure_ciba(
            ciba_endpoint=ciba_endpoint, token_endpoint=token_endpoint
        )

    async def initiate_ciba_authentication(self, request: CIBARequest):
        """Initiate CIBA authentication"""
        if not self._ciba_manager.is_configured():
            # Auto-configure if endpoint available
            if self.config.ciba_endpoint:
                self.configure_ciba()
            else:
                raise CIBAError("CIBA not configured. Call configure_ciba() first.")

        return await self._ciba_manager.initiate_authentication(request)

    async def ciba_authenticate_user(
        self, scope: str, login_hint: str = None, **kwargs
    ):
        """Complete CIBA authentication flow"""
        if not self._ciba_manager.is_configured():
            # Auto-configure if endpoint available
            if self.config.ciba_endpoint:
                self.configure_ciba()
            else:
                raise CIBAError("CIBA not configured. Call configure_ciba() first.")

        return await self._ciba_manager.authenticate_user(
            scope=scope, login_hint=login_hint, **kwargs
        )

    # ==================== RAR METHODS ====================

    def create_rar_builder(self) -> RARBuilder:
        """Create RAR builder for AuthZEN-compatible authorization details"""
        return RARBuilder()

    def create_account_access_request(
        self, account_id: str, actions: List[str] = None, **kwargs
    ):
        """Create account access authorization detail"""
        return create_account_access_detail(account_id, actions, **kwargs)

    def create_api_access_request(
        self, api_endpoint: str, methods: List[str] = None, **kwargs
    ):
        """Create API access authorization detail"""
        return create_api_access_detail(api_endpoint, methods, **kwargs)

    def convert_rar_to_authzen(
        self,
        authorization_details: List[SecureAuthorizationDetail],
        subject: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Convert RAR authorization details to AuthZEN requests"""
        authzen_requests = []
        for detail in authorization_details:
            authzen_requests.append(detail.to_authzen_request(subject))
        return authzen_requests

    # ==================== INTERNAL METHODS ====================

    def _get_security_headers(self) -> Dict[str, str]:
        """Get standard security headers"""
        return {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
            "X-Request-ID": generate_secure_token(16),
            "X-Client-Fingerprint": self._security_context.client_fingerprint,
        }

    async def _get_secure_http_client(self, base_url: str) -> httpx.AsyncClient:
        """Get secure HTTP client with TLS validation"""

        if self._http_client:
            return self._http_client

        client_kwargs = dict(
            base_url=base_url,
            timeout=30.0,
            verify=True,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )

        if self.is_mtls_enabled():
            client_kwargs["cert"] = (self._mtls_cert, self._mtls_key)  # type: ignore

        self._http_client = httpx.AsyncClient(**client_kwargs)
        return self._http_client

    async def aclose(self):
        if self._http_client:
            await self._http_client.aclose()

    async def _secure_request_token(self, **params) -> HardenedToken:
        """Internal secure token request"""
        import asyncio, httpx

        async def _request_token() -> HardenedToken:
            max_attempts = self._retry_policy.attempts  # original try + retries

            for attempt in range(max_attempts):
                try:
                    client = await self._get_secure_http_client(self.config.token_url)

                    headers = self._get_security_headers()
                    headers = self._dpop_manager.add_dpop_header(
                        headers, "POST", self.config.token_url, nonce=self._dpop_nonce
                    )

                    # merge caller supplied params (PKCE, etc.)
                    data = {
                        "grant_type": "client_credentials",
                    }
                    data.update(params)

                    auth = None
                    # Handle different token endpoint authentication methods (RFC 7591)
                    if self.config.token_endpoint_auth_method == "private_key_jwt" and self._pkjwt_config:
                        # Private Key JWT authentication
                        assertion = self._pkjwt_config.to_jwt(
                            self.config.client_id, self.config.token_url
                        )
                        data.update(
                            {
                                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                                "client_assertion": assertion,
                            }
                        )
                    elif self.config.token_endpoint_auth_method == "client_secret_post":
                        # Client credentials in POST body
                        data.update(
                            {
                                "client_id": self.config.client_id,
                                "client_secret": self.config.client_secret,
                            }
                        )
                    elif self.config.token_endpoint_auth_method == "client_secret_basic":
                        # Client credentials in Authorization header (Basic Auth)
                        auth = (self.config.client_id, self.config.client_secret)
                    elif self.config.token_endpoint_auth_method == "none":
                        # Public client - only client_id in POST body
                        data.update({"client_id": self.config.client_id})
                    else:
                        # Fallback for backward compatibility (legacy behavior)
                        if self._pkjwt_config:
                            assertion = self._pkjwt_config.to_jwt(
                                self.config.client_id, self.config.token_url
                            )
                            data.update(
                                {
                                    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                                    "client_assertion": assertion,
                                }
                            )
                        else:
                            auth = (self.config.client_id, self.config.client_secret)

                    response = await client.post(
                        self.config.token_url, data=data, headers=headers, auth=auth
                    )
                    response.raise_for_status()

                    # Parse JSON; do not log secrets at INFO
                    try:
                        token_data = response.json()
                        if logger.isEnabledFor(logging.DEBUG):
                            redacted = {k: ("<redacted>" if k in {"access_token","refresh_token","id_token"} else v) for k, v in token_data.items()}
                            logger.debug("Token response parsed: %s", str(redacted)[:500])
                    except Exception as json_error:
                        logger.error(f"Failed to parse token response JSON: {json_error}")
                        logger.debug(f"Raw response text: {response.text}")
                        logger.debug(f"Response status: {response.status_code}")
                        logger.debug(f"Response headers: {dict(response.headers)}")
                        raise ValueError(f"Invalid JSON in token response: {json_error}") from json_error

                    # Exclusivity check
                    if self._dpop_manager.is_enabled() and self.is_mtls_enabled():
                        logger.warning(
                            "Both DPoP and mTLS enabled – preferring DPoP for token_binding as per RFC guidance"
                        )

                    if self._dpop_manager.is_enabled():
                        token_data["token_binding"] = {
                            "method": "dpop",
                            "jwk_thumbprint": self._dpop_manager.get_jwk_thumbprint(),
                        }
                    elif self.is_mtls_enabled() and getattr(
                        self, "_mtls_cert_thumbprint", None
                    ):
                        token_data["token_binding"] = {
                            "method": "mtls",
                            "cert_thumbprint": self._mtls_cert_thumbprint,
                        }

                    # Filter token_data to only include parameters that HardenedToken accepts
                    # Include id_token so callers can establish user identity when using OIDC
                    # CRITICAL FIX: Exclude client_fingerprint from filtered data to avoid duplicate keyword args
                    filtered_token_data = {
                        k: v for k, v in token_data.items() 
                        if k in {
                            'access_token', 'token_type', 'expires_in', 'refresh_token', 
                            'scope', 'id_token', 'issued_at', 'token_binding'
                        }
                    }
                    
                    return HardenedToken(
                        **filtered_token_data,
                        client_fingerprint=self._security_context.client_fingerprint,
                    )
                except httpx.HTTPStatusError as exc:
                    status = exc.response.status_code
                    # Handle DPoP nonce challenge (retry once with nonce)
                    if status == 401:
                        www = exc.response.headers.get("WWW-Authenticate", "")
                        nonce = exc.response.headers.get("DPoP-Nonce") or exc.response.headers.get("dpop-nonce")
                        if ("use_dpop_nonce" in www or nonce) and attempt < max_attempts - 1:
                            self._dpop_nonce = nonce or self._dpop_nonce
                            continue
                    retryable_status = (500 <= status < 600) or (
                        status == 429 and "retry-after" in exc.response.headers
                    )
                    if retryable_status and attempt < max_attempts - 1:
                        # honour Retry-After if available (delta-seconds or HTTP-date)
                        if status == 429:
                            try:
                                import email.utils, time
                                ra = exc.response.headers.get("retry-after", "")
                                try:
                                    delay = int(ra)
                                except ValueError:
                                    ts = email.utils.parsedate_to_datetime(ra)
                                    delay = max(0, int(ts.timestamp() - time.time()))
                                await anyio.sleep(delay)
                            except Exception:
                                pass
                        # continue to next retry after backoff
                    else:
                        raise
                except (httpx.TransportError, asyncio.TimeoutError) as exc:
                    if (
                        not self._retry_policy.is_retryable(exc)
                        or attempt >= max_attempts - 1
                    ):
                        raise

                # Exponential backoff via policy
                await self._retry_policy.sleep(attempt)

            raise SecurityError("Token request failed after retries")

        return await _request_token()

    # ==================== PRIVATE KEY JWT ====================

    def configure_private_key_jwt(
        self, signing_key, signing_alg: str = "RS256", assertion_ttl: int = 300, *, kid: Optional[str] = None
    ):
        """Configure private_key_jwt client authentication (RFC 7523)."""
        self._pkjwt_config = PrivateKeyJWTConfig(
            signing_key=signing_key,
            signing_alg=signing_alg,
            assertion_ttl=assertion_ttl,
            kid=kid,
        )
        logger.info("🛡️ private_key_jwt configured", extra={"alg": signing_alg})

    async def introspect_token(self, token: str) -> Dict[str, Any]:
        """RFC 7662 token introspection (requires introspection_url)."""
        if not self.config.introspection_url:
            raise SecurityError("introspection_url not configured")

        client = await self._get_secure_http_client(self.config.introspection_url)

        headers = self._get_security_headers()

        data = {"token": token, "token_type_hint": "access_token"}

        if self._pkjwt_config:
            assertion = self._pkjwt_config.to_jwt(
                self.config.client_id, self.config.introspection_url
            )
            data.update(
                {
                    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                    "client_assertion": assertion,
                }
            )
            auth = None
        else:
            auth = (self.config.client_id, self.config.client_secret)

        # Always post to full URL to avoid base_url confusion
        response = await client.post(self.config.introspection_url, data=data, headers=headers, auth=auth)
        response.raise_for_status()
        return response.json()

    async def revoke_token(
        self, token: str, token_type_hint: str = "access_token"
    ) -> None:
        """RFC 7009 token revocation."""
        if not self.config.revocation_url:
            raise SecurityError("revocation_url not configured")

        client = await self._get_secure_http_client(self.config.revocation_url)

        headers = self._get_security_headers()
        data = {"token": token, "token_type_hint": token_type_hint}

        if self._pkjwt_config:
            assertion = self._pkjwt_config.to_jwt(
                self.config.client_id, self.config.revocation_url
            )
            data.update(
                {
                    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                    "client_assertion": assertion,
                }
            )
            auth = None
        else:
            auth = (self.config.client_id, self.config.client_secret)

        # Always post to full URL to avoid base_url confusion
        response = await client.post(self.config.revocation_url, data=data, headers=headers, auth=auth)
        response.raise_for_status()
        return None

    # ------------ Grant Management (RFC 8707) helpers ------------

    def create_authorization_url_with_grant(
        self,
        par_response: PARResponse,
        *,
        action: GrantManagementAction,
        grant_id: str = None,
        **kwargs,
    ) -> str:
        """Return authorization URL with grant_management_* parameters appended."""
        base = self.build_authorization_url(par_response, **kwargs)
        gm_params = build_grant_management_params(action, grant_id)
        import urllib.parse as _u

        return base + "&" + _u.urlencode(gm_params)

    # ------------------------------------------------------------------
    # Convenience sync helper – closes pooled AsyncClient from sync code
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the underlying pooled :class:`httpx.AsyncClient`.

        This is a synchronous wrapper around :py:meth:`aclose()`, useful when
        the caller is not already running inside an event-loop.
        """

        if self._http_client and not self._http_client.is_closed:
            anyio.run(self.aclose)

    # -------------------------------------------------------------
    # Async context manager helpers to allow ``async with HardenedOAuth(...)``
    # -------------------------------------------------------------

    async def __aenter__(self):  # noqa: D401 – magic method
        # Simply return self; HTTP client is initialised lazily on demand.
        return self

    async def __aexit__(self, exc_type, exc, tb):  # noqa: D401 – magic method
        await self.aclose()
        # Do **not** suppress exceptions – return False implicitly.

    # Backward-compat alias expected by some legacy tests

    async def secure_get_token(self, **params) -> HardenedToken:  # noqa: D401
        """Deprecated wrapper around _secure_request_token (async)."""
        return await self._secure_request_token(**params)


# Public alias
OAuth = HardenedOAuth
Token = HardenedToken
AdvancedToken = HardenedToken

# Removed legacy classes SecureOAuth / AdvancedOAuth (prior to first GA)
# OAuthConfig remains for type-compatibility but points to SecureOAuthConfig
OAuthConfig = SecureOAuthConfig

# ==================== GRANT MANAGEMENT ====================


class GrantManagementAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


def build_grant_management_params(
    action: GrantManagementAction, grant_id: Optional[str] = None
) -> Dict[str, str]:
    """Return RFC 8707 compliant query/body parameters."""
    params = {"grant_management_action": action.value}
    if grant_id:
        params["grant_id"] = grant_id
    return params
