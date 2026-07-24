"""Small in-memory rate limiter for a single API instance.

For horizontally scaled production deployments, replace this with a shared
Redis-backed limiter at the infrastructure layer.
"""

from collections import defaultdict, deque
from threading import Lock
from time import monotonic


class SlidingWindowRateLimiter:
    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> int:
        """Return retry-after seconds, or zero when the request is allowed."""
        now = monotonic()
        with self._lock:
            events = self._events[key]
            while events and now - events[0] >= window_seconds:
                events.popleft()
            if len(events) >= limit:
                return max(1, int(window_seconds - (now - events[0])) + 1)
            events.append(now)
            return 0


login_limiter = SlidingWindowRateLimiter()
