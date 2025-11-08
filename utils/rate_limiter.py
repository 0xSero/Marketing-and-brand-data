"""
Rate Limiting Utilities
Ensure ethical scraping with proper rate limiting.
"""

import time
from collections import deque
from typing import Optional


class RateLimiter:
    """
    Token bucket rate limiter for controlling request rates.
    """

    def __init__(self, requests_per_second: float = 0.5, burst_size: int = 5):
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Maximum requests per second
            burst_size: Maximum burst size
        """
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
        self.request_times = deque(maxlen=100)

    def wait_if_needed(self):
        """Wait if rate limit is exceeded"""
        current_time = time.time()

        # Refill tokens
        time_passed = current_time - self.last_update
        self.tokens = min(
            self.burst_size,
            self.tokens + time_passed * self.requests_per_second
        )
        self.last_update = current_time

        # Wait if no tokens available
        if self.tokens < 1:
            sleep_time = (1 - self.tokens) / self.requests_per_second
            time.sleep(sleep_time)
            self.tokens = 1

        # Consume a token
        self.tokens -= 1
        self.request_times.append(current_time)

    def get_current_rate(self) -> float:
        """Get current request rate"""
        if len(self.request_times) < 2:
            return 0.0

        time_span = self.request_times[-1] - self.request_times[0]
        if time_span == 0:
            return 0.0

        return len(self.request_times) / time_span


class AdaptiveRateLimiter(RateLimiter):
    """
    Rate limiter that adapts based on server responses.
    """

    def __init__(
        self,
        initial_rate: float = 0.5,
        min_rate: float = 0.1,
        max_rate: float = 2.0,
        burst_size: int = 5
    ):
        """
        Initialize adaptive rate limiter.

        Args:
            initial_rate: Starting requests per second
            min_rate: Minimum requests per second
            max_rate: Maximum requests per second
            burst_size: Maximum burst size
        """
        super().__init__(initial_rate, burst_size)
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.consecutive_successes = 0
        self.consecutive_failures = 0

    def report_success(self):
        """Report successful request"""
        self.consecutive_successes += 1
        self.consecutive_failures = 0

        # Gradually increase rate after multiple successes
        if self.consecutive_successes >= 10:
            self.requests_per_second = min(
                self.max_rate,
                self.requests_per_second * 1.1
            )
            self.consecutive_successes = 0

    def report_failure(self):
        """Report failed request (e.g., 429 Too Many Requests)"""
        self.consecutive_failures += 1
        self.consecutive_successes = 0

        # Immediately decrease rate on failure
        self.requests_per_second = max(
            self.min_rate,
            self.requests_per_second * 0.5
        )

    def report_rate_limit(self, retry_after: Optional[int] = None):
        """Report rate limit error"""
        if retry_after:
            time.sleep(retry_after)

        # Significantly decrease rate
        self.requests_per_second = max(
            self.min_rate,
            self.requests_per_second * 0.3
        )
        self.consecutive_failures = 0
        self.consecutive_successes = 0
