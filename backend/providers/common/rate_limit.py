import threading
import time
from collections.abc import Callable


class TokenBucketRateLimiter:
    """Thread-safe fixed-interval limiter shared by provider adapters."""

    def __init__(
        self,
        requests_per_minute: int,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        if requests_per_minute <= 0:
            raise ValueError("requests_per_minute must be positive")
        self.interval = 60.0 / requests_per_minute
        self.clock = clock
        self.sleeper = sleeper
        self._lock = threading.Lock()
        self._next_request_at = 0.0

    def acquire(self) -> None:
        with self._lock:
            now = self.clock()
            delay = max(0.0, self._next_request_at - now)
            if delay:
                self.sleeper(delay)
                now = self.clock()
            self._next_request_at = max(now, self._next_request_at) + self.interval
