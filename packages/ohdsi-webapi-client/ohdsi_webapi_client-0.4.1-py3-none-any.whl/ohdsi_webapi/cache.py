"""Generic caching utilities for OHDSI WebAPI client.

This module provides a configurable, in-memory caching system with TTL (time-to-live)
support and LRU (least recently used) eviction. The cache helps improve performance
by avoiding repeated WebAPI calls for expensive operations like vocabulary searches
and concept set listings.

The caching system is controlled by environment variables and can be disabled
completely for debugging or when real-time data is required.

Environment Variables
---------------------
OHDSI_CACHE_ENABLED : bool, default True
    Enable or disable all caching functionality.
OHDSI_CACHE_TTL : int, default 300
    Default time-to-live for cache entries in seconds (5 minutes).
OHDSI_CACHE_MAX_SIZE : int, default 128
    Maximum number of cache entries before LRU eviction occurs.

Examples
--------
Basic usage with decorator:

>>> @cached_method(ttl_seconds=600)  # 10 minutes
... def expensive_operation(self, param):
...     return self._http.get(f"/expensive/{param}")

Force refresh:

>>> result = client.vocabulary.search("diabetes", force_refresh=True)

Check cache statistics:

>>> from ohdsi_webapi.cache import cache_stats
>>> print(cache_stats())
{'size': 42, 'max_size': 128, 'enabled': True, 'ttl_seconds': 300}
"""

from __future__ import annotations

import time
from typing import Any, Callable, ParamSpec, TypeVar

# Import environment utilities
from .env import get_env_bool, get_env_int

P = ParamSpec("P")
T = TypeVar("T")

# Environment variables for cache configuration
CACHE_ENABLED = get_env_bool("OHDSI_CACHE_ENABLED", True)
CACHE_TTL_SECONDS = get_env_int("OHDSI_CACHE_TTL", 300)  # 5 minutes default
CACHE_MAX_SIZE = get_env_int("OHDSI_CACHE_MAX_SIZE", 128)  # 128 items default


class CacheEntry:
    """Cache entry with timestamp for TTL (time-to-live) support.

    Each cache entry stores a value along with creation timestamp and TTL duration.
    This allows for automatic expiration of stale data based on configurable
    time windows.

    Parameters
    ----------
    value : Any
        The value to cache (typically API response data).
    ttl_seconds : int, default from OHDSI_CACHE_TTL
        Time-to-live in seconds before this entry expires.

    Examples
    --------
    >>> entry = CacheEntry("some data", ttl_seconds=600)  # 10 minutes
    >>> if not entry.is_expired():
    ...     return entry.value
    """

    def __init__(self, value: Any, ttl_seconds: int = CACHE_TTL_SECONDS):
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds

    def is_expired(self) -> bool:
        """Check if cache entry has expired based on TTL.

        Returns
        -------
        bool
            True if the entry has exceeded its time-to-live duration.

        Examples
        --------
        >>> entry = CacheEntry("data", ttl_seconds=300)
        >>> # ... 301 seconds later ...
        >>> entry.is_expired()  # Returns True
        """
        return time.time() - self.created_at > self.ttl_seconds


class WebApiCache:
    """Simple in-memory cache with TTL and LRU eviction.

    This cache implementation provides automatic expiration of stale entries
    based on TTL (time-to-live) and evicts least recently used items when
    the cache reaches its maximum size. It's designed specifically for
    caching WebAPI responses to improve performance.

    Parameters
    ----------
    max_size : int, default from OHDSI_CACHE_MAX_SIZE
        Maximum number of cache entries. When exceeded, least recently
        used entries are evicted.

    Examples
    --------
    >>> cache = WebApiCache(max_size=256)
    >>> cache.set("key1", {"data": "value"}, ttl_seconds=600)
    >>> result = cache.get("key1")  # Returns {"data": "value"} if not expired
    >>> cache.clear()  # Remove all entries

    Notes
    -----
    The cache uses MD5 hashing for keys to ensure consistent length and
    avoid issues with special characters in method arguments.
    """

    def __init__(self, max_size: int = CACHE_MAX_SIZE):
        self._cache: dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._access_order: list[str] = []  # For LRU eviction

    def _evict_expired(self) -> None:
        """Remove expired entries."""
        expired_keys = [key for key, entry in self._cache.items() if entry.is_expired()]
        for key in expired_keys:
            self._cache.pop(key, None)
            if key in self._access_order:
                self._access_order.remove(key)

    def _evict_lru(self) -> None:
        """Evict least recently used items if cache is full."""
        while len(self._cache) >= self._max_size and self._access_order:
            oldest_key = self._access_order.pop(0)
            self._cache.pop(oldest_key, None)

    def get(self, key: str) -> Any | None:
        """Get value from cache if exists and not expired.

        This method automatically handles expired entry cleanup and LRU
        ordering updates. If an entry is found but expired, it's removed
        from the cache.

        Parameters
        ----------
        key : str
            The cache key to retrieve.

        Returns
        -------
        Any or None
            The cached value if found and not expired, None otherwise.

        Examples
        --------
        >>> cache = WebApiCache()
        >>> cache.set("concepts", [{"id": 1, "name": "diabetes"}])
        >>> result = cache.get("concepts")  # Returns the list if not expired
        >>> missing = cache.get("nonexistent")  # Returns None
        """
        self._evict_expired()

        entry = self._cache.get(key)
        if entry and not entry.is_expired():
            # Move to end (most recently used)
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            return entry.value
        elif entry:
            # Expired entry, remove it
            self._cache.pop(key, None)
            if key in self._access_order:
                self._access_order.remove(key)

        return None

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Set value in cache with optional custom TTL.

        If caching is disabled globally via OHDSI_CACHE_ENABLED, this method
        returns immediately without storing anything.

        Parameters
        ----------
        key : str
            The cache key to store under.
        value : Any
            The value to cache (typically API response data).
        ttl_seconds : int, optional
            Custom TTL for this entry. If None, uses global default.

        Examples
        --------
        >>> cache = WebApiCache()
        >>>
        >>> # Use default TTL
        >>> cache.set("key1", {"data": "value"})
        >>>
        >>> # Custom TTL for expensive operations
        >>> cache.set("expensive_data", large_dataset, ttl_seconds=3600)  # 1 hour
        """
        if not CACHE_ENABLED:
            return

        self._evict_expired()
        self._evict_lru()

        ttl = ttl_seconds if ttl_seconds is not None else CACHE_TTL_SECONDS
        self._cache[key] = CacheEntry(value, ttl)

        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

    def clear(self) -> None:
        """Clear all cache entries.

        This removes all cached data and resets the LRU ordering.
        Useful for debugging or when you need to ensure fresh data.

        Examples
        --------
        >>> cache = WebApiCache()
        >>> cache.set("key1", "value1")
        >>> cache.clear()
        >>> cache.get("key1")  # Returns None
        """
        self._cache.clear()
        self._access_order.clear()

    def stats(self) -> dict[str, Any]:
        """Get cache statistics and configuration.

        This method automatically cleans up expired entries before
        returning statistics, so the size reflects only valid entries.

        Returns
        -------
        dict
            Dictionary containing cache size, configuration, and status.

        Examples
        --------
        >>> cache = WebApiCache()
        >>> stats = cache.stats()
        >>> print(f"Cache usage: {stats['size']}/{stats['max_size']}")
        >>> print(f"TTL: {stats['ttl_seconds']} seconds")

        Returns
        -------
        dict with keys:
            - size: Current number of valid cache entries
            - max_size: Maximum cache capacity
            - enabled: Whether caching is globally enabled
            - ttl_seconds: Default TTL for new entries
        """
        self._evict_expired()
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "enabled": CACHE_ENABLED,
            "ttl_seconds": CACHE_TTL_SECONDS,
        }


# Global cache instance
_global_cache = WebApiCache()


def get_cache_key(*args: Any, method_name: str = "", **kwargs: Any) -> str:
    """Generate a human-readable cache key from method arguments.

    This function creates descriptive, developer-friendly cache keys that clearly
    show what operation and parameters are being cached. Keys are designed to be
    easily readable in logs, debugging output, and cache statistics.

    Parameters
    ----------
    *args : Any
        Positional arguments to include in the cache key.
    method_name : str, default ""
        The method name to include for uniqueness across different methods.
    **kwargs : Any
        Keyword arguments to include in the cache key.

    Returns
    -------
    str
        A human-readable cache key that clearly describes the cached operation.

    Examples
    --------
    >>> # Individual concept lookup
    >>> get_cache_key(201826, method_name="VocabularyService.get_concept")
    'VocabularyService.get_concept(201826)'
    >>>
    >>> # Basic concept search
    >>> get_cache_key("diabetes", method_name="VocabularyService.search",
    ...               page=1, page_size=20)
    'VocabularyService.search("diabetes", page=1, page_size=20)'
    >>>
    >>> # Filtered concept search
    >>> get_cache_key("diabetes", method_name="VocabularyService.search",
    ...               domain_id="Condition", standard_concept="S")
    'VocabularyService.search("diabetes", domain_id="Condition", standard_concept="S")'
    >>>
    >>> # List operations with no args
    >>> get_cache_key(method_name="VocabularyService.list_domains")
    'VocabularyService.list_domains()'
    >>>
    >>> # Concept relationships
    >>> get_cache_key(201826, method_name="VocabularyService.descendants")
    'VocabularyService.descendants(201826)'

    Notes
    -----
    The cache key generation creates readable keys that:
    - Clearly show the service method being called
    - Display all arguments and parameters
    - Use function call syntax for familiarity
    - Are consistent and deterministic
    - Help with debugging and monitoring

    Key characteristics:
    - Easy to read and understand what's cached
    - Show exact method and parameters
    - Consistent ordering (kwargs sorted alphabetically)
    - No length limitations from hashing
    - Perfect for logging and debugging
    """
    # Extract just the class and method name for cleaner keys
    if "." in method_name:
        parts = method_name.split(".")
        # Get the last two parts: ClassName.method_name
        clean_method = ".".join(parts[-2:]) if len(parts) >= 2 else parts[-1]
    else:
        clean_method = method_name

    # Build argument list
    arg_parts = []

    # Add positional arguments
    for arg in args:
        if isinstance(arg, str):
            # Quote strings for clarity
            arg_parts.append(f'"{arg}"')
        else:
            arg_parts.append(str(arg))

    # Add keyword arguments (sorted for consistency)
    for key, value in sorted(kwargs.items()):
        if isinstance(value, str):
            arg_parts.append(f'{key}="{value}"')
        else:
            arg_parts.append(f"{key}={value}")

    # Combine into function call syntax
    if arg_parts:
        return f"{clean_method}({', '.join(arg_parts)})"
    else:
        return f"{clean_method}()"


def cached_method(ttl_seconds: int | None = None, enabled: bool | None = None) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator for caching service method results with configurable TTL.

    This decorator automatically caches method results based on their arguments,
    with support for TTL expiration and force refresh capability. It's designed
    specifically for service methods that make expensive WebAPI calls.

    Parameters
    ----------
    ttl_seconds : int, optional
        Cache TTL override in seconds. If None, uses the global default
        from OHDSI_CACHE_TTL environment variable.
    enabled : bool, optional
        Cache enabled override. If None, uses the global setting from
        OHDSI_CACHE_ENABLED environment variable.

    Returns
    -------
    callable
        A decorator function that wraps the target method with caching.

    Examples
    --------
    Basic usage with default settings:

    >>> @cached_method()
    ... def search_concepts(self, query: str) -> list:
    ...     return self._http.get(f"/vocabulary/search?q={query}")

    Custom TTL for expensive operations:

    >>> @cached_method(ttl_seconds=3600)  # 1 hour
    ... def list_all_concept_sets(self) -> list:
    ...     return self._http.get("/conceptset/")

    Disable caching for specific method:

    >>> @cached_method(enabled=False)
    ... def get_real_time_data(self) -> dict:
    ...     return self._http.get("/real-time-endpoint")

    Using force_refresh parameter:

    >>> # Normal cached call
    >>> results = client.vocabulary.search("diabetes")
    >>>
    >>> # Force fresh data from server
    >>> fresh_results = client.vocabulary.search("diabetes", force_refresh=True)

    Notes
    -----
    The decorator automatically handles:
    - Cache key generation from method arguments
    - TTL-based expiration
    - LRU eviction when cache is full
    - Global enable/disable via environment variables
    - Force refresh via force_refresh parameter

    The 'self' parameter is automatically excluded from cache key generation
    to ensure proper caching across different service instances.
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Check if caching is enabled
            cache_enabled = enabled if enabled is not None else CACHE_ENABLED
            force_refresh = kwargs.pop("force_refresh", False)

            if not cache_enabled or force_refresh:
                return func(*args, **kwargs)

            # Generate cache key
            cache_key = get_cache_key(*args[1:], method_name=f"{func.__module__}.{func.__qualname__}", **kwargs)  # Skip 'self' parameter

            # Try to get from cache
            cached_result = _global_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Cache miss - call function and cache result
            result = func(*args, **kwargs)
            _global_cache.set(cache_key, result, ttl_seconds)

            return result

        return wrapper

    return decorator


def clear_cache() -> None:
    """Clear all cached data globally.

    This function clears all entries from the global cache instance.
    Useful for debugging, testing, or when you need to ensure all
    subsequent API calls fetch fresh data.

    Examples
    --------
    >>> from ohdsi_webapi.cache import clear_cache
    >>>
    >>> # Clear all cached data
    >>> clear_cache()
    >>>
    >>> # All subsequent API calls will fetch fresh data
    >>> concepts = client.vocabulary.search("diabetes")  # Fresh from server
    """
    _global_cache.clear()


def cache_stats() -> dict[str, Any]:
    """Get global cache statistics and configuration.

    Returns current cache usage, configuration settings, and status
    information. Useful for monitoring cache performance and debugging.

    Returns
    -------
    dict
        Dictionary containing cache statistics with keys:
        - size: Number of currently cached entries
        - max_size: Maximum cache capacity
        - enabled: Whether caching is globally enabled
        - ttl_seconds: Default TTL for new cache entries

    Examples
    --------
    >>> from ohdsi_webapi.cache import cache_stats
    >>>
    >>> stats = cache_stats()
    >>> print(f"Cache usage: {stats['size']}/{stats['max_size']}")
    >>> print(f"Caching enabled: {stats['enabled']}")
    >>> print(f"Default TTL: {stats['ttl_seconds']} seconds")
    >>>
    >>> # Example output:
    >>> # Cache usage: 42/128
    >>> # Caching enabled: True
    >>> # Default TTL: 300 seconds
    """
    return _global_cache.stats()


def cache_contents() -> dict[str, Any]:
    """Get detailed information about all cached entries.

    This function provides a developer-friendly view of what's currently
    cached, including readable cache keys, creation times, and TTL status.
    Perfect for debugging and understanding cache behavior.

    Returns
    -------
    dict
        Dictionary with cache statistics and detailed entry information:
        - stats: Overall cache statistics
        - entries: List of cache entry details with readable keys

    Examples
    --------
    >>> from ohdsi_webapi.cache import cache_contents
    >>>
    >>> contents = cache_contents()
    >>> print(f"Cache size: {contents['stats']['size']}")
    >>>
    >>> for entry in contents['entries']:
    ...     print(f"Key: {entry['key']}")
    ...     print(f"  Created: {entry['created_ago']} seconds ago")
    ...     print(f"  Expires in: {entry['expires_in']} seconds")
    ...     print(f"  Data type: {entry['data_type']}")

    Sample output:
    Cache size: 3
    Key: VocabularyService.get_concept(201826)
      Created: 45 seconds ago
      Expires in: 255 seconds
      Data type: <class 'Concept'>
    Key: VocabularyService.list_domains()
      Created: 120 seconds ago
      Expires in: 180 seconds
      Data type: <class 'list'> (50 items)
    """
    import time

    _global_cache._evict_expired()  # Clean up first

    stats = _global_cache.stats()
    entries = []

    current_time = time.time()

    for key, entry in _global_cache._cache.items():
        created_ago = current_time - entry.created_at
        expires_in = entry.ttl_seconds - created_ago

        # Determine data type info
        data_type = type(entry.value).__name__
        if isinstance(entry.value, list):
            data_info = f"list ({len(entry.value)} items)"
        elif isinstance(entry.value, dict):
            data_info = f"dict ({len(entry.value)} keys)"
        elif hasattr(entry.value, "__class__"):
            data_info = f"{entry.value.__class__.__name__}"
        else:
            data_info = data_type

        entries.append(
            {
                "key": key,
                "created_ago": round(created_ago, 1),
                "expires_in": round(expires_in, 1) if expires_in > 0 else "expired",
                "data_type": data_info,
                "ttl_seconds": entry.ttl_seconds,
            }
        )

    # Sort by creation time (most recent first)
    entries.sort(key=lambda x: x["created_ago"])

    return {"stats": stats, "entries": entries}
