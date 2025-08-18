"""
Core cache manager and entry for LogicPwn.
"""
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from collections import OrderedDict
import hashlib
from loguru import logger

@dataclass
class CacheEntry:
    value: Any
    timestamp: float
    ttl: int
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl

    def access(self):
        self.access_count += 1

class CacheManager:
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0
        }

    def _generate_key(self, *args, **kwargs) -> str:
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            entry = self.cache[key]
            if entry.is_expired():
                del self.cache[key]
                self.stats['expirations'] += 1
                self.stats['misses'] += 1
                return None
            self.cache.move_to_end(key)
            entry.access()
            self.stats['hits'] += 1
            return entry.value
        self.stats['misses'] += 1
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        entry = CacheEntry(
            value=value,
            timestamp=time.time(),
            ttl=ttl or self.default_ttl,
            metadata=metadata or {}
        )
        self.cache[key] = entry
        logger.debug(f"Cached entry: {key} (TTL: {entry.ttl}s)")

    def _evict_oldest(self) -> None:
        if self.cache:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.stats['evictions'] += 1
            logger.debug(f"Evicted cache entry: {oldest_key}")

    def invalidate(self, key: str) -> bool:
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Invalidated cache entry: {key}")
            return True
        return False

    def clear(self) -> None:
        self.cache.clear()
        logger.info("Cache cleared")

    def cleanup_expired(self) -> int:
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]
        for key in expired_keys:
            del self.cache[key]
            self.stats['expirations'] += 1
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        return {
            **self.stats,
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        } 