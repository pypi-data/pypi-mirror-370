"""
Session cache for LogicPwn with enhanced session management.

This module provides intelligent session caching that works optimally with
the auth module's stable session ID generation, excluding dynamic tokens
like CSRF tokens from cache keys.
"""
from typing import Any, Optional, Dict, List
from loguru import logger
from .cache_manager import CacheManager


class SessionCache:
    """
    Enhanced session cache that provides intelligent caching for authenticated sessions.
    
    Features:
    - Stable session ID generation (excludes dynamic tokens)
    - Session validation before returning cached sessions
    - Automatic cleanup of expired/invalid sessions
    - Cache statistics and monitoring
    """
    
    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        """
        Initialize session cache.
        
        Args:
            max_size: Maximum number of sessions to cache
            default_ttl: Default time-to-live for cached sessions in seconds
        """
        self.cache_manager = CacheManager(max_size, default_ttl)
        logger.debug(f"Initialized SessionCache with max_size={max_size}, ttl={default_ttl}")

    def get_session(self, session_id: str) -> Optional[Any]:
        """
        Get cached session by ID.
        
        Args:
            session_id: Stable session ID (should exclude dynamic tokens)
            
        Returns:
            Cached session if found and valid, None otherwise
        """
        session = self.cache_manager.get(session_id)
        if session:
            logger.debug(f"Retrieved cached session: {session_id}")
        return session

    def set_session(self, session_id: str, session: Any, ttl: Optional[int] = None) -> None:
        """
        Cache a session with optional TTL override.
        
        Args:
            session_id: Stable session ID (should exclude dynamic tokens)
            session: Session object to cache
            ttl: Optional TTL override in seconds
        """
        metadata = {
            'session_type': type(session).__name__,
            'cookies_count': self._safe_get_cookies_count(session),
            'headers_count': self._safe_get_headers_count(session)
        }
        
        self.cache_manager.set(session_id, session, ttl, metadata)
        logger.debug(f"Cached session: {session_id} with {metadata['cookies_count']} cookies")

    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate and remove a cached session.
        
        Args:
            session_id: Session ID to invalidate
            
        Returns:
            True if session was found and removed, False otherwise
        """
        result = self.cache_manager.invalidate(session_id)
        if result:
            logger.debug(f"Invalidated cached session: {session_id}")
        return result
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions from cache.
        
        Returns:
            Number of sessions removed
        """
        removed_count = self.cache_manager.cleanup_expired()
        if removed_count > 0:
            logger.debug(f"Cleaned up {removed_count} expired sessions")
        return removed_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        stats = self.cache_manager.get_stats()
        stats['cache_type'] = 'session_cache'
        return stats
    
    def list_cached_sessions(self) -> List[Dict[str, Any]]:
        """
        List all cached sessions with metadata.
        
        Returns:
            List of dictionaries containing session info
        """
        sessions = []
        for key, entry in self.cache_manager.cache.items():
            session_info = {
                'session_id': key,
                'timestamp': entry.timestamp,
                'ttl': entry.ttl,
                'access_count': entry.access_count,
                'metadata': entry.metadata,
                'is_expired': entry.is_expired()
            }
            sessions.append(session_info)
        
        return sessions
    
    def clear_all_sessions(self) -> None:
        """Clear all cached sessions."""
        self.cache_manager.clear()
        logger.info("Cleared all cached sessions")
    
    def generate_stable_session_id(self, auth_config) -> str:
        """
        Generate a stable session ID excluding dynamic tokens.
        
        This method creates cache keys that remain consistent across
        requests even when dynamic tokens (like CSRF tokens) change.
        
        Args:
            auth_config: Authentication configuration object
            
        Returns:
            Stable session ID string
        """
        # List of dynamic token field names to exclude from session ID
        dynamic_tokens = {
            # CSRF tokens
            'user_token', 'csrf_token', '_token', 'authenticity_token', 
            'csrfmiddlewaretoken', 'xsrf_token', 'csrf', 'token',
            
            # ASP.NET ViewState
            '__viewstate', '__viewstategenerator', '__eventvalidation', 
            '__eventargument', '__eventtarget',
            
            # Spring Security
            'lt', 'execution', '_eventId', 'submit', 'service',
            
            # SAML
            'samlresponse', 'relaystate', 'samlrequest',
            
            # OAuth/OpenID
            'state', 'nonce', 'code_challenge', 'code_verifier',
            
            # Session tokens
            'session_token', 'request_token', 'form_token',
            
            # Captcha
            'captcha', 'recaptcha', 'captcha_token',
            
            # Nonces and timestamps
            'nonce', 'timestamp', '_t', 'time',
            
            # Other dynamic fields
            'challenge', 'salt', 'random', 'guid', 'uuid'
        }
        
        # Filter out dynamic tokens from credentials
        stable_creds = {
            k.lower(): v for k, v in auth_config.credentials.items() 
            if k.lower() not in dynamic_tokens
        }
        
        # Create stable cache key components
        key_components = {
            'url': auth_config.url,
            'method': auth_config.method.upper(),
            'credentials': stable_creds,
            'verify_ssl': getattr(auth_config, 'verify_ssl', True)
        }
        
        # Generate hash of stable components
        import hashlib
        key_string = str(sorted(key_components.items()))
        session_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        session_id = f"auth_session_{session_hash}"
        logger.debug(f"Generated stable session ID: {session_id} (excluded {len(auth_config.credentials) - len(stable_creds)} dynamic tokens)")
        
        return session_id

    def _safe_get_cookies_count(self, session) -> int:
        """
        Safely get the count of cookies from a session, handling Mock objects during testing.
        
        Args:
            session: Session object (real or Mock)
            
        Returns:
            int: Number of cookies, or 0 if unable to determine
        """
        if not hasattr(session, 'cookies'):
            return 0
            
        try:
            # Handle Mock objects during testing
            from unittest.mock import Mock
            if isinstance(session.cookies, Mock):
                return 0  # Mock object, return safe default
                
            # Try to count cookies safely
            if hasattr(session.cookies, '__iter__'):
                return len(list(session.cookies))
            else:
                return 0
        except (TypeError, AttributeError):
            # If anything fails, return safe default
            return 0

    def _safe_get_headers_count(self, session) -> int:
        """
        Safely get the count of headers from a session, handling Mock objects during testing.
        
        Args:
            session: Session object (real or Mock)
            
        Returns:
            int: Number of headers, or 0 if unable to determine
        """
        if not hasattr(session, 'headers'):
            return 0
            
        try:
            # Handle Mock objects during testing
            from unittest.mock import Mock
            if isinstance(session.headers, Mock):
                return 0  # Mock object, return safe default
                
            # Try to count headers safely
            if hasattr(session.headers, '__len__'):
                return len(session.headers)
            else:
                return 0
        except (TypeError, AttributeError):
            # If anything fails, return safe default
            return 0