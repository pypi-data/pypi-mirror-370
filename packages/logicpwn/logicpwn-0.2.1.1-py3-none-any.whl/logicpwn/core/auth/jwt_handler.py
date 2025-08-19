"""
JWT Token Management for LogicPwn.

Provides comprehensive JWT (JSON Web Token) handling including:
- JWT parsing and validation
- Signature verification (HS256, RS256, ES256)
- Claims extraction and validation
- Token lifecycle management
- JWK (JSON Web Key) support
- Token refresh mechanisms

Features:
- Multiple signature algorithms
- Automatic token refresh
- Claims validation (exp, nbf, iat, iss, aud)
- JWK Set (JWKS) integration
- Custom claim validation
- Token introspection
"""
import base64
import json
import time
import hmac
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timezone
import secrets

import requests
from loguru import logger
from pydantic import BaseModel, Field, field_validator
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.exceptions import InvalidSignature

from logicpwn.exceptions import AuthenticationError, ValidationError, NetworkError
from logicpwn.core.performance import monitor_performance


@dataclass
class JWTClaims:
    """JWT claims with validation."""
    # Standard claims
    iss: Optional[str] = None  # Issuer
    sub: Optional[str] = None  # Subject
    aud: Optional[Union[str, List[str]]] = None  # Audience
    exp: Optional[int] = None  # Expiration time
    nbf: Optional[int] = None  # Not before
    iat: Optional[int] = None  # Issued at
    jti: Optional[str] = None  # JWT ID
    
    # Custom claims
    custom_claims: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.exp:
            return False
        return time.time() >= self.exp
    
    @property
    def is_not_yet_valid(self) -> bool:
        """Check if token is not yet valid."""
        if not self.nbf:
            return False
        return time.time() < self.nbf
    
    @property
    def is_valid(self) -> bool:
        """Check if token is currently valid."""
        return not self.is_expired and not self.is_not_yet_valid
    
    def validate_audience(self, expected_audience: Union[str, List[str]]) -> bool:
        """Validate audience claim."""
        if not self.aud:
            return not expected_audience
        
        if isinstance(expected_audience, str):
            expected_audience = [expected_audience]
        
        if isinstance(self.aud, str):
            return self.aud in expected_audience
        
        return any(aud in expected_audience for aud in self.aud)
    
    def validate_issuer(self, expected_issuer: str) -> bool:
        """Validate issuer claim."""
        return self.iss == expected_issuer


@dataclass
class JWTHeader:
    """JWT header information."""
    alg: str
    typ: str = "JWT"
    kid: Optional[str] = None  # Key ID
    cty: Optional[str] = None  # Content type
    crit: Optional[List[str]] = None  # Critical headers
    
    @classmethod
    def from_dict(cls, header_dict: Dict[str, Any]) -> 'JWTHeader':
        """Create header from dictionary."""
        return cls(
            alg=header_dict.get('alg', 'none'),
            typ=header_dict.get('typ', 'JWT'),
            kid=header_dict.get('kid'),
            cty=header_dict.get('cty'),
            crit=header_dict.get('crit')
        )


@dataclass
class JWK:
    """JSON Web Key."""
    kty: str  # Key type
    use: Optional[str] = None  # Public key use
    alg: Optional[str] = None  # Algorithm
    kid: Optional[str] = None  # Key ID
    
    # RSA keys
    n: Optional[str] = None  # Modulus
    e: Optional[str] = None  # Exponent
    
    # EC keys
    crv: Optional[str] = None  # Curve
    x: Optional[str] = None  # X coordinate
    y: Optional[str] = None  # Y coordinate
    
    # Symmetric keys
    k: Optional[str] = None  # Key value
    
    @classmethod
    def from_dict(cls, jwk_dict: Dict[str, Any]) -> 'JWK':
        """Create JWK from dictionary."""
        return cls(**{k: v for k, v in jwk_dict.items() if hasattr(cls, k)})
    
    def to_public_key(self):
        """Convert JWK to cryptography public key."""
        if self.kty == 'RSA':
            if not self.n or not self.e:
                raise ValidationError("RSA key missing n or e parameter")
            
            # Decode base64url encoded values
            n_bytes = base64.urlsafe_b64decode(self.n + '==')
            e_bytes = base64.urlsafe_b64decode(self.e + '==')
            
            n_int = int.from_bytes(n_bytes, 'big')
            e_int = int.from_bytes(e_bytes, 'big')
            
            public_numbers = rsa.RSAPublicNumbers(e_int, n_int)
            return public_numbers.public_key()
            
        elif self.kty == 'EC':
            if not self.crv or not self.x or not self.y:
                raise ValidationError("EC key missing crv, x, or y parameter")
            
            # Decode coordinates
            x_bytes = base64.urlsafe_b64decode(self.x + '==')
            y_bytes = base64.urlsafe_b64decode(self.y + '==')
            
            x_int = int.from_bytes(x_bytes, 'big')
            y_int = int.from_bytes(y_bytes, 'big')
            
            # Select curve
            if self.crv == 'P-256':
                curve = ec.SECP256R1()
            elif self.crv == 'P-384':
                curve = ec.SECP384R1()
            elif self.crv == 'P-521':
                curve = ec.SECP521R1()
            else:
                raise ValidationError(f"Unsupported curve: {self.crv}")
            
            public_numbers = ec.EllipticCurvePublicNumbers(x_int, y_int, curve)
            return public_numbers.public_key()
        
        else:
            raise ValidationError(f"Unsupported key type: {self.kty}")


class JWTConfig(BaseModel):
    """JWT configuration."""
    
    # Verification settings
    verify_signature: bool = Field(default=True, description="Verify JWT signature")
    verify_exp: bool = Field(default=True, description="Verify expiration time")
    verify_nbf: bool = Field(default=True, description="Verify not before time")
    verify_iat: bool = Field(default=True, description="Verify issued at time")
    verify_aud: bool = Field(default=True, description="Verify audience")
    verify_iss: bool = Field(default=True, description="Verify issuer")
    
    # Expected values
    expected_audience: Optional[Union[str, List[str]]] = Field(default=None, description="Expected audience")
    expected_issuer: Optional[str] = Field(default=None, description="Expected issuer")
    
    # Key management
    secret_key: Optional[str] = Field(default=None, description="Secret key for HMAC algorithms")
    public_key: Optional[str] = Field(default=None, description="Public key for RSA/EC algorithms")
    jwks_url: Optional[str] = Field(default=None, description="JWK Set URL for key discovery")
    jwks_cache_ttl: int = Field(default=300, description="JWKS cache TTL in seconds")
    
    # Algorithm settings
    algorithms: List[str] = Field(default=['HS256', 'RS256'], description="Allowed algorithms")
    
    # Leeway for time-based claims (in seconds)
    leeway: int = Field(default=0, ge=0, le=300, description="Clock skew leeway in seconds")
    
    # Token refresh
    refresh_threshold: int = Field(default=300, description="Refresh token before expiry (seconds)")
    refresh_url: Optional[str] = Field(default=None, description="Token refresh endpoint")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token")
    
    # Custom claim validators
    custom_validators: Dict[str, Callable] = Field(default_factory=dict, description="Custom claim validators")
    
    model_config = {"arbitrary_types_allowed": True}


class JWTHandler:
    """
    JWT token handler with comprehensive validation and management.
    
    Features:
    - JWT parsing and validation
    - Multiple signature algorithms (HS256, RS256, ES256)
    - JWK Set integration
    - Automatic token refresh
    - Custom claim validation
    - Token introspection
    """
    
    def __init__(self, config: JWTConfig, session: Optional[requests.Session] = None):
        self.config = config
        self.session = session or requests.Session()
        self._jwks_cache: Dict[str, Any] = {}
        self._jwks_cache_time: float = 0
        
    def _base64url_decode(self, data: str) -> bytes:
        """Decode base64url encoded data."""
        # Add padding if needed
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        
        return base64.urlsafe_b64decode(data)
    
    def _base64url_encode(self, data: bytes) -> str:
        """Encode data as base64url."""
        return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')
    
    @monitor_performance("jwt_token_parsing")
    def parse_token(self, token: str) -> tuple[JWTHeader, JWTClaims, str]:
        """
        Parse JWT token into header, claims, and signature.
        
        Args:
            token: JWT token string
            
        Returns:
            Tuple of (header, claims, signature)
        """
        try:
            parts = token.split('.')
            if len(parts) != 3:
                raise ValidationError("Invalid JWT format - expected 3 parts")
            
            header_data = json.loads(self._base64url_decode(parts[0]))
            payload_data = json.loads(self._base64url_decode(parts[1]))
            signature = parts[2]
            
            # Parse header
            header = JWTHeader.from_dict(header_data)
            
            # Parse claims
            claims = JWTClaims(
                iss=payload_data.get('iss'),
                sub=payload_data.get('sub'),
                aud=payload_data.get('aud'),
                exp=payload_data.get('exp'),
                nbf=payload_data.get('nbf'),
                iat=payload_data.get('iat'),
                jti=payload_data.get('jti'),
                custom_claims={k: v for k, v in payload_data.items() 
                             if k not in ['iss', 'sub', 'aud', 'exp', 'nbf', 'iat', 'jti']}
            )
            
            return header, claims, signature
            
        except (ValueError, json.JSONDecodeError) as e:
            raise ValidationError(f"Invalid JWT token: {e}")
    
    @monitor_performance("jwt_signature_verification")
    def verify_signature(self, token: str, header: JWTHeader, key: Optional[Any] = None) -> bool:
        """
        Verify JWT signature.
        
        Args:
            token: JWT token string
            header: JWT header
            key: Verification key (optional, will be resolved from config)
            
        Returns:
            True if signature is valid
        """
        if not self.config.verify_signature:
            return True
        
        if header.alg == 'none':
            return True
        
        if header.alg not in self.config.algorithms:
            raise ValidationError(f"Algorithm {header.alg} not allowed")
        
        parts = token.split('.')
        if len(parts) != 3:
            raise ValidationError("Invalid JWT format")
        
        message = f"{parts[0]}.{parts[1]}".encode('utf-8')
        signature = self._base64url_decode(parts[2])
        
        # Get verification key
        if not key:
            key = self._get_verification_key(header)
        
        try:
            if header.alg.startswith('HS'):
                # HMAC algorithms
                if not isinstance(key, (str, bytes)):
                    raise ValidationError("HMAC algorithms require string or bytes key")
                
                if isinstance(key, str):
                    key = key.encode('utf-8')
                
                if header.alg == 'HS256':
                    expected_signature = hmac.new(key, message, hashlib.sha256).digest()
                elif header.alg == 'HS384':
                    expected_signature = hmac.new(key, message, hashlib.sha384).digest()
                elif header.alg == 'HS512':
                    expected_signature = hmac.new(key, message, hashlib.sha512).digest()
                else:
                    raise ValidationError(f"Unsupported HMAC algorithm: {header.alg}")
                
                return hmac.compare_digest(signature, expected_signature)
                
            elif header.alg.startswith('RS'):
                # RSA algorithms
                if header.alg == 'RS256':
                    hash_alg = hashes.SHA256()
                elif header.alg == 'RS384':
                    hash_alg = hashes.SHA384()
                elif header.alg == 'RS512':
                    hash_alg = hashes.SHA512()
                else:
                    raise ValidationError(f"Unsupported RSA algorithm: {header.alg}")
                
                key.verify(signature, message, PKCS1v15(), hash_alg)
                return True
                
            elif header.alg.startswith('ES'):
                # ECDSA algorithms
                if header.alg == 'ES256':
                    hash_alg = hashes.SHA256()
                elif header.alg == 'ES384':
                    hash_alg = hashes.SHA384()
                elif header.alg == 'ES512':
                    hash_alg = hashes.SHA512()
                else:
                    raise ValidationError(f"Unsupported ECDSA algorithm: {header.alg}")
                
                key.verify(signature, message, ec.ECDSA(hash_alg))
                return True
            
            else:
                raise ValidationError(f"Unsupported algorithm: {header.alg}")
                
        except InvalidSignature:
            return False
        except Exception as e:
            logger.warning(f"Signature verification error: {e}")
            return False
    
    def _get_verification_key(self, header: JWTHeader) -> Any:
        """Get verification key for token."""
        if header.alg.startswith('HS'):
            if not self.config.secret_key:
                raise ValidationError("No secret key configured for HMAC verification")
            return self.config.secret_key
        
        elif header.alg.startswith(('RS', 'ES')):
            # Try to get key from JWKS first
            if self.config.jwks_url and header.kid:
                jwk = self._get_jwk_by_kid(header.kid)
                if jwk:
                    return jwk.to_public_key()
            
            # Fallback to configured public key
            if self.config.public_key:
                return serialization.load_pem_public_key(self.config.public_key.encode())
            
            raise ValidationError("No verification key available for RSA/EC algorithms")
        
        else:
            raise ValidationError(f"Unsupported algorithm: {header.alg}")
    
    @monitor_performance("jwks_fetch")
    def _fetch_jwks(self) -> Dict[str, Any]:
        """Fetch JWK Set from configured URL."""
        if not self.config.jwks_url:
            return {}
        
        # Check cache
        now = time.time()
        if (self._jwks_cache and 
            now - self._jwks_cache_time < self.config.jwks_cache_ttl):
            return self._jwks_cache
        
        try:
            response = self.session.get(self.config.jwks_url, timeout=30)
            response.raise_for_status()
            
            jwks = response.json()
            self._jwks_cache = jwks
            self._jwks_cache_time = now
            
            logger.debug(f"Fetched JWKS from {self.config.jwks_url}")
            return jwks
            
        except (requests.exceptions.RequestException, ValueError) as e:
            logger.warning(f"Failed to fetch JWKS: {e}")
            return self._jwks_cache  # Return cached version if available
    
    def _get_jwk_by_kid(self, kid: str) -> Optional[JWK]:
        """Get JWK by key ID."""
        jwks = self._fetch_jwks()
        
        for key_data in jwks.get('keys', []):
            if key_data.get('kid') == kid:
                return JWK.from_dict(key_data)
        
        return None
    
    @monitor_performance("jwt_token_validation")
    def validate_token(self, token: str) -> JWTClaims:
        """
        Validate JWT token and return claims.
        
        Args:
            token: JWT token string
            
        Returns:
            JWTClaims if token is valid
            
        Raises:
            AuthenticationError: If token is invalid
            ValidationError: If token format is invalid
        """
        # Parse token
        header, claims, signature = self.parse_token(token)
        
        # Verify signature
        if not self.verify_signature(token, header):
            raise AuthenticationError("Invalid JWT signature")
        
        # Validate time-based claims
        now = time.time()
        
        if self.config.verify_exp and claims.exp:
            if now >= claims.exp + self.config.leeway:
                raise AuthenticationError("JWT token has expired")
        
        if self.config.verify_nbf and claims.nbf:
            if now < claims.nbf - self.config.leeway:
                raise AuthenticationError("JWT token is not yet valid")
        
        if self.config.verify_iat and claims.iat:
            if now < claims.iat - self.config.leeway:
                raise AuthenticationError("JWT token issued in the future")
        
        # Validate audience
        if self.config.verify_aud and self.config.expected_audience:
            if not claims.validate_audience(self.config.expected_audience):
                raise AuthenticationError("Invalid JWT audience")
        
        # Validate issuer
        if self.config.verify_iss and self.config.expected_issuer:
            if not claims.validate_issuer(self.config.expected_issuer):
                raise AuthenticationError("Invalid JWT issuer")
        
        # Run custom validators
        for claim_name, validator in self.config.custom_validators.items():
            claim_value = claims.custom_claims.get(claim_name)
            if not validator(claim_value):
                raise AuthenticationError(f"Custom validation failed for claim: {claim_name}")
        
        logger.debug(f"Successfully validated JWT token for subject: {claims.sub}")
        return claims
    
    @monitor_performance("jwt_token_refresh")
    def refresh_token(self) -> Optional[str]:
        """
        Refresh JWT token using refresh token.
        
        Returns:
            New JWT token if refresh successful
        """
        if not self.config.refresh_url or not self.config.refresh_token:
            return None
        
        try:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.config.refresh_token
            }
            
            response = self.session.post(
                self.config.refresh_url,
                data=data,
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            new_token = token_data.get('access_token')
            
            # Update refresh token if provided
            if 'refresh_token' in token_data:
                self.config.refresh_token = token_data['refresh_token']
            
            logger.info("Successfully refreshed JWT token")
            return new_token
            
        except (requests.exceptions.RequestException, ValueError) as e:
            logger.warning(f"Token refresh failed: {e}")
            return None
    
    def should_refresh_token(self, token: str) -> bool:
        """
        Check if token should be refreshed.
        
        Args:
            token: JWT token string
            
        Returns:
            True if token should be refreshed
        """
        try:
            _, claims, _ = self.parse_token(token)
            
            if not claims.exp:
                return False
            
            time_until_expiry = claims.exp - time.time()
            return time_until_expiry <= self.config.refresh_threshold
            
        except Exception:
            return True  # Refresh if we can't parse the token
    
    def create_token(self, claims: Dict[str, Any], algorithm: str = 'HS256',
                    key: Optional[Any] = None, expires_in: Optional[int] = None) -> str:
        """
        Create JWT token with given claims.
        
        Args:
            claims: Token claims
            algorithm: Signature algorithm
            key: Signing key
            expires_in: Expiration time in seconds
            
        Returns:
            JWT token string
        """
        now = int(time.time())
        
        # Add standard claims
        token_claims = {
            'iat': now,
            **claims
        }
        
        if expires_in:
            token_claims['exp'] = now + expires_in
        
        # Create header
        header = {
            'typ': 'JWT',
            'alg': algorithm
        }
        
        # Encode header and payload
        header_encoded = self._base64url_encode(json.dumps(header).encode())
        payload_encoded = self._base64url_encode(json.dumps(token_claims).encode())
        
        message = f"{header_encoded}.{payload_encoded}"
        
        # Sign token
        if algorithm == 'none':
            signature = ''
        else:
            if not key:
                if algorithm.startswith('HS'):
                    key = self.config.secret_key
                else:
                    raise ValidationError("Signing key required")
            
            if algorithm == 'HS256':
                signature_bytes = hmac.new(
                    key.encode() if isinstance(key, str) else key,
                    message.encode(),
                    hashlib.sha256
                ).digest()
            else:
                raise ValidationError(f"Unsupported signing algorithm: {algorithm}")
            
            signature = self._base64url_encode(signature_bytes)
        
        return f"{message}.{signature}"


def create_jwt_config_from_well_known(issuer_url: str, audience: Optional[str] = None,
                                    **kwargs) -> JWTConfig:
    """
    Create JWT configuration from OpenID Connect discovery document.
    
    Args:
        issuer_url: OIDC issuer URL
        audience: Expected audience
        **kwargs: Additional JWTConfig parameters
        
    Returns:
        JWTConfig with discovered endpoints
    """
    well_known_url = f"{issuer_url.rstrip('/')}/.well-known/openid_configuration"
    
    try:
        response = requests.get(well_known_url, timeout=30)
        response.raise_for_status()
        discovery = response.json()
        
        config_data = {
            'expected_issuer': discovery['issuer'],
            'jwks_url': discovery.get('jwks_uri'),
            'expected_audience': audience,
            **kwargs
        }
        
        return JWTConfig(**config_data)
        
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        raise ValidationError(f"Failed to discover JWT configuration: {e}") from e
