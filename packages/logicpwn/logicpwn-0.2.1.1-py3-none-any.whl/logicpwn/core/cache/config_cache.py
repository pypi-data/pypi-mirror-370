"""
Configuration cache for LogicPwn.
"""
from .cache_manager import CacheManager

config_cache = CacheManager(max_size=100, default_ttl=600) 