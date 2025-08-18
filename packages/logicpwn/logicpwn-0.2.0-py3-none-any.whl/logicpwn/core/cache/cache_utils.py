"""
Cache utilities for LogicPwn.
"""
import functools
from typing import Callable, Optional, Dict
from .cache_manager import CacheManager
from .response_cache import ResponseCache
from .session_cache import SessionCache

# Global cache instances (for stats/clearing)
response_cache = ResponseCache()
session_cache = SessionCache()
config_cache = CacheManager(max_size=100, default_ttl=600)

def cached(ttl: int = 300, key_func: Optional[Callable] = None):
    def decorator(func: Callable) -> Callable:
        cache_manager = CacheManager(default_ttl=ttl)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache_manager._generate_key(*args, **kwargs)
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

def get_cache_stats() -> Dict[str, Dict]:
    return {
        'response_cache': response_cache.cache_manager.get_stats(),
        'session_cache': session_cache.cache_manager.get_stats(),
        'config_cache': config_cache.get_stats()
    }

def clear_all_caches() -> None:
    response_cache.cache_manager.clear()
    session_cache.cache_manager.clear()
    config_cache.clear() 