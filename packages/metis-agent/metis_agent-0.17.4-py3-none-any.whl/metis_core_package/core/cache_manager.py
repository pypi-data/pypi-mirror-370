"""
Enhanced Cache Manager for Metis Agent with TTL support.

This module provides intelligent caching capabilities with time-to-live (TTL),
LRU eviction, and tool-specific caching policies for performance optimization.
"""
import time
import hashlib
import json
import threading
from typing import Any, Dict, Optional, Union, List, Tuple
from dataclasses import dataclass, asdict
from collections import OrderedDict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CachePolicy(Enum):
    """Cache policy options for different scenarios."""
    AGGRESSIVE = "aggressive"  # Cache everything, long TTL
    CONSERVATIVE = "conservative"  # Cache selectively, short TTL
    DISABLED = "disabled"  # No caching
    CUSTOM = "custom"  # Custom policy defined per tool


@dataclass
class CacheEntry:
    """Represents a single cache entry with metadata."""
    value: Any
    created_at: float
    last_accessed: float
    access_count: int
    ttl: float
    size_bytes: int
    cache_key: str
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() > (self.created_at + self.ttl)
    
    def is_stale(self, staleness_threshold: float = 0.8) -> bool:
        """Check if cache entry is approaching expiration."""
        age = time.time() - self.created_at
        return (age / self.ttl) > staleness_threshold
    
    def update_access(self):
        """Update access metadata."""
        self.last_accessed = time.time()
        self.access_count += 1


@dataclass
class CacheMetrics:
    """Cache performance metrics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expired_removals: int = 0
    total_size_bytes: int = 0
    total_entries: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate percentage."""
        return 100.0 - self.hit_rate


class CacheKeyGenerator:
    """Generates intelligent cache keys for various inputs."""
    
    @staticmethod
    def generate_key(tool_name: str, task: str, **kwargs) -> str:
        """
        Generate a deterministic cache key from tool name, task, and parameters.
        
        Args:
            tool_name: Name of the tool
            task: The task being executed
            **kwargs: Additional parameters affecting the result
            
        Returns:
            SHA-256 hash as cache key
        """
        # Create deterministic representation
        key_data = {
            "tool": tool_name,
            "task": task,
            "params": kwargs
        }
        
        # Sort keys for deterministic JSON serialization
        key_json = json.dumps(key_data, sort_keys=True, default=str)
        
        # Generate SHA-256 hash
        return hashlib.sha256(key_json.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_context_key(user_id: str, session_id: Optional[str] = None) -> str:
        """Generate cache key for context-sensitive operations."""
        context_data = {"user_id": user_id}
        if session_id:
            context_data["session_id"] = session_id
            
        key_json = json.dumps(context_data, sort_keys=True)
        return hashlib.sha256(key_json.encode('utf-8')).hexdigest()


class LRUCacheStore:
    """LRU (Least Recently Used) cache store with TTL support."""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self.metrics = CacheMetrics()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache, handling TTL and LRU updates."""
        with self._lock:
            if key not in self._cache:
                self.metrics.misses += 1
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired():
                self._remove_entry(key)
                self.metrics.misses += 1
                self.metrics.expired_removals += 1
                return None
            
            # Update access and move to end (most recently used)
            entry.update_access()
            self._cache.move_to_end(key)
            self.metrics.hits += 1
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: float = 3600) -> bool:
        """Set value in cache with TTL."""
        with self._lock:
            # Calculate entry size (rough estimation)
            size_bytes = self._estimate_size(value)
            
            # Check if we need to make space
            while (len(self._cache) >= self.max_size or 
                   self.metrics.total_size_bytes + size_bytes > self.max_memory_bytes):
                if not self._evict_lru():
                    # Cannot make space
                    return False
            
            # Remove existing entry if updating
            if key in self._cache:
                self._remove_entry(key)
            
            # Create new entry
            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                ttl=ttl,
                size_bytes=size_bytes,
                cache_key=key
            )
            
            # Add to cache
            self._cache[key] = entry
            self.metrics.total_entries += 1
            self.metrics.total_size_bytes += size_bytes
            
            return True
    
    def invalidate(self, key: str) -> bool:
        """Remove specific entry from cache."""
        with self._lock:
            if key in self._cache:
                self._remove_entry(key)
                return True
            return False
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self.metrics = CacheMetrics()
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries and return count removed."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() 
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                self._remove_entry(key)
                self.metrics.expired_removals += 1
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        with self._lock:
            # Include computed properties from metrics
            metrics_dict = asdict(self.metrics)
            metrics_dict["hit_rate"] = self.metrics.hit_rate
            metrics_dict["miss_rate"] = self.metrics.miss_rate
            
            return {
                "metrics": metrics_dict,
                "size": len(self._cache),
                "max_size": self.max_size,
                "memory_usage_mb": self.metrics.total_size_bytes / (1024 * 1024),
                "max_memory_mb": self.max_memory_bytes / (1024 * 1024),
                "oldest_entry_age": self._get_oldest_entry_age(),
                "stale_entries": self._count_stale_entries()
            }
    
    def _remove_entry(self, key: str):
        """Remove entry and update metrics."""
        if key in self._cache:
            entry = self._cache.pop(key)
            self.metrics.total_entries -= 1
            self.metrics.total_size_bytes -= entry.size_bytes
    
    def _evict_lru(self) -> bool:
        """Evict least recently used entry."""
        if not self._cache:
            return False
        
        # Remove oldest (least recently used) entry
        key = next(iter(self._cache))
        self._remove_entry(key)
        self.metrics.evictions += 1
        return True
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of value in bytes."""
        try:
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, (dict, list)):
                return len(json.dumps(value, default=str).encode('utf-8'))
            elif hasattr(value, '__sizeof__'):
                return value.__sizeof__()
            else:
                return len(str(value).encode('utf-8'))
        except:
            return 1024  # Default fallback size
    
    def _get_oldest_entry_age(self) -> float:
        """Get age of oldest entry in seconds."""
        if not self._cache:
            return 0.0
        
        oldest_entry = next(iter(self._cache.values()))
        return time.time() - oldest_entry.created_at
    
    def _count_stale_entries(self) -> int:
        """Count entries that are approaching expiration."""
        return sum(1 for entry in self._cache.values() if entry.is_stale())


class CacheManager:
    """
    Main cache manager providing intelligent caching with TTL, LRU eviction,
    and tool-specific policies.
    """
    
    def __init__(self, 
                 max_size: int = 1000,
                 max_memory_mb: int = 100,
                 default_ttl: float = 3600,
                 cleanup_interval: float = 300):
        """
        Initialize cache manager.
        
        Args:
            max_size: Maximum number of cache entries
            max_memory_mb: Maximum memory usage in MB
            default_ttl: Default TTL in seconds
            cleanup_interval: Cleanup interval in seconds
        """
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        self._store = LRUCacheStore(max_size, max_memory_mb)
        self._tool_policies: Dict[str, Dict[str, Any]] = {}
        self._last_cleanup = time.time()
        
        logger.info(f"CacheManager initialized: max_size={max_size}, "
                   f"max_memory_mb={max_memory_mb}, default_ttl={default_ttl}s")
    
    def get(self, tool_name: str, task: str, **kwargs) -> Optional[Any]:
        """
        Get cached result for tool execution.
        
        Args:
            tool_name: Name of the tool
            task: The task being executed
            **kwargs: Additional parameters
            
        Returns:
            Cached result or None if not found/expired
        """
        if not self._should_cache(tool_name):
            return None
        
        key = CacheKeyGenerator.generate_key(tool_name, task, **kwargs)
        result = self._store.get(key)
        
        if result is not None:
            logger.debug(f"Cache HIT for {tool_name}: {key[:16]}...")
        else:
            logger.debug(f"Cache MISS for {tool_name}: {key[:16]}...")
        
        self._maybe_cleanup()
        return result
    
    def set(self, tool_name: str, task: str, result: Any, **kwargs) -> bool:
        """
        Cache result of tool execution.
        
        Args:
            tool_name: Name of the tool
            task: The task being executed
            result: Result to cache
            **kwargs: Additional parameters
            
        Returns:
            True if cached successfully
        """
        if not self._should_cache(tool_name):
            return False
        
        # Get tool-specific TTL
        ttl = self._get_tool_ttl(tool_name)
        
        key = CacheKeyGenerator.generate_key(tool_name, task, **kwargs)
        success = self._store.set(key, result, ttl)
        
        if success:
            logger.debug(f"Cache SET for {tool_name}: {key[:16]}... (TTL={ttl}s)")
        else:
            logger.warning(f"Cache SET failed for {tool_name}: {key[:16]}...")
        
        self._maybe_cleanup()
        return success
    
    def invalidate_tool(self, tool_name: str):
        """Invalidate all cache entries for a specific tool."""
        # Note: This is a simplified implementation
        # In production, we'd need to track tool-specific keys
        logger.info(f"Invalidating cache entries for tool: {tool_name}")
        # For now, we'll just clear all cache - could be optimized later
        self._store.clear()
    
    def set_tool_policy(self, tool_name: str, 
                       policy: CachePolicy = CachePolicy.CONSERVATIVE,
                       ttl: Optional[float] = None,
                       cache_enabled: bool = True):
        """
        Set caching policy for a specific tool.
        
        Args:
            tool_name: Name of the tool
            policy: Cache policy to apply
            ttl: Custom TTL in seconds
            cache_enabled: Whether caching is enabled for this tool
        """
        self._tool_policies[tool_name] = {
            "policy": policy,
            "ttl": ttl or self._get_default_ttl_for_policy(policy),
            "enabled": cache_enabled
        }
        
        logger.info(f"Set cache policy for {tool_name}: {policy.value}, "
                   f"TTL={self._tool_policies[tool_name]['ttl']}s")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        stats = self._store.get_stats()
        stats["tool_policies"] = self._tool_policies
        stats["last_cleanup"] = self._last_cleanup
        return stats
    
    def force_cleanup(self) -> int:
        """Force cleanup of expired entries."""
        removed = self._store.cleanup_expired()
        self._last_cleanup = time.time()
        logger.info(f"Cache cleanup removed {removed} expired entries")
        return removed
    
    def clear(self):
        """Clear all cache entries."""
        self._store.clear()
        logger.info("Cache cleared")
    
    def _should_cache(self, tool_name: str) -> bool:
        """Check if caching is enabled for the tool."""
        if tool_name in self._tool_policies:
            return self._tool_policies[tool_name]["enabled"]
        return True  # Default to enabled
    
    def _get_tool_ttl(self, tool_name: str) -> float:
        """Get TTL for specific tool."""
        if tool_name in self._tool_policies:
            return self._tool_policies[tool_name]["ttl"]
        return self.default_ttl
    
    def _get_default_ttl_for_policy(self, policy: CachePolicy) -> float:
        """Get default TTL based on cache policy."""
        if policy == CachePolicy.AGGRESSIVE:
            return 7200  # 2 hours
        elif policy == CachePolicy.CONSERVATIVE:
            return 1800  # 30 minutes
        else:
            return self.default_ttl
    
    def _maybe_cleanup(self):
        """Perform cleanup if interval has passed."""
        if time.time() - self._last_cleanup > self.cleanup_interval:
            self.force_cleanup()


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get or create global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def configure_cache(max_size: int = 1000, 
                   max_memory_mb: int = 100,
                   default_ttl: float = 3600) -> CacheManager:
    """Configure global cache manager with custom settings."""
    global _cache_manager
    _cache_manager = CacheManager(max_size, max_memory_mb, default_ttl)
    return _cache_manager