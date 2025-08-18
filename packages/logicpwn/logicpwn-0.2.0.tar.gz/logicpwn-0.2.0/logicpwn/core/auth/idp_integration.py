"""
Identity Provider (IdP) Integration for LogicPwn.

Provides integration with external identity providers including:
- Generic OIDC providers
- Enterprise identity systems
- Social login providers
- Custom IdP implementations
- Federation protocols
- Attribute mapping and transformation

Features:
- Multi-IdP support
- Dynamic provider discovery
- Attribute mapping
- Session federation
- Provider-specific optimizations
- Fallback authentication chains
"""
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
from urllib.parse import urlencode, parse_qs, urlparse
from abc import ABC, abstractmethod

import requests
from loguru import logger
from pydantic import BaseModel, Field, field_validator

from logicpwn.exceptions import AuthenticationError, ValidationError, NetworkError
from logicpwn.core.performance import monitor_performance
from .oauth_handler import OAuthHandler, OAuthConfig, OAuthToken
from .saml_handler import SAMLHandler, SAMLConfig, SAMLAssertion
from .jwt_handler import JWTHandler, JWTConfig, JWTClaims


@dataclass
class UserProfile:
    """Unified user profile from IdP."""
    user_id: str
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    provider: Optional[str] = None
    raw_profile: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthenticationSession:
    """Authentication session from IdP."""
    session_id: str
    user_profile: UserProfile
    provider: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    expires_at: Optional[float] = None
    session_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        if not self.expires_at:
            return False
        return time.time() >= self.expires_at


class AttributeMapping(BaseModel):
    """Attribute mapping configuration."""
    user_id: Union[str, List[str]] = Field(default=["sub", "id", "user_id"], description="User ID mapping")
    email: Union[str, List[str]] = Field(default=["email", "mail", "emailAddress"], description="Email mapping")
    username: Union[str, List[str]] = Field(default=["preferred_username", "username", "login"], description="Username mapping")
    first_name: Union[str, List[str]] = Field(default=["given_name", "firstName", "first_name"], description="First name mapping")
    last_name: Union[str, List[str]] = Field(default=["family_name", "lastName", "last_name"], description="Last name mapping")
    display_name: Union[str, List[str]] = Field(default=["name", "displayName", "display_name"], description="Display name mapping")
    avatar_url: Union[str, List[str]] = Field(default=["picture", "avatar_url", "photo"], description="Avatar URL mapping")
    roles: Union[str, List[str]] = Field(default=["roles", "role", "authorities"], description="Roles mapping")
    groups: Union[str, List[str]] = Field(default=["groups", "group", "memberOf"], description="Groups mapping")
    
    def extract_value(self, data: Dict[str, Any], field_name: str) -> Any:
        """Extract value from data using field mapping."""
        mapping = getattr(self, field_name)
        
        if isinstance(mapping, str):
            mapping = [mapping]
        
        for key in mapping:
            if key in data:
                return data[key]
        
        return None


class IdPConfig(BaseModel):
    """Identity Provider configuration."""
    
    # Provider identification
    provider_id: str = Field(..., description="Unique provider identifier")
    provider_name: str = Field(..., description="Human-readable provider name")
    provider_type: str = Field(..., description="Provider type (oidc, saml, oauth2, custom)")
    
    # Provider endpoints
    discovery_url: Optional[str] = Field(default=None, description="OIDC discovery URL")
    authorization_url: Optional[str] = Field(default=None, description="Authorization endpoint")
    token_url: Optional[str] = Field(default=None, description="Token endpoint")
    userinfo_url: Optional[str] = Field(default=None, description="UserInfo endpoint")
    logout_url: Optional[str] = Field(default=None, description="Logout endpoint")
    
    # Authentication configuration
    client_id: str = Field(..., description="Client ID")
    client_secret: Optional[str] = Field(default=None, description="Client secret")
    scope: List[str] = Field(default_factory=list, description="OAuth scopes")
    
    # Provider-specific settings
    provider_config: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific configuration")
    
    # Attribute mapping
    attribute_mapping: AttributeMapping = Field(default_factory=AttributeMapping, description="Attribute mapping")
    
    # Security settings
    validate_issuer: bool = Field(default=True, description="Validate token issuer")
    validate_audience: bool = Field(default=True, description="Validate token audience")
    require_https: bool = Field(default=True, description="Require HTTPS endpoints")
    
    # Session settings
    session_timeout: int = Field(default=3600, description="Session timeout in seconds")
    remember_me_timeout: int = Field(default=86400 * 30, description="Remember me timeout in seconds")
    
    @field_validator('provider_type')
    @classmethod
    def validate_provider_type(cls, v: str) -> str:
        valid_types = ["oidc", "saml", "oauth2", "custom"]
        if v not in valid_types:
            raise ValueError(f"Invalid provider type. Must be one of: {valid_types}")
        return v


class BaseIdPProvider(ABC):
    """Base class for identity providers."""
    
    def __init__(self, config: IdPConfig, session: Optional[requests.Session] = None):
        self.config = config
        self.session = session or requests.Session()
    
    @abstractmethod
    def get_authorization_url(self, state: Optional[str] = None, **kwargs) -> tuple[str, str]:
        """Get authorization URL for user redirection."""
        pass
    
    @abstractmethod
    def handle_callback(self, callback_data: Dict[str, Any]) -> AuthenticationSession:
        """Handle authentication callback."""
        pass
    
    @abstractmethod
    def get_user_profile(self, session: AuthenticationSession) -> UserProfile:
        """Get user profile information."""
        pass
    
    @abstractmethod
    def refresh_session(self, session: AuthenticationSession) -> AuthenticationSession:
        """Refresh authentication session."""
        pass
    
    @abstractmethod
    def logout(self, session: AuthenticationSession) -> bool:
        """Logout user session."""
        pass
    
    def _map_attributes(self, raw_data: Dict[str, Any]) -> UserProfile:
        """Map raw attributes to UserProfile."""
        mapping = self.config.attribute_mapping
        
        user_id = mapping.extract_value(raw_data, 'user_id')
        if not user_id:
            raise ValidationError("No user ID found in provider response")
        
        # Extract standard attributes
        profile = UserProfile(
            user_id=str(user_id),
            email=mapping.extract_value(raw_data, 'email'),
            username=mapping.extract_value(raw_data, 'username'),
            first_name=mapping.extract_value(raw_data, 'first_name'),
            last_name=mapping.extract_value(raw_data, 'last_name'),
            display_name=mapping.extract_value(raw_data, 'display_name'),
            avatar_url=mapping.extract_value(raw_data, 'avatar_url'),
            provider=self.config.provider_id,
            raw_profile=raw_data
        )
        
        # Extract roles and groups
        roles = mapping.extract_value(raw_data, 'roles')
        if roles:
            if isinstance(roles, str):
                profile.roles = [roles]
            elif isinstance(roles, list):
                profile.roles = [str(role) for role in roles]
        
        groups = mapping.extract_value(raw_data, 'groups')
        if groups:
            if isinstance(groups, str):
                profile.groups = [groups]
            elif isinstance(groups, list):
                profile.groups = [str(group) for group in groups]
        
        # Extract custom attributes
        standard_fields = {'user_id', 'email', 'username', 'first_name', 'last_name', 
                          'display_name', 'avatar_url', 'roles', 'groups'}
        
        profile.custom_attributes = {
            k: v for k, v in raw_data.items() 
            if k not in standard_fields
        }
        
        return profile


class OIDCProvider(BaseIdPProvider):
    """OpenID Connect identity provider."""
    
    def __init__(self, config: IdPConfig, session: Optional[requests.Session] = None):
        super().__init__(config, session)
        
        # Initialize OAuth handler
        oauth_config = self._create_oauth_config()
        self.oauth_handler = OAuthHandler(oauth_config, session)
        
        # Initialize JWT handler if needed
        if config.provider_config.get('validate_id_token', True):
            jwt_config = self._create_jwt_config()
            self.jwt_handler = JWTHandler(jwt_config, session)
        else:
            self.jwt_handler = None
    
    def _create_oauth_config(self) -> OAuthConfig:
        """Create OAuth configuration from IdP config."""
        # Auto-discover endpoints if discovery URL provided
        if self.config.discovery_url:
            try:
                discovery = self._fetch_discovery_document()
                authorization_url = discovery.get('authorization_endpoint', self.config.authorization_url)
                token_url = discovery.get('token_endpoint', self.config.token_url)
                userinfo_url = discovery.get('userinfo_endpoint', self.config.userinfo_url)
            except Exception as e:
                logger.warning(f"Failed to fetch discovery document: {e}")
                authorization_url = self.config.authorization_url
                token_url = self.config.token_url
                userinfo_url = self.config.userinfo_url
        else:
            authorization_url = self.config.authorization_url
            token_url = self.config.token_url
            userinfo_url = self.config.userinfo_url
        
        return OAuthConfig(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            authorization_url=authorization_url,
            token_url=token_url,
            userinfo_url=userinfo_url,
            scope=self.config.scope or ['openid', 'profile', 'email'],
            **self.config.provider_config
        )
    
    def _create_jwt_config(self) -> JWTConfig:
        """Create JWT configuration for ID token validation."""
        try:
            discovery = self._fetch_discovery_document()
            
            return JWTConfig(
                jwks_url=discovery.get('jwks_uri'),
                expected_issuer=discovery.get('issuer') if self.config.validate_issuer else None,
                expected_audience=self.config.client_id if self.config.validate_audience else None,
                algorithms=discovery.get('id_token_signing_alg_values_supported', ['RS256'])
            )
        except Exception as e:
            logger.warning(f"Failed to fetch discovery document for JWT config: {e}")
            # Return minimal JWT config for testing
            return JWTConfig(
                secret_key="test_fallback_secret",  # For testing only
                expected_audience=self.config.client_id if self.config.validate_audience else None,
                algorithms=['RS256', 'HS256']
            )
    
    @monitor_performance("oidc_discovery")
    def _fetch_discovery_document(self) -> Dict[str, Any]:
        """Fetch OIDC discovery document."""
        if not self.config.discovery_url:
            raise ValidationError("No discovery URL configured")
        
        try:
            response = self.session.get(self.config.discovery_url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise NetworkError(f"Failed to fetch discovery document: {e}")
    
    def get_authorization_url(self, state: Optional[str] = None, **kwargs) -> tuple[str, str]:
        """Get OIDC authorization URL."""
        return self.oauth_handler.get_authorization_url()
    
    @monitor_performance("oidc_callback_handling")
    def handle_callback(self, callback_data: Dict[str, Any]) -> AuthenticationSession:
        """Handle OIDC callback."""
        code = callback_data.get('code')
        state = callback_data.get('state')
        
        if not code:
            error = callback_data.get('error', 'unknown_error')
            error_description = callback_data.get('error_description', 'No authorization code received')
            raise AuthenticationError(f"OIDC error: {error} - {error_description}")
        
        # Exchange code for tokens
        token = self.oauth_handler.exchange_code_for_token(code, state)
        
        # Validate ID token if present
        id_token_claims = None
        if token.id_token and self.jwt_handler:
            try:
                id_token_claims = self.jwt_handler.validate_token(token.id_token)
            except Exception as e:
                logger.warning(f"ID token validation failed: {e}")
        
        # Get user profile
        user_profile = self._get_user_profile_from_token(token, id_token_claims)
        
        # Create session
        session = AuthenticationSession(
            session_id=f"oidc_{int(time.time())}_{user_profile.user_id}",
            user_profile=user_profile,
            provider=self.config.provider_id,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            id_token=token.id_token,
            expires_at=token.expires_at,
            session_data={'token': token}
        )
        
        logger.info(f"OIDC authentication successful for user: {user_profile.user_id}")
        return session
    
    def _get_user_profile_from_token(self, token: OAuthToken, id_token_claims: Optional[JWTClaims] = None) -> UserProfile:
        """Get user profile from token and claims."""
        # Start with ID token claims if available
        profile_data = {}
        if id_token_claims:
            profile_data.update(id_token_claims.custom_claims)
            if id_token_claims.sub:
                profile_data['sub'] = id_token_claims.sub
        
        # Fetch additional data from UserInfo endpoint if available
        if self.oauth_handler.config.userinfo_url:
            try:
                userinfo = self.oauth_handler.get_user_info()
                profile_data.update(userinfo)
            except Exception as e:
                logger.warning(f"Failed to fetch UserInfo: {e}")
        
        return self._map_attributes(profile_data)
    
    def get_user_profile(self, session: AuthenticationSession) -> UserProfile:
        """Get current user profile."""
        return session.user_profile
    
    def refresh_session(self, session: AuthenticationSession) -> AuthenticationSession:
        """Refresh OIDC session."""
        if not session.refresh_token:
            raise AuthenticationError("No refresh token available")
        
        # Refresh OAuth token
        self.oauth_handler.token = session.session_data.get('token')
        new_token = self.oauth_handler.refresh_access_token()
        
        # Update session
        session.access_token = new_token.access_token
        session.expires_at = new_token.expires_at
        if new_token.refresh_token:
            session.refresh_token = new_token.refresh_token
        if new_token.id_token:
            session.id_token = new_token.id_token
        
        session.session_data['token'] = new_token
        
        logger.info(f"Refreshed OIDC session for user: {session.user_profile.user_id}")
        return session
    
    def logout(self, session: AuthenticationSession) -> bool:
        """Logout OIDC session."""
        # Revoke tokens
        if session.access_token:
            self.oauth_handler.token = session.session_data.get('token')
            self.oauth_handler.revoke_token(session.access_token)
        
        # Perform end session if endpoint available
        if self.config.logout_url:
            try:
                params = {}
                if session.id_token:
                    params['id_token_hint'] = session.id_token
                
                logout_url = f"{self.config.logout_url}?{urlencode(params)}"
                response = self.session.get(logout_url, timeout=10)
                
                logger.info(f"OIDC logout successful for user: {session.user_profile.user_id}")
                return response.status_code < 400
                
            except Exception as e:
                logger.warning(f"OIDC logout failed: {e}")
                return False
        
        return True


class SAMLIdPProvider(BaseIdPProvider):
    """SAML identity provider."""
    
    def __init__(self, config: IdPConfig, session: Optional[requests.Session] = None):
        super().__init__(config, session)
        
        # Create SAML configuration
        saml_config = self._create_saml_config()
        self.saml_handler = SAMLHandler(saml_config, session)
    
    def _create_saml_config(self) -> SAMLConfig:
        """Create SAML configuration from IdP config."""
        provider_config = self.config.provider_config
        
        return SAMLConfig(
            sp_entity_id=provider_config['sp_entity_id'],
            sp_acs_url=provider_config['sp_acs_url'],
            idp_entity_id=provider_config['idp_entity_id'],
            idp_sso_url=self.config.authorization_url,
            idp_slo_url=self.config.logout_url,
            **{k: v for k, v in provider_config.items() if k not in ['sp_entity_id', 'sp_acs_url', 'idp_entity_id']}
        )
    
    def get_authorization_url(self, state: Optional[str] = None, **kwargs) -> tuple[str, str]:
        """Get SAML authorization URL."""
        return self.saml_handler.create_auth_request()
    
    def handle_callback(self, callback_data: Dict[str, Any]) -> AuthenticationSession:
        """Handle SAML callback."""
        saml_response = callback_data.get('SAMLResponse')
        relay_state = callback_data.get('RelayState')
        
        if not saml_response:
            raise AuthenticationError("No SAML response received")
        
        # Process SAML response
        assertion = self.saml_handler.process_saml_response(saml_response, relay_state)
        
        # Map attributes to user profile
        profile_data = {
            'sub': assertion.subject_name_id,
            **assertion.attributes
        }
        
        user_profile = self._map_attributes(profile_data)
        
        # Create session
        session = AuthenticationSession(
            session_id=f"saml_{int(time.time())}_{user_profile.user_id}",
            user_profile=user_profile,
            provider=self.config.provider_id,
            expires_at=assertion.not_on_or_after.timestamp() if assertion.not_on_or_after else None,
            session_data={'assertion': assertion}
        )
        
        logger.info(f"SAML authentication successful for user: {user_profile.user_id}")
        return session
    
    def get_user_profile(self, session: AuthenticationSession) -> UserProfile:
        """Get current user profile."""
        return session.user_profile
    
    def refresh_session(self, session: AuthenticationSession) -> AuthenticationSession:
        """SAML sessions typically don't support refresh."""
        raise AuthenticationError("SAML sessions do not support refresh")
    
    def logout(self, session: AuthenticationSession) -> bool:
        """Logout SAML session."""
        if not self.config.logout_url:
            return True
        
        assertion = session.session_data.get('assertion')
        if assertion:
            logout_url, relay_state = self.saml_handler.create_logout_request(
                assertion.subject_name_id,
                assertion.session_index
            )
            
            # For testing purposes, we'll just log the logout URL
            # In a real implementation, you'd redirect the user
            logger.info(f"SAML logout URL: {logout_url}")
            return True
        
        return False


class IdPManager:
    """
    Identity Provider manager for multi-IdP support.
    
    Features:
    - Multiple IdP support
    - Dynamic provider selection
    - Session federation
    - Provider failover
    - Centralized user management
    """
    
    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.providers: Dict[str, BaseIdPProvider] = {}
        self.active_sessions: Dict[str, AuthenticationSession] = {}
    
    def register_provider(self, config: IdPConfig) -> BaseIdPProvider:
        """Register identity provider."""
        if config.provider_type == "oidc":
            provider = OIDCProvider(config, self.session)
        elif config.provider_type == "saml":
            provider = SAMLIdPProvider(config, self.session)
        else:
            raise ValidationError(f"Unsupported provider type: {config.provider_type}")
        
        self.providers[config.provider_id] = provider
        logger.info(f"Registered IdP: {config.provider_name} ({config.provider_id})")
        
        return provider
    
    def get_provider(self, provider_id: str) -> BaseIdPProvider:
        """Get provider by ID."""
        provider = self.providers.get(provider_id)
        if not provider:
            raise ValidationError(f"Provider not found: {provider_id}")
        return provider
    
    def list_providers(self) -> List[Dict[str, str]]:
        """List available providers."""
        return [
            {
                'provider_id': provider.config.provider_id,
                'provider_name': provider.config.provider_name,
                'provider_type': provider.config.provider_type
            }
            for provider in self.providers.values()
        ]
    
    @monitor_performance("idp_authentication")
    def authenticate(self, provider_id: str, callback_data: Dict[str, Any]) -> AuthenticationSession:
        """Authenticate user with specified provider."""
        provider = self.get_provider(provider_id)
        session = provider.handle_callback(callback_data)
        
        # Store active session
        self.active_sessions[session.session_id] = session
        
        return session
    
    def get_session(self, session_id: str) -> Optional[AuthenticationSession]:
        """Get active session by ID."""
        return self.active_sessions.get(session_id)
    
    def refresh_session(self, session_id: str) -> AuthenticationSession:
        """Refresh session."""
        session = self.get_session(session_id)
        if not session:
            raise AuthenticationError("Session not found")
        
        provider = self.get_provider(session.provider)
        refreshed_session = provider.refresh_session(session)
        
        # Update stored session
        self.active_sessions[session_id] = refreshed_session
        
        return refreshed_session
    
    def logout(self, session_id: str) -> bool:
        """Logout session."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        provider = self.get_provider(session.provider)
        success = provider.logout(session)
        
        # Remove from active sessions
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        return success
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        now = time.time()
        expired_sessions = [
            session_id for session_id, session in self.active_sessions.items()
            if session.is_expired
        ]
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        if expired_sessions:
            logger.debug(f"Cleaned up {len(expired_sessions)} expired IdP sessions")


# Convenience functions for common providers

def create_google_idp_config(client_id: str, client_secret: str, **kwargs) -> IdPConfig:
    """Create Google OIDC provider configuration."""
    return IdPConfig(
        provider_id="google",
        provider_name="Google",
        provider_type="oidc",
        discovery_url="https://accounts.google.com/.well-known/openid_configuration",
        client_id=client_id,
        client_secret=client_secret,
        scope=["openid", "email", "profile"],
        **kwargs
    )


def create_microsoft_idp_config(client_id: str, client_secret: str, tenant: str = "common", **kwargs) -> IdPConfig:
    """Create Microsoft Azure AD provider configuration."""
    return IdPConfig(
        provider_id="microsoft",
        provider_name="Microsoft",
        provider_type="oidc",
        discovery_url=f"https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid_configuration",
        client_id=client_id,
        client_secret=client_secret,
        scope=["openid", "email", "profile"],
        **kwargs
    )


def create_okta_idp_config(client_id: str, client_secret: str, okta_domain: str, **kwargs) -> IdPConfig:
    """Create Okta OIDC provider configuration."""
    return IdPConfig(
        provider_id="okta",
        provider_name="Okta",
        provider_type="oidc",
        discovery_url=f"https://{okta_domain}/.well-known/openid_configuration",
        client_id=client_id,
        client_secret=client_secret,
        scope=["openid", "email", "profile"],
        **kwargs
    )
