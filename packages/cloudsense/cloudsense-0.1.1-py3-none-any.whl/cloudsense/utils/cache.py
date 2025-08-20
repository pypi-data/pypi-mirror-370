"""Server-side caching utilities for CloudSense"""

import time
import hashlib
import json
import logging
from typing import Dict, Any, Optional, Union
from flask import current_app

logger = logging.getLogger(__name__)

# In-memory cache storage
_cache_storage: Dict[str, Dict[str, Any]] = {}
_cache_timestamps: Dict[str, float] = {}
_cache_stats = {
    'hits': 0,
    'misses': 0,
    'sets': 0,
    'evictions': 0
}

# Maximum cache size to prevent memory issues
MAX_CACHE_SIZE = 1000


def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate a unique cache key from function arguments
    
    Args:
        *args: Function positional arguments
        **kwargs: Function keyword arguments
        
    Returns:
        str: Unique cache key
    """
    # Create a string representation of all arguments
    key_data = {
        'args': args,
        'kwargs': kwargs
    }
    
    # Serialize to JSON for consistent key generation
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    
    # Generate MD5 hash for compact key
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    
    return f"cloudsense_cache_{key_hash}"


def get_cache_duration() -> int:
    """Get cache duration from config or default"""
    try:
        return current_app.config.get('CACHE_DURATION', 3600)
    except RuntimeError:
        # Outside app context, use default
        return 3600


def get_cached_data(cache_key: str, custom_duration: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Get cached data if still valid
    
    Args:
        cache_key: Unique cache key
        custom_duration: Override default cache duration
        
    Returns:
        Cached data if valid, None if expired or not found
    """
    global _cache_stats
    
    if cache_key not in _cache_storage:
        _cache_stats['misses'] += 1
        return None
    
    # Check if cache is still valid
    cache_duration = custom_duration or get_cache_duration()
    cache_age = time.time() - _cache_timestamps[cache_key]
    
    if cache_age < cache_duration:
        _cache_stats['hits'] += 1
        logger.debug(f"Cache HIT for key: {cache_key[:20]}... (age: {cache_age:.1f}s)")
        return _cache_storage[cache_key]
    else:
        # Cache expired
        logger.debug(f"Cache EXPIRED for key: {cache_key[:20]}... (age: {cache_age:.1f}s)")
        evict_cache_entry(cache_key)
        _cache_stats['misses'] += 1
        return None


def set_cached_data(cache_key: str, data: Dict[str, Any]) -> None:
    """
    Cache the data with timestamp
    
    Args:
        cache_key: Unique cache key
        data: Data to cache
    """
    global _cache_stats
    
    # Enforce maximum cache size
    if len(_cache_storage) >= MAX_CACHE_SIZE:
        evict_oldest_entries(int(MAX_CACHE_SIZE * 0.1))  # Remove 10% of entries
    
    _cache_storage[cache_key] = data
    _cache_timestamps[cache_key] = time.time()
    _cache_stats['sets'] += 1
    
    logger.debug(f"Cache SET for key: {cache_key[:20]}... (cache size: {len(_cache_storage)})")


def evict_cache_entry(cache_key: str) -> None:
    """Remove a specific cache entry"""
    global _cache_stats
    
    if cache_key in _cache_storage:
        del _cache_storage[cache_key]
        del _cache_timestamps[cache_key]
        _cache_stats['evictions'] += 1


def evict_oldest_entries(count: int) -> None:
    """Evict the oldest cache entries"""
    if not _cache_timestamps:
        return
    
    # Sort by timestamp (oldest first)
    sorted_entries = sorted(_cache_timestamps.items(), key=lambda x: x[1])
    
    for cache_key, _ in sorted_entries[:count]:
        evict_cache_entry(cache_key)
    
    logger.debug(f"Evicted {count} oldest cache entries")


def clear_cache() -> None:
    """Clear all cached data"""
    global _cache_storage, _cache_timestamps, _cache_stats
    
    entries_cleared = len(_cache_storage)
    _cache_storage.clear()
    _cache_timestamps.clear()
    
    logger.debug(f"Cache cleared: {entries_cleared} entries removed")


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    total_requests = _cache_stats['hits'] + _cache_stats['misses']
    hit_rate = (_cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
    
    return {
        'total_entries': len(_cache_storage),
        'hits': _cache_stats['hits'],
        'misses': _cache_stats['misses'],
        'sets': _cache_stats['sets'],
        'evictions': _cache_stats['evictions'],
        'hit_rate_percent': round(hit_rate, 2),
        'total_requests': total_requests,
        'max_cache_size': MAX_CACHE_SIZE
    }


def cache_result(cache_duration: Optional[int] = None):
    """
    Decorator to cache function results
    
    Args:
        cache_duration: Override default cache duration
        
    Usage:
        @cache_result()
        def expensive_function(arg1, arg2):
            return expensive_computation(arg1, arg2)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = generate_cache_key(func.__name__, *args, **kwargs)
            
            # Try to get cached result
            cached_data = get_cached_data(cache_key, cache_duration)
            if cached_data is not None:
                return cached_data
            
            # Cache miss - call the actual function  
            logger.debug(f"Cache MISS for {func.__name__} - fetching fresh data")
            result = func(*args, **kwargs)
            
            # Cache the result
            if result and not isinstance(result, dict) or 'error' not in result:
                set_cached_data(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalidate cache entries matching a pattern
    
    Args:
        pattern: Pattern to match in cache keys
        
    Returns:
        Number of entries invalidated
    """
    keys_to_remove = [key for key in _cache_storage.keys() if pattern in key]
    
    for key in keys_to_remove:
        evict_cache_entry(key)
    
    logger.debug(f"Invalidated {len(keys_to_remove)} cache entries matching pattern: {pattern}")
    return len(keys_to_remove)


def cleanup_expired_cache() -> int:
    """
    Clean up expired cache entries
    
    Returns:
        Number of expired entries removed
    """
    current_time = time.time()
    cache_duration = get_cache_duration()
    
    expired_keys = [
        key for key, timestamp in _cache_timestamps.items()
        if current_time - timestamp > cache_duration
    ]
    
    for key in expired_keys:
        evict_cache_entry(key)
    
    if expired_keys:
        logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    return len(expired_keys)
