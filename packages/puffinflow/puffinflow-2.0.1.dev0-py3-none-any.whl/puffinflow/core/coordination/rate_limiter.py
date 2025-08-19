"""Rate limiting implementations."""

import asyncio
import math
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting strategies"""

    TOKEN_BUCKET = auto()
    LEAKY_BUCKET = auto()
    FIXED_WINDOW = auto()
    SLIDING_WINDOW = auto()


@dataclass
class RateLimiter:
    """Advanced rate limiter with multiple strategies"""

    max_rate: float
    burst_size: int = 1
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    window_size: float = 1.0  # For windowed strategies

    _tokens: float = field(init=False)
    _last_update: float = field(init=False)
    _window_requests: dict[float, int] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def __post_init__(self) -> None:
        self._tokens = self.burst_size
        self._last_update = time.time()

    async def acquire(self) -> bool:
        """Attempt to acquire rate limit token"""
        async with self._lock:
            now = time.time()

            if self.strategy == RateLimitStrategy.TOKEN_BUCKET:
                time_passed = now - self._last_update
                self._tokens = min(
                    self.burst_size, self._tokens + time_passed * self.max_rate
                )
                self._last_update = now

                if self._tokens >= 1:
                    self._tokens -= 1
                    return True

            elif self.strategy == RateLimitStrategy.LEAKY_BUCKET:
                # Clean old requests
                cutoff = now - self.window_size
                self._window_requests = {
                    ts: count
                    for ts, count in self._window_requests.items()
                    if ts > cutoff
                }

                # Check rate
                total_requests = sum(self._window_requests.values())
                if total_requests < self.max_rate:
                    self._window_requests[now] = self._window_requests.get(now, 0) + 1
                    return True

            elif self.strategy == RateLimitStrategy.FIXED_WINDOW:
                # Clean up old requests outside the relevant window to prevent
                # memory leaks
                cleanup_cutoff = now - (self.window_size * 2)
                self._window_requests = {
                    ts: count
                    for ts, count in self._window_requests.items()
                    if ts > cleanup_cutoff
                }

                window_start = math.floor(now / self.window_size) * self.window_size

                # Count requests in current window
                requests = sum(
                    count
                    for ts, count in self._window_requests.items()
                    if ts >= window_start
                )

                # For the base RateLimiter, max_rate represents requests per window
                if requests < self.max_rate:
                    self._window_requests[now] = self._window_requests.get(now, 0) + 1
                    return True

            elif self.strategy == RateLimitStrategy.SLIDING_WINDOW:
                # Clean up old requests outside the relevant window
                cleanup_cutoff = now - (self.window_size * 2)
                self._window_requests = {
                    ts: count
                    for ts, count in self._window_requests.items()
                    if ts > cleanup_cutoff
                }

                window_start = now - self.window_size

                # Count requests in sliding window
                requests = sum(
                    count
                    for ts, count in self._window_requests.items()
                    if ts >= window_start
                )

                if requests < self.max_rate:
                    self._window_requests[now] = 1
                    return True

            return False

    async def wait_for_token(self, timeout: Optional[float] = None) -> bool:
        """Wait for a token to become available"""
        start_time = time.time()

        while True:
            if await self.acquire():
                return True

            # Check timeout
            if timeout is not None and (time.time() - start_time) >= timeout:
                return False

            # Calculate wait time based on strategy
            wait_time = self._calculate_wait_time()

            if timeout is not None:
                remaining_timeout = timeout - (time.time() - start_time)
                if remaining_timeout <= 0:
                    return False
                wait_time = min(wait_time, remaining_timeout)

            if wait_time <= 0:
                # If no wait time, yield to event loop to prevent tight loop, then retry
                await asyncio.sleep(0.001)
                continue

            await asyncio.sleep(wait_time)

    def _calculate_wait_time(self) -> float:
        """Calculate how long to wait for next token"""
        now = time.time()

        if self.strategy == RateLimitStrategy.TOKEN_BUCKET:
            if self._tokens < 1:
                tokens_needed = 1 - self._tokens
                return max(0, tokens_needed / self.max_rate)

        elif self.strategy == RateLimitStrategy.FIXED_WINDOW:
            current_window_start = math.floor(now / self.window_size) * self.window_size
            next_window_start = current_window_start + self.window_size
            time_to_wait = next_window_start - now
            # Return a non-negative wait time with a small buffer to ensure we are
            # in the next window
            return max(0, time_to_wait) + 0.001

        elif self.strategy == RateLimitStrategy.SLIDING_WINDOW:
            window_start = now - self.window_size
            relevant_requests_ts = [
                ts for ts in self._window_requests if ts >= window_start
            ]

            if len(relevant_requests_ts) >= self.max_rate:
                # To make space, we must wait for the oldest request to expire
                oldest_request_ts = min(relevant_requests_ts)
                time_to_wait = (oldest_request_ts + self.window_size) - now
                return max(0, time_to_wait) + 0.001

        # For Leaky Bucket or other cases, a small polling delay is the
        # simplest approach
        return 0.1

    def get_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics"""
        return {
            "strategy": self.strategy.name,
            "max_rate": self.max_rate,
            "burst_size": self.burst_size,
            "current_tokens": self._tokens if hasattr(self, "_tokens") else 0,
            "window_requests": len(self._window_requests),
        }


# Specialized rate limiter implementations
class TokenBucket(RateLimiter):
    """Token bucket rate limiter"""

    def __init__(
        self, rate: float, capacity: int, initial_tokens: Optional[float] = None
    ):
        super().__init__(
            max_rate=rate, burst_size=capacity, strategy=RateLimitStrategy.TOKEN_BUCKET
        )
        if initial_tokens is not None:
            self._tokens = initial_tokens

    @property
    def tokens(self) -> float:
        """Get current token count"""
        # Ensure tokens are up-to-date before returning
        now = time.time()
        time_passed = now - self._last_update
        self._tokens = min(self.burst_size, self._tokens + time_passed * self.max_rate)
        self._last_update = now
        return self._tokens

    @property
    def capacity(self) -> int:
        """Get bucket capacity"""
        return self.burst_size

    async def consume(self, tokens: int = 1) -> bool:
        """Consume multiple tokens at once"""
        async with self._lock:
            # Update tokens first, but don't use the property to avoid extra
            # regeneration
            now = time.time()
            time_passed = now - self._last_update
            self._tokens = min(
                self.burst_size, self._tokens + time_passed * self.max_rate
            )
            self._last_update = now

            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False


class LeakyBucket(RateLimiter):
    """Leaky bucket rate limiter"""

    def __init__(self, rate: float, capacity: int):
        super().__init__(
            max_rate=rate, burst_size=capacity, strategy=RateLimitStrategy.LEAKY_BUCKET
        )
        self._bucket: deque = deque(maxlen=capacity)
        self._last_leak = time.time()

    async def acquire(self) -> bool:
        """Add request to bucket"""
        async with self._lock:
            now = time.time()

            # Leak requests
            self._leak(now)

            # Check if bucket has space
            if len(self._bucket) < self.burst_size:
                self._bucket.append(now)
                return True

            return False

    def _leak(self, now: float) -> None:
        """Leak requests from bucket"""
        time_passed = now - self._last_leak
        leak_count = int(time_passed * self.max_rate)

        if leak_count > 0:
            # Remove leaked requests
            for _ in range(min(leak_count, len(self._bucket))):
                self._bucket.popleft()

            self._last_leak = now


class SlidingWindow(RateLimiter):
    """Sliding window rate limiter"""

    def __init__(self, rate: float, window_size: float = 60.0):
        super().__init__(
            max_rate=rate,
            strategy=RateLimitStrategy.SLIDING_WINDOW,
            window_size=window_size,
        )
        self._request_log: deque = deque()

    async def acquire(self) -> bool:
        """Check if request is allowed"""
        async with self._lock:
            now = time.time()
            window_start = now - self.window_size

            # Remove old requests
            while self._request_log and self._request_log[0] < window_start:
                self._request_log.popleft()

            # Check rate - max_rate is requests per window, not per second
            if len(self._request_log) < self.max_rate:
                self._request_log.append(now)
                return True

            return False

    @property
    def current_rate(self) -> float:
        """Get current request rate per second"""
        now = time.time()
        window_start = now - self.window_size

        # Count recent requests
        recent_count = sum(1 for t in self._request_log if t >= window_start)

        return recent_count / self.window_size


class FixedWindow(RateLimiter):
    """Fixed window rate limiter"""

    def __init__(self, rate: float, window_size: float = 60.0):
        super().__init__(
            max_rate=rate,
            strategy=RateLimitStrategy.FIXED_WINDOW,
            window_size=window_size,
        )
        self._window_counts: dict[int, int] = {}

    async def acquire(self) -> bool:
        """Check if request is allowed"""
        async with self._lock:
            now = time.time()
            window_id = int(now / self.window_size)

            # Get count for current window
            count = self._window_counts.get(window_id, 0)

            # max_rate is requests per window
            if count < self.max_rate:
                self._window_counts[window_id] = count + 1

                # Clean old windows
                cutoff_window = window_id - 2
                self._window_counts = {
                    w: c for w, c in self._window_counts.items() if w > cutoff_window
                }

                return True

            return False


class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts based on system load"""

    def __init__(
        self,
        base_rate: float,
        min_rate: float,
        max_rate: float,
        strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET,
    ):
        self.base_rate = base_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.strategy = strategy

        self._current_rate = base_rate
        self._limiter = self._create_limiter(base_rate)
        self._success_count = 0
        self._failure_count = 0
        self._last_adjustment = time.time()
        self._adjustment_interval = 10.0  # seconds
        self._lock = asyncio.Lock()

    def _create_limiter(self, rate: float) -> RateLimiter:
        """Create underlying rate limiter"""
        return RateLimiter(
            max_rate=rate,
            burst_size=int(rate * 2),  # Allow some burst
            strategy=self.strategy,
        )

    async def acquire(self) -> bool:
        """Acquire with adaptive rate"""
        # Check if we should adjust rate first
        now = time.time()
        should_adjust = False
        async with self._lock:
            if now - self._last_adjustment >= self._adjustment_interval:
                should_adjust = True

        if should_adjust:
            async with self._lock:
                # Double-check after acquiring lock
                if now - self._last_adjustment >= self._adjustment_interval:
                    await self._adjust_rate()
                    self._last_adjustment = now

        # Try to acquire
        success = await self._limiter.acquire()

        # Track success/failure
        async with self._lock:
            if success:
                self._success_count += 1
            else:
                self._failure_count += 1

        return success

    async def _adjust_rate(self) -> None:
        """Adjust rate based on success/failure ratio"""
        total = self._success_count + self._failure_count
        if total == 0:
            return

        success_ratio = self._success_count / total

        # Adjust rate based on success ratio
        if success_ratio > 0.95:
            # Very high success rate, can increase
            new_rate = min(self._current_rate * 1.1, self.max_rate)
        elif success_ratio > 0.8:
            # Good success rate, slight increase
            new_rate = min(self._current_rate * 1.05, self.max_rate)
        elif success_ratio < 0.5:
            # Low success rate, decrease significantly
            new_rate = max(self._current_rate * 0.8, self.min_rate)
        elif success_ratio < 0.7:
            # Moderate success rate, slight decrease
            new_rate = max(self._current_rate * 0.95, self.min_rate)
        else:
            # Keep current rate
            new_rate = self._current_rate

        if new_rate != self._current_rate:
            logger.info(
                "rate_adjusted",
                old_rate=self._current_rate,
                new_rate=new_rate,
                success_ratio=success_ratio,
            )

            self._current_rate = new_rate
            self._limiter = self._create_limiter(new_rate)

        # Reset counters
        self._success_count = 0
        self._failure_count = 0

    @property
    def current_rate(self) -> float:
        """Get current rate"""
        return self._current_rate

    def get_stats(self) -> dict[str, Any]:
        """Get adaptive limiter statistics"""
        return {
            "current_rate": self._current_rate,
            "base_rate": self.base_rate,
            "min_rate": self.min_rate,
            "max_rate": self.max_rate,
            "success_count": self._success_count,
            "failure_count": self._failure_count,
            "limiter_stats": self._limiter.get_stats(),
        }


# Composite rate limiter for multiple limits
class CompositeRateLimiter:
    """Combines multiple rate limiters"""

    def __init__(self, limiters: list[RateLimiter]):
        self.limiters = limiters

    async def acquire(self) -> bool:
        """Acquire from all limiters"""
        # For simplicity, try to acquire from all limiters
        # If any fails, the whole request fails
        # Note: This approach may consume tokens from some limiters even if others fail
        # A more sophisticated approach would require checking all first, then acquiring
        # TODO: Implement a more sophisticated acquisition strategy

        acquired_from = []
        for i, limiter in enumerate(self.limiters):
            if await limiter.acquire():
                acquired_from.append(i)
            else:
                # At least one limiter rejected the request
                return False
        return True

    async def wait_for_all(self, timeout: Optional[float] = None) -> bool:
        """Wait for all limiters to allow request"""
        start_time = time.time()

        while True:
            # Try to acquire from all limiters
            if await self.acquire():
                return True

            # Check timeout
            if timeout is not None and (time.time() - start_time) >= timeout:
                return False

            # Calculate the maximum wait time across all limiters
            # We need to wait for the slowest limiter
            max_wait_time = 0.0
            for limiter in self.limiters:
                wait_time = limiter._calculate_wait_time()
                max_wait_time = max(max_wait_time, wait_time)

            # Apply timeout constraint
            if timeout is not None:
                remaining_timeout = timeout - (time.time() - start_time)
                if remaining_timeout <= 0:
                    return False
                max_wait_time = min(max_wait_time, remaining_timeout)

            # Wait for the calculated time, or a small amount if no wait needed
            if max_wait_time <= 0:
                await asyncio.sleep(0.001)
            else:
                await asyncio.sleep(max_wait_time)
