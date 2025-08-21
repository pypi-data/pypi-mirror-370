"""
Simple retry strategy

Exponential backoff with maximum attempts.
Clear, predictable behavior.
"""

import asyncio
import logging
import random
from typing import Awaitable, Callable, TypeVar

from ..exceptions import AuthError, NetworkError, WeiboError

T = TypeVar("T")


class RetryStrategy:
    """Simple exponential backoff retry

    Responsibilities:
    - Execute functions with retry logic
    - Exponential backoff with jitter
    - Configurable retry conditions

    Does NOT handle:
    - Complex retry policies
    - Statistics tracking
    - Business logic
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        logger: logging.Logger | None = None,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self._logger = logger or logging.getLogger(__name__)

        # Exceptions that should trigger retry
        self._retryable_exceptions: tuple[type[Exception], ...] = (
            NetworkError,
            AuthError,
        )

    async def execute(self, func: Callable[[], Awaitable[T]]) -> T:
        """Execute function with retry logic"""
        last_exception: Exception | None = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                return await func()

            except Exception as e:
                last_exception = e

                # Don't retry non-retryable exceptions
                if not self._should_retry(e):
                    self._logger.debug(f"Not retrying {type(e).__name__}: {e}")
                    raise

                # Don't sleep after last attempt
                if attempt == self.max_attempts:
                    break

                # Calculate delay with exponential backoff and jitter
                delay = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
                # Add 20% jitter
                jitter = delay * 0.2 * random.random()
                final_delay = delay + jitter

                self._logger.warning(
                    f"Attempt {attempt}/{self.max_attempts} failed: {e}. "
                    f"Retrying in {final_delay:.1f}s..."
                )

                await asyncio.sleep(final_delay)

        # All attempts failed
        if last_exception:
            self._logger.error(f"All {self.max_attempts} attempts failed")
            raise last_exception

        # This shouldn't happen, but just in case
        raise RuntimeError("Retry logic error")

    def _should_retry(self, exception: Exception) -> bool:
        """Check if exception should trigger retry"""
        if isinstance(exception, self._retryable_exceptions):
            return True

        # Special case: some HTTP errors are retryable
        if isinstance(exception, NetworkError):
            if hasattr(exception, "status_code"):
                # Retry on temporary failures
                return exception.status_code in (429, 502, 503, 504)
            return True

        return False
