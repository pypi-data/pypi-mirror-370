"""
OAuth 2.0 Authentication Handler for LogicPwn.

Supports OAuth 2.0 authorization flows including:
- Authorization Code Flow
- Implicit Flow  
- Client Credentials Flow
- PKCE (Proof Key for Code Exchange)
- OpenID Connect (OIDC)

Features:
- Automatic authorization server discovery
- Token lifecycle management
- Refresh token handling
- Scope management
- State parameter validation
- PKCE challenge generation
"""
import base64
import hashlib
import json
import secrets
import time
import urllib.parse
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
from urllib.parse import urlencode, parse_qs, urlparse

import requests
from loguru import logger
from pydantic import BaseModel, Field, field_validator

from logicpwn.exceptions import AuthenticationError, ValidationError, NetworkError
from logicpwn.core.performance import monitor_performance
from .auth_models import AuthConfig


@dataclass
class OAuthToken:
    """OAuth token with metadata."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    id_token: Optional[str] = None  # For OpenID Connect
    expires_at: Optional[float] = field(default=None, init=False)
    
    def __post_init__(self):
        if self.expires_in:
            self.expires_at = time.time() + self.expires_in
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_at:
            return False
        return time.time() >= self.expires_at
    
    @property
    def expires_in_seconds(self) -> Optional[int]:
        """Get seconds until expiration."""
        if not self.expires_at:
            return None
        remaining = self.expires_at - time.time()
        return max(0, int(remaining))


@dataclass
class PKCEChallenge:
    """PKCE code challenge and verifier."""
    code_verifier: str
    code_challenge: str
    code_challenge_method: str = "S256"
    
    @classmethod
    def generate(cls) -> 'PKCEChallenge':
        """Generate PKCE challenge pair."""
        # Generate code verifier (43-128 characters)
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        # Generate code challenge
        challenge_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')
        
        return cls(
            code_verifier=code_verifier,
            code_challenge=code_challenge,
            code_challenge_method="S256"
        )


class OAuthConfig(BaseModel):
    """OAuth 2.0 configuration."""
    client_id: str = Field(..., description="OAuth client ID")
    client_secret: Optional[str] = Field(default=None, description="OAuth client secret")
    authorization_url: str = Field(..., description="Authorization endpoint URL")
    token_url: str = Field(..., description="Token endpoint URL")
    redirect_uri: str = Field(default="http://localhost:8080/callback", description="Redirect URI")
    scope: List[str] = Field(default_factory=list, description="OAuth scopes")
    
    # Flow configuration
    grant_type: str = Field(default="authorization_code", description="OAuth grant type")
    use_pkce: bool = Field(default=True, description="Use PKCE for security")
    response_type: str = Field(default="code", description="OAuth response type")
    
    # Optional endpoints
    userinfo_url: Optional[str] = Field(default=None, description="UserInfo endpoint (OIDC)")
    jwks_url: Optional[str] = Field(default=None, description="JWKS endpoint for token validation")
    issuer: Optional[str] = Field(default=None, description="OIDC issuer")
    
    # Advanced options
    state_generator: Optional[Callable[[], str]] = Field(default=None, description="Custom state generator")
    additional_params: Dict[str, str] = Field(default_factory=dict, description="Additional OAuth parameters")
    token_endpoint_auth_method: str = Field(default="client_secret_basic", description="Token endpoint auth method")
    
    model_config = {"arbitrary_types_allowed": True}
    
    @field_validator('grant_type')
    @classmethod
    def validate_grant_type(cls, v: str) -> str:
        valid_types = ["authorization_code", "implicit", "client_credentials", "refresh_token"]
        if v not in valid_types:
            raise ValueError(f"Invalid grant_type. Must be one of: {valid_types}")
        return v


class OAuthHandler:
    """
    OAuth 2.0 authentication handler with comprehensive flow support.
    
    Features:
    - Multiple OAuth flows (authorization code, implicit, client credentials)
    - PKCE support for enhanced security
    - OpenID Connect compatibility
    - Automatic token refresh
    - State parameter validation
    - Scope management
    """
    
    def __init__(self, config: OAuthConfig, session: Optional[requests.Session] = None):
        self.config = config
        self.session = session or requests.Session()
        self.token: Optional[OAuthToken] = None
        self._pkce_challenge: Optional[PKCEChallenge] = None
        self._state: Optional[str] = None
        
    def generate_state(self) -> str:
        """Generate secure state parameter."""
        if self.config.state_generator:
            return self.config.state_generator()
        return secrets.token_urlsafe(32)
    
    @monitor_performance("oauth_authorization_url_generation")
    def get_authorization_url(self) -> tuple[str, str]:
        """
        Generate authorization URL for authorization code flow.
        
        Returns:
            Tuple of (authorization_url, state)
        """
        if self.config.grant_type not in ["authorization_code", "implicit"]:
            raise ValidationError("Authorization URL only available for authorization_code and implicit flows")
        
        # Generate state parameter
        self._state = self.generate_state()
        
        # Generate PKCE challenge if enabled
        if self.config.use_pkce and self.config.grant_type == "authorization_code":
            self._pkce_challenge = PKCEChallenge.generate()
        
        # Build authorization parameters
        params = {
            'response_type': self.config.response_type,
            'client_id': self.config.client_id,
            'redirect_uri': self.config.redirect_uri,
            'state': self._state,
        }
        
        # Add scope if specified
        if self.config.scope:
            params['scope'] = ' '.join(self.config.scope)
        
        # Add PKCE parameters
        if self._pkce_challenge:
            params['code_challenge'] = self._pkce_challenge.code_challenge
            params['code_challenge_method'] = self._pkce_challenge.code_challenge_method
        
        # Add additional parameters
        params.update(self.config.additional_params)
        
        # Build full URL
        auth_url = f"{self.config.authorization_url}?{urlencode(params)}"
        
        logger.debug(f"Generated OAuth authorization URL: {auth_url}")
        return auth_url, self._state
    
    @monitor_performance("oauth_token_exchange")
    def exchange_code_for_token(self, authorization_code: str, state: str) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            authorization_code: Authorization code from callback
            state: State parameter for validation
            
        Returns:
            OAuthToken with access token and metadata
        """
        # Validate state parameter
        if state != self._state:
            raise AuthenticationError(f"Invalid state parameter. Expected: {self._state}, Got: {state}")
        
        # Prepare token request
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.config.redirect_uri,
        }
        
        # Add PKCE verifier if used
        if self._pkce_challenge:
            data['code_verifier'] = self._pkce_challenge.code_verifier
        
        # Add client credentials based on auth method
        if self.config.token_endpoint_auth_method == "client_secret_basic":
            auth = (self.config.client_id, self.config.client_secret or "")
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        elif self.config.token_endpoint_auth_method == "client_secret_post":
            auth = None
            data['client_id'] = self.config.client_id
            if self.config.client_secret:
                data['client_secret'] = self.config.client_secret
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        else:
            raise ValidationError(f"Unsupported token endpoint auth method: {self.config.token_endpoint_auth_method}")
        
        try:
            response = self.session.post(
                self.config.token_url,
                data=data,
                headers=headers,
                auth=auth,
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.token = OAuthToken(**token_data)
            
            logger.info(f"Successfully exchanged authorization code for access token")
            return self.token
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Token exchange failed: {e}") from e
        except (KeyError, ValueError) as e:
            raise AuthenticationError(f"Invalid token response: {e}") from e
    
    @monitor_performance("oauth_client_credentials")
    def client_credentials_flow(self) -> OAuthToken:
        """
        Perform client credentials flow.
        
        Returns:
            OAuthToken with access token
        """
        if not self.config.client_secret:
            raise ValidationError("Client secret required for client credentials flow")
        
        data = {
            'grant_type': 'client_credentials',
        }
        
        # Add scope if specified
        if self.config.scope:
            data['scope'] = ' '.join(self.config.scope)
        
        auth = (self.config.client_id, self.config.client_secret)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        try:
            response = self.session.post(
                self.config.token_url,
                data=data,
                headers=headers,
                auth=auth,
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.token = OAuthToken(**token_data)
            
            logger.info("Successfully completed client credentials flow")
            return self.token
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Client credentials flow failed: {e}") from e
        except (KeyError, ValueError) as e:
            raise AuthenticationError(f"Invalid token response: {e}") from e
    
    @monitor_performance("oauth_token_refresh")
    def refresh_access_token(self) -> OAuthToken:
        """
        Refresh access token using refresh token.
        
        Returns:
            New OAuthToken with refreshed access token
        """
        if not self.token or not self.token.refresh_token:
            raise AuthenticationError("No refresh token available")
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.token.refresh_token,
        }
        
        # Add scope if specified
        if self.config.scope:
            data['scope'] = ' '.join(self.config.scope)
        
        auth = (self.config.client_id, self.config.client_secret or "")
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        try:
            response = self.session.post(
                self.config.token_url,
                data=data,
                headers=headers,
                auth=auth,
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            
            # Preserve refresh token if not returned
            if 'refresh_token' not in token_data and self.token.refresh_token:
                token_data['refresh_token'] = self.token.refresh_token
            
            self.token = OAuthToken(**token_data)
            
            logger.info("Successfully refreshed access token")
            return self.token
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Token refresh failed: {e}") from e
        except (KeyError, ValueError) as e:
            raise AuthenticationError(f"Invalid token response: {e}") from e
    
    def get_authorization_header(self) -> Dict[str, str]:
        """
        Get authorization header for authenticated requests.
        
        Returns:
            Dictionary with Authorization header
        """
        if not self.token:
            raise AuthenticationError("No access token available")
        
        # Auto-refresh if token is expired
        if self.token.is_expired and self.token.refresh_token:
            self.refresh_access_token()
        
        return {
            'Authorization': f'{self.token.token_type} {self.token.access_token}'
        }
    
    @monitor_performance("oauth_userinfo_fetch")
    def get_user_info(self) -> Dict[str, Any]:
        """
        Fetch user information from UserInfo endpoint.
        
        Returns:
            User information dictionary
        """
        if not self.config.userinfo_url:
            raise ValidationError("UserInfo URL not configured")
        
        headers = self.get_authorization_header()
        
        try:
            response = self.session.get(
                self.config.userinfo_url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"UserInfo request failed: {e}") from e
        except ValueError as e:
            raise AuthenticationError(f"Invalid UserInfo response: {e}") from e
    
    def revoke_token(self, token: Optional[str] = None) -> bool:
        """
        Revoke access or refresh token.
        
        Args:
            token: Token to revoke (defaults to current access token)
            
        Returns:
            True if revocation successful
        """
        if not token and self.token:
            token = self.token.access_token
        
        if not token:
            return False
        
        # Try common revocation endpoint patterns
        revoke_urls = [
            self.config.token_url.replace('/token', '/revoke'),
            self.config.authorization_url.replace('/authorize', '/revoke'),
        ]
        
        for revoke_url in revoke_urls:
            try:
                data = {'token': token}
                auth = (self.config.client_id, self.config.client_secret or "")
                
                response = self.session.post(
                    revoke_url,
                    data=data,
                    auth=auth,
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully revoked token at {revoke_url}")
                    self.token = None
                    return True
                    
            except requests.exceptions.RequestException:
                continue
        
        logger.warning("Token revocation failed - no working revocation endpoint found")
        return False


def create_oauth_config_from_well_known(issuer_url: str, client_id: str, 
                                       client_secret: Optional[str] = None,
                                       **kwargs) -> OAuthConfig:
    """
    Create OAuth configuration from OpenID Connect discovery document.
    
    Args:
        issuer_url: OIDC issuer URL
        client_id: OAuth client ID
        client_secret: OAuth client secret
        **kwargs: Additional OAuthConfig parameters
        
    Returns:
        OAuthConfig with discovered endpoints
    """
    well_known_url = f"{issuer_url.rstrip('/')}/.well-known/openid_configuration"
    
    try:
        response = requests.get(well_known_url, timeout=30)
        response.raise_for_status()
        discovery = response.json()
        
        config_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'authorization_url': discovery['authorization_endpoint'],
            'token_url': discovery['token_endpoint'],
            'userinfo_url': discovery.get('userinfo_endpoint'),
            'jwks_url': discovery.get('jwks_uri'),
            'issuer': discovery['issuer'],
            **kwargs
        }
        
        return OAuthConfig(**config_data)
        
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        raise ValidationError(f"Failed to discover OAuth endpoints: {e}") from e


# Convenience functions for common OAuth providers

def create_google_oauth_config(client_id: str, client_secret: str, **kwargs) -> OAuthConfig:
    """Create OAuth config for Google."""
    return OAuthConfig(
        client_id=client_id,
        client_secret=client_secret,
        authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        userinfo_url="https://openidconnect.googleapis.com/v1/userinfo",
        jwks_url="https://www.googleapis.com/oauth2/v3/certs",
        issuer="https://accounts.google.com",
        scope=["openid", "email", "profile"],
        **kwargs
    )


def create_microsoft_oauth_config(client_id: str, client_secret: str, tenant: str = "common", **kwargs) -> OAuthConfig:
    """Create OAuth config for Microsoft Azure AD."""
    base_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0"
    return OAuthConfig(
        client_id=client_id,
        client_secret=client_secret,
        authorization_url=f"{base_url}/authorize",
        token_url=f"{base_url}/token",
        userinfo_url="https://graph.microsoft.com/v1.0/me",
        jwks_url=f"https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys",
        issuer=f"https://login.microsoftonline.com/{tenant}/v2.0",
        scope=["openid", "email", "profile"],
        **kwargs
    )


def create_github_oauth_config(client_id: str, client_secret: str, **kwargs) -> OAuthConfig:
    """Create OAuth config for GitHub."""
    return OAuthConfig(
        client_id=client_id,
        client_secret=client_secret,
        authorization_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        userinfo_url="https://api.github.com/user",
        scope=["user:email"],
        use_pkce=False,  # GitHub doesn't support PKCE
        **kwargs
    )
