"""Retry utilities for TRC20 monitoring."""

import asyncio
import functools
import logging
from typing import Any, Callable, Optional, Type, Union


logger = logging.getLogger(__name__)


class ExponentialBackoff:
    """Exponential backoff strategy for retries."""

    def __init__(self, base_delay: float = 1.0, max_delay: float = 60.0, multiplier: float = 2.0):
        """Initialize exponential backoff.
        
        Args:
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            multiplier: Multiplier for each retry
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier

    def get_delay(self, attempt: int) -> float:
        """Get delay for the given attempt number."""
        delay = self.base_delay * (self.multiplier ** (attempt - 1))
        return min(delay, self.max_delay)


def with_retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff: Optional[ExponentialBackoff] = None,
    exceptions: Union[Type[Exception], tuple[Type[Exception], ...]] = Exception,
    on_retry: Optional[Callable[[int, Exception], None]] = None,
):
    """Decorator to add retry logic to async functions.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay_seconds: Initial delay between attempts (if no backoff strategy)
        backoff: Optional exponential backoff strategy
        exceptions: Exception types to retry on
        on_retry: Optional callback called on each retry
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        # Last attempt failed, re-raise the exception
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    # Calculate delay
                    if backoff:
                        delay = backoff.get_delay(attempt)
                    else:
                        delay = delay_seconds

                    logger.warning(
                        f"Function {func.__name__} failed on attempt {attempt}/{max_attempts}: {e}. "
                        f"Retrying in {delay}s..."
                    )

                    # Call retry callback if provided
                    if on_retry:
                        on_retry(attempt, e)

                    # Wait before next attempt
                    await asyncio.sleep(delay)

            # This should never be reached
            raise last_exception

        return wrapper

    return decorator


async def retry_async(
    coro_func: Callable,
    *args,
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff: Optional[ExponentialBackoff] = None,
    exceptions: Union[Type[Exception], tuple[Type[Exception], ...]] = Exception,
    on_retry: Optional[Callable[[int, Exception], None]] = None,
    **kwargs,
) -> Any:
    """Retry an async function call without using a decorator.
    
    Args:
        coro_func: Async function to retry
        max_attempts: Maximum number of retry attempts
        delay_seconds: Initial delay between attempts (if no backoff strategy)
        backoff: Optional exponential backoff strategy
        exceptions: Exception types to retry on
        on_retry: Optional callback called on each retry
        *args, **kwargs: Arguments to pass to the function
        
    Returns:
        Result of the function call
        
    Raises:
        The last exception if all retries fail
    """
    last_exception = None

    for attempt in range(1, max_attempts + 1):
        try:
            return await coro_func(*args, **kwargs)
        except exceptions as e:
            last_exception = e
            
            if attempt == max_attempts:
                # Last attempt failed, re-raise the exception
                logger.error(
                    f"Function {coro_func.__name__} failed after {max_attempts} attempts: {e}"
                )
                raise

            # Calculate delay
            if backoff:
                delay = backoff.get_delay(attempt)
            else:
                delay = delay_seconds

            logger.warning(
                f"Function {coro_func.__name__} failed on attempt {attempt}/{max_attempts}: {e}. "
                f"Retrying in {delay}s..."
            )

            # Call retry callback if provided
            if on_retry:
                on_retry(attempt, e)

            # Wait before next attempt
            await asyncio.sleep(delay)

    # This should never be reached
    raise last_exception