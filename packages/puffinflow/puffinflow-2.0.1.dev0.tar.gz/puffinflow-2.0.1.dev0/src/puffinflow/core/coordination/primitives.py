"""Coordination primitives for distributed systems."""

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum, auto
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


class PrimitiveType(Enum):
    """Coordination primitive types"""

    MUTEX = auto()  # Exclusive access
    SEMAPHORE = auto()  # Limited concurrent access
    BARRIER = auto()  # Synchronization point
    LEASE = auto()  # Time-based exclusive access
    LOCK = auto()  # Simple lock
    QUOTA = auto()  # Resource quota management


class ResourceState(Enum):
    """Resource states"""

    AVAILABLE = "available"
    ACQUIRED = "acquired"
    LOCKED = "locked"
    EXPIRED = "expired"
    ERROR = "error"


@dataclass
class CoordinationPrimitive:
    """Coordination primitive"""

    name: str
    type: PrimitiveType
    ttl: float = 30.0
    max_count: int = 1
    wait_timeout: Optional[float] = None
    quota_limit: Optional[float] = None

    # Internal state
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _condition: asyncio.Condition = field(default_factory=asyncio.Condition)
    _owners: set[str] = field(default_factory=set)
    _acquired_times: dict[str, float] = field(default_factory=dict)
    _quota_usage: dict[str, float] = field(default_factory=dict)
    _wait_count: int = 0
    _state: ResourceState = field(default=ResourceState.AVAILABLE)
    _last_error: Optional[str] = None

    async def acquire(
        self,
        caller_id: str,
        timeout: Optional[float] = None,
        quota_amount: Optional[float] = None,
    ) -> bool:
        """Acquire the primitive"""
        try:
            async with self._lock:
                # Handle quota type specially
                if self.type == PrimitiveType.QUOTA:
                    if quota_amount is None:
                        raise ValueError("Quota amount required")
                    current_usage = sum(self._quota_usage.values())
                    if current_usage + quota_amount <= (self.quota_limit or 0):
                        self._quota_usage[caller_id] = (
                            self._quota_usage.get(caller_id, 0) + quota_amount
                        )
                        return True
                    return False

                # Check existing ownership
                if caller_id in self._owners:
                    self._acquired_times[caller_id] = time.time()
                    return True

                # Handle different primitive types
                if self.type == PrimitiveType.MUTEX:
                    if not self._owners:
                        self._acquire_for(caller_id)
                        return True

                elif self.type == PrimitiveType.SEMAPHORE:
                    if len(self._owners) < self.max_count:
                        self._acquire_for(caller_id)
                        return True

                elif self.type == PrimitiveType.BARRIER:
                    # Unify the condition's lock with the primitive's lock on first use.
                    if not hasattr(self, "_barrier_lock_unified"):
                        self._condition = asyncio.Condition(self._lock)
                        self._barrier_lock_unified = True

                    self._acquire_for(caller_id)

                    if len(self._owners) < self.max_count:
                        # We must wait for other parties.
                        self._wait_count += 1
                        try:
                            # The `wait()` method will atomically release the lock and block until notified.
                            await asyncio.wait_for(
                                self._condition.wait(),
                                timeout=timeout or self.wait_timeout,
                            )
                            # Woke up successfully.
                            return True
                        except asyncio.TimeoutError:
                            # Timed out waiting for others.
                            self._remove_owner(caller_id)
                            return False
                        finally:
                            self._wait_count -= 1
                    else:
                        # We are the last party. Notify all waiters and proceed.
                        self._condition.notify_all()
                        return True

                elif self.type == PrimitiveType.LEASE:
                    self._cleanup_expired()
                    if not self._owners:
                        self._acquire_for(caller_id)
                        return True

                return False

        except Exception as e:
            self._state = ResourceState.ERROR
            self._last_error = str(e)
            raise

    def _acquire_for(self, caller_id: str) -> None:
        """Internal acquisition helper"""
        self._owners.add(caller_id)
        self._acquired_times[caller_id] = time.time()
        self._state = ResourceState.ACQUIRED

    def _remove_owner(self, caller_id: str) -> None:
        """Internal removal helper"""
        self._owners.discard(caller_id)
        self._acquired_times.pop(caller_id, None)
        self._quota_usage.pop(caller_id, None)
        if not self._owners:
            self._state = ResourceState.AVAILABLE

    def _cleanup_expired(self) -> None:
        """Clean up expired acquisitions"""
        now = time.time()
        expired = [
            owner
            for owner, acquired in self._acquired_times.items()
            if now - acquired > self.ttl
        ]
        for owner in expired:
            self._remove_owner(owner)

    async def release(self, caller_id: str) -> bool:
        """Release the primitive"""
        async with self._lock:
            # The acquire method for QUOTA does not add to _owners, so we handle its release separately.
            if self.type == PrimitiveType.QUOTA and caller_id in self._quota_usage:
                self._quota_usage.pop(caller_id)
                return True

            if caller_id in self._owners:
                self._remove_owner(caller_id)

                if self.type == PrimitiveType.BARRIER and self._wait_count > 0:
                    async with self._condition:
                        self._condition.notify_all()

                return True

            return False

    def get_state(self) -> dict[str, Any]:
        """Get current state information"""
        return {
            "state": self._state.value,
            "owners": list(self._owners),
            "wait_count": self._wait_count,
            "quota_usage": dict(self._quota_usage),
            "last_error": self._last_error,
            "ttl_remaining": (
                min(
                    (self.ttl - (time.time() - acquired))
                    for acquired in self._acquired_times.values()
                )
                if self._acquired_times
                else None
            ),
        }


# Specialized primitive implementations
class Mutex(CoordinationPrimitive):
    """Mutual exclusion lock"""

    def __init__(self, name: str, ttl: float = 30.0):
        super().__init__(name=name, type=PrimitiveType.MUTEX, ttl=ttl, max_count=1)

    async def __aenter__(self) -> "Mutex":
        """Async context manager support"""
        caller_id = str(uuid.uuid4())
        self._context_caller_id = caller_id
        await self.acquire(caller_id)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager support"""
        if hasattr(self, "_context_caller_id"):
            await self.release(self._context_caller_id)
            delattr(self, "_context_caller_id")


class Semaphore(CoordinationPrimitive):
    """Counting semaphore"""

    def __init__(self, name: str, max_count: int = 1, ttl: float = 30.0):
        super().__init__(
            name=name, type=PrimitiveType.SEMAPHORE, ttl=ttl, max_count=max_count
        )

    @property
    def available_permits(self) -> int:
        """Get number of available permits"""
        return self.max_count - len(self._owners)


class Barrier(CoordinationPrimitive):
    """Synchronization barrier"""

    def __init__(self, name: str, parties: int, timeout: Optional[float] = None):
        super().__init__(
            name=name,
            type=PrimitiveType.BARRIER,
            max_count=parties,
            wait_timeout=timeout,
        )
        self._parties = parties
        self._generation = 0
        self._condition = asyncio.Condition(self._lock)

    async def wait(self, caller_id: Optional[str] = None) -> int:
        """Wait at the barrier"""
        if caller_id is None:
            caller_id = str(uuid.uuid4())

        async with self._lock:
            generation = self._generation

            self._owners.add(caller_id)
            self._acquired_times[caller_id] = time.time()

            if len(self._owners) < self._parties:
                try:
                    await asyncio.wait_for(
                        self._condition.wait(),  # Releases lock
                        timeout=self.wait_timeout,
                    )
                    return generation
                except asyncio.TimeoutError:
                    self._owners.discard(caller_id)
                    # Notify others who might be waiting on a now-unreachable barrier
                    self._condition.notify_all()
                    raise
            else:
                # Last party: reset and notify
                self._generation += 1
                self._owners.clear()
                self._acquired_times.clear()
                self._condition.notify_all()
                return generation


class Lease(CoordinationPrimitive):
    """Time-based lease"""

    def __init__(
        self,
        name: str,
        ttl: float = 30.0,
        auto_renew: bool = False,
        renew_interval: float = 10.0,
    ):
        super().__init__(name=name, type=PrimitiveType.LEASE, ttl=ttl)
        self.auto_renew = auto_renew
        self.renew_interval = renew_interval
        self._renew_task: Optional[asyncio.Task] = None

    async def acquire(
        self,
        caller_id: str,
        timeout: Optional[float] = None,
        quota_amount: Optional[float] = None,
    ) -> bool:
        """Acquire lease with optional auto-renewal"""
        success = await super().acquire(caller_id, timeout, quota_amount)

        if success and self.auto_renew and not self._renew_task:
            self._renew_task = asyncio.create_task(self._auto_renew_loop(caller_id))

        return success

    async def release(self, caller_id: str) -> bool:
        """Release lease and cancel auto-renewal"""
        if self._renew_task:
            self._renew_task.cancel()
            await asyncio.gather(self._renew_task, return_exceptions=True)
            self._renew_task = None

        return await super().release(caller_id)

    async def _auto_renew_loop(self, caller_id: str) -> None:
        """Auto-renew lease periodically"""
        while True:
            try:
                await asyncio.sleep(self.renew_interval)

                async with self._lock:
                    if caller_id in self._owners:
                        self._acquired_times[caller_id] = time.time()
                        logger.debug(
                            "lease_renewed", lease=self.name, caller_id=caller_id
                        )
                    else:
                        break

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("lease_renew_error", lease=self.name, error=str(e))
                break


class Lock(CoordinationPrimitive):
    """Simple reentrant lock"""

    def __init__(self, name: str, ttl: float = 30.0):
        super().__init__(name=name, type=PrimitiveType.LOCK, ttl=ttl)
        self._lock_count: dict[str, int] = {}

    async def acquire(
        self,
        caller_id: str,
        timeout: Optional[float] = None,
        quota_amount: Optional[float] = None,
    ) -> bool:
        """Acquire lock with reentrancy support"""
        async with self._lock:
            # Check if already owned by caller (reentrant)
            if caller_id in self._owners:
                self._lock_count[caller_id] = self._lock_count.get(caller_id, 1) + 1
                return True

            # Try to acquire
            if not self._owners:
                self._acquire_for(caller_id)
                self._lock_count[caller_id] = 1
                return True

            return False

    async def release(self, caller_id: str) -> bool:
        """Release lock with reentrancy support"""
        async with self._lock:
            if caller_id not in self._owners:
                return False

            # Decrement lock count
            count = self._lock_count.get(caller_id, 1) - 1

            if count <= 0:
                # Fully release
                self._remove_owner(caller_id)
                self._lock_count.pop(caller_id, None)
                return True
            else:
                # Still locked
                self._lock_count[caller_id] = count
                return True


class Quota(CoordinationPrimitive):
    """Resource quota management"""

    def __init__(
        self, name: str, limit: float, reset_interval: Optional[timedelta] = None
    ):
        super().__init__(name=name, type=PrimitiveType.QUOTA, quota_limit=limit)
        self.reset_interval = reset_interval
        self._last_reset = time.time()
        self._reset_task: Optional[asyncio.Task] = None

    def _start_reset_task_if_needed(self) -> None:
        """Start the background reset task if configured and not already running."""
        if self.reset_interval and self._reset_task is None:
            self._reset_task = asyncio.create_task(self._reset_loop())

    async def consume(self, caller_id: str, amount: float) -> bool:
        """Consume quota amount"""
        self._start_reset_task_if_needed()
        return await self.acquire(caller_id, quota_amount=amount)

    async def release_quota(self, caller_id: str, amount: float) -> None:
        """Release quota (give back)"""
        self._start_reset_task_if_needed()
        async with self._lock:
            if caller_id in self._quota_usage and amount > 0:
                self._quota_usage[caller_id] = max(
                    0, self._quota_usage[caller_id] - amount
                )

    @property
    def available(self) -> float:
        """Get available quota"""
        used = sum(self._quota_usage.values())
        return max(0, (self.quota_limit or 0) - used)

    @property
    def usage(self) -> dict[str, float]:
        """Get current usage by caller"""
        return dict(self._quota_usage)

    async def reset(self) -> None:
        """Reset all quota usage"""
        self._start_reset_task_if_needed()
        async with self._lock:
            self._quota_usage.clear()
            self._last_reset = time.time()
            logger.info("quota_reset", quota=self.name)

    async def _reset_loop(self) -> None:
        """Periodic quota reset"""
        while True:
            try:
                if self.reset_interval:
                    await asyncio.sleep(self.reset_interval.total_seconds())
                    await self.reset()
                else:
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("quota_reset_error", quota=self.name, error=str(e))

    def __del__(self) -> None:
        """Cleanup reset task"""
        if self._reset_task and not self._reset_task.done():
            self._reset_task.cancel()


# Factory function
def create_primitive(
    primitive_type: PrimitiveType, name: str, **kwargs: Any
) -> CoordinationPrimitive:
    """Create a coordination primitive by type"""
    primitives = {
        PrimitiveType.MUTEX: Mutex,
        PrimitiveType.SEMAPHORE: Semaphore,
        PrimitiveType.BARRIER: Barrier,
        PrimitiveType.LEASE: Lease,
        PrimitiveType.LOCK: Lock,
        PrimitiveType.QUOTA: Quota,
    }

    primitive_class = primitives.get(primitive_type, CoordinationPrimitive)

    if primitive_class == CoordinationPrimitive:
        return CoordinationPrimitive(name=name, type=primitive_type, **kwargs)
    else:
        return primitive_class(name=name, **kwargs)  # type: ignore[no-any-return]
