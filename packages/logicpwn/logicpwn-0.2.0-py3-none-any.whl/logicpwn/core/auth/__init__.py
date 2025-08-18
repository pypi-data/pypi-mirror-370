from .auth_session import (
    authenticate_session, 
    validate_session, 
    logout_session,
    authenticate_session_advanced,
    create_csrf_config
)
from .auth_models import AuthConfig, SessionState, CSRFConfig
from .auth_utils import _sanitize_credentials
from .auth_constants import HTTP_METHODS, DEFAULT_SESSION_TIMEOUT, MAX_RESPONSE_TEXT_LENGTH
from .http_client import LogicPwnHTTPClient, create_authenticated_client

# Enhanced authentication modules
from .oauth_handler import (
    OAuthHandler, OAuthConfig, OAuthToken, PKCEChallenge,
    create_oauth_config_from_well_known,
    create_google_oauth_config, create_microsoft_oauth_config, create_github_oauth_config
)
from .saml_handler import (
    SAMLHandler, SAMLConfig, SAMLAssertion, IdPMetadata,
    load_idp_metadata_from_url, create_saml_config_from_metadata,
    create_okta_saml_config, create_azure_saml_config
)
from .jwt_handler import (
    JWTHandler, JWTConfig, JWTClaims, JWTHeader, JWK,
    create_jwt_config_from_well_known
)
from .mfa_handler import (
    MFAManager, MFAConfig, MFAChallenge, TOTPHandler, SMSHandler, EmailHandler, BackupCodeHandler,
    TOTPSecret, create_totp_qr_code, validate_totp_code
)
from .idp_integration import (
    IdPManager, IdPConfig, AuthenticationSession, UserProfile, AttributeMapping,
    OIDCProvider, SAMLIdPProvider,
    create_google_idp_config, create_microsoft_idp_config, create_okta_idp_config
)
from .enhanced_auth import (
    EnhancedAuthenticator, EnhancedAuthConfig, RedirectInfo, AuthFlow,
    create_enhanced_config, create_oauth_enhanced_config, create_saml_enhanced_config, create_mfa_enhanced_config
)

__all__ = [
    # Core authentication functions
    "authenticate_session",
    "validate_session", 
    "logout_session",
    
    # Advanced authentication with HTTP client
    "authenticate_session_advanced",
    "create_authenticated_client",
    "create_csrf_config",
    
    # Models and configurations
    "AuthConfig",
    "SessionState", 
    "CSRFConfig",
    "LogicPwnHTTPClient",
    
    # OAuth 2.0 Support
    "OAuthHandler",
    "OAuthConfig", 
    "OAuthToken",
    "PKCEChallenge",
    "create_oauth_config_from_well_known",
    "create_google_oauth_config",
    "create_microsoft_oauth_config",
    "create_github_oauth_config",
    
    # SAML SSO Support
    "SAMLHandler",
    "SAMLConfig",
    "SAMLAssertion",
    "IdPMetadata",
    "load_idp_metadata_from_url",
    "create_saml_config_from_metadata",
    "create_okta_saml_config",
    "create_azure_saml_config",
    
    # JWT Token Management
    "JWTHandler",
    "JWTConfig",
    "JWTClaims",
    "JWTHeader",
    "JWK",
    "create_jwt_config_from_well_known",
    
    # Multi-Factor Authentication
    "MFAManager",
    "MFAConfig",
    "MFAChallenge",
    "TOTPHandler",
    "SMSHandler", 
    "EmailHandler",
    "BackupCodeHandler",
    "TOTPSecret",
    "create_totp_qr_code",
    "validate_totp_code",
    
    # Identity Provider Integration
    "IdPManager",
    "IdPConfig",
    "AuthenticationSession",
    "UserProfile",
    "AttributeMapping",
    "OIDCProvider",
    "SAMLIdPProvider",
    "create_google_idp_config",
    "create_microsoft_idp_config",
    "create_okta_idp_config",
    
    # Enhanced Authentication
    "EnhancedAuthenticator",
    "EnhancedAuthConfig",
    "RedirectInfo",
    "AuthFlow",
    "create_enhanced_config",
    "create_oauth_enhanced_config",
    "create_saml_enhanced_config",
    "create_mfa_enhanced_config",
    
    # Utilities and constants
    "_sanitize_credentials",
    "HTTP_METHODS",
    "DEFAULT_SESSION_TIMEOUT",
    "MAX_RESPONSE_TEXT_LENGTH"
] 