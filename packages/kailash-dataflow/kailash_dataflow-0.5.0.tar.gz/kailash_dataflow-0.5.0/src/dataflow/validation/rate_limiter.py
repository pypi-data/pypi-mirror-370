"""DataFlow Rate Limiter Module."""

import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    max_requests: int = 100
    time_window_seconds: int = 60
    burst_limit: int = 150  # Allow short bursts
    burst_window_seconds: int = 10
    enabled: bool = True
    key_generator: Optional[str] = None  # Function to generate rate limit keys


from typing import Dict, Optional


class RateLimiter:
    """Rate limiter for DataFlow operations."""

    def __init__(self, max_requests: int = 100, time_window: int = 60):  # seconds
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, List[float]] = {}

    def is_allowed(self, key: str) -> bool:
        """Check if a request is allowed for the given key."""
        now = time.time()

        # Initialize if key doesn't exist
        if key not in self.requests:
            self.requests[key] = []

        # Remove old requests outside the time window
        cutoff_time = now - self.time_window
        self.requests[key] = [
            timestamp for timestamp in self.requests[key] if timestamp > cutoff_time
        ]

        # Check if under limit
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(now)
            return True

        return False

    def get_remaining(self, key: str) -> int:
        """Get remaining requests for the given key."""
        if key not in self.requests:
            return self.max_requests

        now = time.time()
        cutoff_time = now - self.time_window

        # Count requests within time window
        valid_requests = [
            timestamp for timestamp in self.requests[key] if timestamp > cutoff_time
        ]

        return max(0, self.max_requests - len(valid_requests))

    def get_reset_time(self, key: str) -> Optional[float]:
        """Get the time when the rate limit resets for the given key."""
        if key not in self.requests or not self.requests[key]:
            return None

        # Find the oldest request timestamp
        oldest_timestamp = min(self.requests[key])
        return oldest_timestamp + self.time_window

    def reset(self, key: Optional[str] = None):
        """Reset rate limit counters."""
        if key:
            if key in self.requests:
                del self.requests[key]
        else:
            self.requests.clear()


class TokenBucketRateLimiter:
    """Token bucket rate limiter for more flexible rate limiting."""

    def __init__(
        self, capacity: int = 100, refill_rate: float = 10.0  # tokens per second
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets: Dict[str, Dict[str, Any]] = {}

    def _get_bucket(self, key: str) -> Dict[str, Any]:
        """Get or create a token bucket for the key."""
        if key not in self.buckets:
            self.buckets[key] = {"tokens": self.capacity, "last_refill": time.time()}
        return self.buckets[key]

    def _refill_bucket(self, bucket: Dict[str, Any]):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - bucket["last_refill"]

        tokens_to_add = elapsed * self.refill_rate
        bucket["tokens"] = min(self.capacity, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now

    def consume(self, key: str, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket."""
        bucket = self._get_bucket(key)
        self._refill_bucket(bucket)

        if bucket["tokens"] >= tokens:
            bucket["tokens"] -= tokens
            return True

        return False

    def get_available_tokens(self, key: str) -> float:
        """Get the number of available tokens."""
        bucket = self._get_bucket(key)
        self._refill_bucket(bucket)
        return bucket["tokens"]


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""

    pass


class DataFlowRateLimiter:
    """Rate limiter for DataFlow operations."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    def check_limit(self, key: str) -> bool:
        """Check if request is within rate limit."""
        current_time = time.time()

        # Clean old requests
        if key in self.requests:
            self.requests[key] = [
                ts
                for ts in self.requests[key]
                if current_time - ts < self.window_seconds
            ]
        else:
            self.requests[key] = []

        # Check limit
        if len(self.requests[key]) >= self.max_requests:
            raise RateLimitExceeded(f"Rate limit exceeded for key: {key}")

        # Record request
        self.requests[key].append(current_time)
        return True

    def get_remaining(self, key: str) -> int:
        """Get remaining requests for key."""
        if key not in self.requests:
            return self.max_requests

        current_time = time.time()
        active_requests = [
            ts for ts in self.requests[key] if current_time - ts < self.window_seconds
        ]

        return max(0, self.max_requests - len(active_requests))
