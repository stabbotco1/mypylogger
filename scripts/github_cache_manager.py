#!/usr/bin/env python3
"""
GitHub API Cache and Rate Limiting Manager

This module implements response caching and rate limiting compliance
for GitHub API requests to optimize performance and stay within API limits.
"""

import hashlib
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class CacheEntryType(Enum):
    """Types of cache entries with different TTL strategies."""

    WORKFLOW_RUNS = "workflow_runs"  # Workflow run data
    REPOSITORY_INFO = "repository_info"  # Repository metadata
    RATE_LIMIT_INFO = "rate_limit_info"  # Rate limit status
    USER_INFO = "user_info"  # User/organization info


@dataclass
class CacheEntry:
    """A cached API response with metadata."""

    key: str
    data: Any
    entry_type: CacheEntryType
    created_at: datetime
    expires_at: datetime
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    hit_count: int = 0

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return datetime.now(timezone.utc) >= self.expires_at

    def is_stale(self, staleness_threshold: timedelta = timedelta(minutes=5)) -> bool:
        """Check if the cache entry is stale but not expired."""
        stale_time = self.expires_at - staleness_threshold
        return datetime.now(timezone.utc) >= stale_time

    def record_hit(self) -> None:
        """Record a cache hit."""
        self.hit_count += 1


@dataclass
class RateLimitInfo:
    """GitHub API rate limit information."""

    limit: int
    remaining: int
    reset_time: datetime
    used: int = 0

    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> "RateLimitInfo":
        """Create RateLimitInfo from HTTP headers."""
        limit = int(headers.get("X-RateLimit-Limit", 5000))
        remaining = int(headers.get("X-RateLimit-Remaining", limit))
        reset_timestamp = int(headers.get("X-RateLimit-Reset", time.time() + 3600))
        reset_time = datetime.fromtimestamp(reset_timestamp, tz=timezone.utc)
        used = limit - remaining

        return cls(limit=limit, remaining=remaining, reset_time=reset_time, used=used)

    def time_until_reset(self) -> timedelta:
        """Get time until rate limit resets."""
        return max(timedelta(0), self.reset_time - datetime.now(timezone.utc))

    def is_exhausted(self, threshold: int = 10) -> bool:
        """Check if rate limit is exhausted (below threshold)."""
        return self.remaining <= threshold

    def requests_per_minute_available(self) -> float:
        """Calculate available requests per minute."""
        time_until_reset = self.time_until_reset()
        if time_until_reset.total_seconds() <= 0:
            return float(self.limit)

        minutes_until_reset = time_until_reset.total_seconds() / 60
        return self.remaining / minutes_until_reset


@dataclass
class CacheConfig:
    """Configuration for cache behavior."""

    # TTL settings for different entry types (seconds)
    workflow_runs_ttl: int = 30  # Workflow runs change frequently
    repository_info_ttl: int = 3600  # Repository info is relatively stable
    rate_limit_info_ttl: int = 60  # Rate limit info changes with each request
    user_info_ttl: int = 1800  # User info is fairly stable

    # Cache size limits
    max_entries: int = 1000  # Maximum number of cache entries
    max_memory_mb: int = 50  # Maximum memory usage estimate

    # Staleness settings
    allow_stale_responses: bool = True  # Allow stale responses when API is unavailable
    stale_threshold_minutes: int = 5  # How long before entry is considered stale

    # Rate limiting settings
    rate_limit_threshold: int = 10  # Remaining requests before throttling
    rate_limit_backoff_seconds: int = 60  # How long to wait when rate limited

    def get_ttl_for_type(self, entry_type: CacheEntryType) -> int:
        """Get TTL for a specific cache entry type."""
        ttl_map = {
            CacheEntryType.WORKFLOW_RUNS: self.workflow_runs_ttl,
            CacheEntryType.REPOSITORY_INFO: self.repository_info_ttl,
            CacheEntryType.RATE_LIMIT_INFO: self.rate_limit_info_ttl,
            CacheEntryType.USER_INFO: self.user_info_ttl,
        }
        return ttl_map.get(entry_type, self.workflow_runs_ttl)


class GitHubCacheManager:
    """
    Manages caching and rate limiting for GitHub API requests.

    Features:
    - Response caching with appropriate TTL for different data types
    - Rate limit tracking and compliance
    - Request queuing and throttling
    - Cache invalidation logic for real-time updates
    - Stale response handling for better availability
    """

    def __init__(self, config: Optional[CacheConfig] = None):
        """
        Initialize the cache manager.

        Args:
            config: Cache configuration
        """
        self.config = config or CacheConfig()
        self.cache: Dict[str, CacheEntry] = {}
        self.rate_limit_info: Optional[RateLimitInfo] = None
        self.request_queue: List[Tuple[str, datetime]] = []  # (endpoint, timestamp)
        self.last_request_time: Optional[datetime] = None

    def _generate_cache_key(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a cache key for an API endpoint and parameters.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Cache key string
        """
        # Normalize endpoint
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        # Create key from endpoint and sorted parameters
        key_parts = [endpoint]
        if params:
            sorted_params = sorted(params.items())
            param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
            key_parts.append(param_str)

        key_string = "|".join(key_parts)

        # Hash long keys to keep them manageable
        if len(key_string) > 200:
            return hashlib.sha256(key_string.encode()).hexdigest()

        return key_string

    def _determine_entry_type(self, endpoint: str) -> CacheEntryType:
        """
        Determine cache entry type based on endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            Cache entry type
        """
        if "/actions/runs" in endpoint:
            return CacheEntryType.WORKFLOW_RUNS
        elif "/repos/" in endpoint and "/actions/" not in endpoint:
            # Repository info endpoints like /repos/owner/repo
            return CacheEntryType.REPOSITORY_INFO
        elif "/rate_limit" in endpoint:
            return CacheEntryType.RATE_LIMIT_INFO
        elif "/user" in endpoint or "/orgs/" in endpoint:
            return CacheEntryType.USER_INFO
        else:
            return CacheEntryType.WORKFLOW_RUNS  # Default

    def get_cached_response(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        allow_stale: Optional[bool] = None,
    ) -> Optional[Any]:
        """
        Get a cached response if available and valid.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            allow_stale: Whether to allow stale responses (overrides config)

        Returns:
            Cached response data or None if not available/valid
        """
        cache_key = self._generate_cache_key(endpoint, params)
        entry = self.cache.get(cache_key)

        if not entry:
            return None

        # Check if entry is expired
        if entry.is_expired():
            # Remove expired entry
            del self.cache[cache_key]
            return None

        # Check if we should allow stale responses
        allow_stale = (
            allow_stale
            if allow_stale is not None
            else self.config.allow_stale_responses
        )

        if entry.is_stale() and not allow_stale:
            return None

        # Record cache hit and return data
        entry.record_hit()
        return entry.data

    def cache_response(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]],
        response_data: Any,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Cache an API response.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            response_data: Response data to cache
            headers: HTTP response headers
        """
        cache_key = self._generate_cache_key(endpoint, params)
        entry_type = self._determine_entry_type(endpoint)

        # Calculate expiration time
        ttl_seconds = self.config.get_ttl_for_type(entry_type)
        created_at = datetime.now(timezone.utc)
        expires_at = created_at + timedelta(seconds=ttl_seconds)

        # Extract caching headers if available
        etag = headers.get("ETag") if headers else None
        last_modified = headers.get("Last-Modified") if headers else None

        # Create cache entry
        entry = CacheEntry(
            key=cache_key,
            data=response_data,
            entry_type=entry_type,
            created_at=created_at,
            expires_at=expires_at,
            etag=etag,
            last_modified=last_modified,
        )

        # Store in cache
        self.cache[cache_key] = entry

        # Enforce cache size limits
        self._enforce_cache_limits()

    def invalidate_cache(
        self,
        endpoint_pattern: Optional[str] = None,
        entry_type: Optional[CacheEntryType] = None,
    ) -> int:
        """
        Invalidate cache entries matching criteria.

        Args:
            endpoint_pattern: Pattern to match in cache keys
            entry_type: Type of entries to invalidate

        Returns:
            Number of entries invalidated
        """
        keys_to_remove = []

        for key, entry in self.cache.items():
            should_remove = False

            if endpoint_pattern and endpoint_pattern in key:
                should_remove = True

            if entry_type and entry.entry_type == entry_type:
                should_remove = True

            if endpoint_pattern is None and entry_type is None:
                should_remove = True  # Clear all if no criteria specified

            if should_remove:
                keys_to_remove.append(key)

        # Remove identified entries
        for key in keys_to_remove:
            del self.cache[key]

        return len(keys_to_remove)

    def update_rate_limit_info(self, headers: Dict[str, str]) -> None:
        """
        Update rate limit information from response headers.

        Args:
            headers: HTTP response headers
        """
        if any(header.startswith("X-RateLimit-") for header in headers):
            self.rate_limit_info = RateLimitInfo.from_headers(headers)

            # Cache the rate limit info
            self.cache_response(
                "/rate_limit",
                None,
                {
                    "limit": self.rate_limit_info.limit,
                    "remaining": self.rate_limit_info.remaining,
                    "reset_time": self.rate_limit_info.reset_time.isoformat(),
                    "used": self.rate_limit_info.used,
                },
                headers,
            )

    def should_throttle_request(self) -> bool:
        """
        Check if requests should be throttled due to rate limiting.

        Returns:
            True if requests should be throttled
        """
        if not self.rate_limit_info:
            return False

        return self.rate_limit_info.is_exhausted(self.config.rate_limit_threshold)

    def get_throttle_delay(self) -> float:
        """
        Get the delay needed before making the next request.

        Returns:
            Delay in seconds
        """
        if not self.rate_limit_info:
            return 0.0

        if self.rate_limit_info.is_exhausted():
            # Wait until rate limit resets
            time_until_reset = self.rate_limit_info.time_until_reset()
            return min(
                time_until_reset.total_seconds(), self.config.rate_limit_backoff_seconds
            )

        # Calculate delay to spread requests evenly
        requests_per_minute = self.rate_limit_info.requests_per_minute_available()
        if requests_per_minute > 0:
            return max(0.0, 60.0 / requests_per_minute - 1.0)

        return 0.0

    def record_request(self, endpoint: str) -> None:
        """
        Record that a request was made to an endpoint.

        Args:
            endpoint: API endpoint that was requested
        """
        now = datetime.now(timezone.utc)
        self.request_queue.append((endpoint, now))
        self.last_request_time = now

        # Keep only recent requests (last hour)
        cutoff_time = now - timedelta(hours=1)
        self.request_queue = [
            (ep, ts) for ep, ts in self.request_queue if ts > cutoff_time
        ]

    def get_request_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about API requests and caching.

        Returns:
            Dictionary with statistics
        """
        now = datetime.now(timezone.utc)

        # Calculate cache statistics
        total_entries = len(self.cache)
        expired_entries = sum(1 for entry in self.cache.values() if entry.is_expired())
        stale_entries = sum(1 for entry in self.cache.values() if entry.is_stale())
        total_hits = sum(entry.hit_count for entry in self.cache.values())

        # Calculate request statistics
        recent_requests = len(
            [req for req in self.request_queue if req[1] > now - timedelta(minutes=10)]
        )

        # Calculate cache hit ratio (approximate)
        cache_hit_ratio = 0.0
        if total_hits > 0 and recent_requests > 0:
            cache_hit_ratio = min(1.0, total_hits / (total_hits + recent_requests))

        stats = {
            "cache": {
                "total_entries": total_entries,
                "expired_entries": expired_entries,
                "stale_entries": stale_entries,
                "total_hits": total_hits,
                "hit_ratio": cache_hit_ratio,
            },
            "requests": {
                "recent_requests_10min": recent_requests,
                "total_requests_1hour": len(self.request_queue),
                "last_request_time": (
                    self.last_request_time.isoformat()
                    if self.last_request_time
                    else None
                ),
            },
            "rate_limit": {},
        }

        if self.rate_limit_info:
            stats["rate_limit"] = {
                "limit": self.rate_limit_info.limit,
                "remaining": self.rate_limit_info.remaining,
                "used": self.rate_limit_info.used,
                "reset_time": self.rate_limit_info.reset_time.isoformat(),
                "time_until_reset_seconds": self.rate_limit_info.time_until_reset().total_seconds(),
                "is_exhausted": self.rate_limit_info.is_exhausted(),
                "requests_per_minute_available": self.rate_limit_info.requests_per_minute_available(),
            }

        return stats

    def _enforce_cache_limits(self) -> None:
        """Enforce cache size limits by removing old entries."""
        if len(self.cache) <= self.config.max_entries:
            return

        # Sort entries by last access time (least recently used first)
        entries_by_age = sorted(
            self.cache.items(), key=lambda item: (item[1].hit_count, item[1].created_at)
        )

        # Remove oldest entries until we're under the limit
        entries_to_remove = len(self.cache) - self.config.max_entries
        for i in range(entries_to_remove):
            key, _ = entries_by_age[i]
            del self.cache[key]

    def cleanup_expired_entries(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)


def create_cache_manager(config: Optional[CacheConfig] = None) -> GitHubCacheManager:
    """
    Factory function to create a cache manager.

    Args:
        config: Optional cache configuration

    Returns:
        Configured GitHubCacheManager instance
    """
    return GitHubCacheManager(config)
