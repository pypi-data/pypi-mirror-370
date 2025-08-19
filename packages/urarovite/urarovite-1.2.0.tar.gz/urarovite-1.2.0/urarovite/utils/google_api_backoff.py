"""Exponential backoff utility for Google API calls.

This module provides a centralized exponential backoff implementation for
handling Google API rate limits and temporary failures with intelligent retry
logic.
"""

import logging
import random
import time
from functools import wraps
from typing import Any, Callable, Optional, Type, TypeVar

# Import progress utilities
try:
    from urarovite.utils.progress import show_backoff_status, BackoffStatus

    PROGRESS_AVAILABLE = True
except ImportError:
    PROGRESS_AVAILABLE = False

from typing import Union

try:
    from googleapiclient.errors import HttpError

    _HttpError = HttpError
except ImportError:
    try:
        from google.api_core.exceptions import GoogleAPIError as HttpError

        _HttpError = HttpError
    except ImportError:
        # Fallback - create a dummy class for type checking
        class _HttpError(Exception):
            def __init__(self, resp, content):
                self.resp = resp
                super().__init__(str(content))


try:
    from google.auth.exceptions import GoogleAuthError
except ImportError:
    GoogleAuthError = Exception

from requests.exceptions import ConnectionError, HTTPError, Timeout
import gspread

from urarovite.core.exceptions import AuthenticationError, SheetAccessError

# Type variables for generic function decoration
F = TypeVar("F", bound=Callable[..., Any])

logger = logging.getLogger(__name__)


class ExponentialBackoffConfig:
    """Configuration for exponential backoff behavior."""

    def __init__(
        self,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        multiplier: float = 2.0,
        max_retries: int = 5,
        jitter: bool = True,
        backoff_factor: float = 0.1,
    ):
        """Initialize exponential backoff configuration.

        Args:
            initial_delay: Initial delay in seconds before first retry
            max_delay: Maximum delay in seconds between retries
            multiplier: Multiplier for exponential backoff (default: 2.0)
            max_retries: Maximum number of retry attempts
            jitter: Whether to add random jitter to reduce thundering herd
            backoff_factor: Factor for jitter calculation (0.0-1.0)
        """
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.multiplier = multiplier
        self.max_retries = max_retries
        self.jitter = jitter
        self.backoff_factor = backoff_factor

        # Validate configuration
        if initial_delay < 0:
            raise ValueError("initial_delay must be non-negative")
        if max_delay < initial_delay:
            raise ValueError("max_delay must be >= initial_delay")
        if multiplier <= 1.0:
            raise ValueError("multiplier must be > 1.0")
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if not 0.0 <= backoff_factor <= 1.0:
            raise ValueError("backoff_factor must be between 0.0 and 1.0")


# Default configurations for different API operations
DEFAULT_CONFIG = ExponentialBackoffConfig()

# More aggressive retries for authentication operations
AUTH_CONFIG = ExponentialBackoffConfig(initial_delay=0.5, max_delay=30.0, max_retries=3)

# Conservative retries for write operations
WRITE_CONFIG = ExponentialBackoffConfig(
    initial_delay=3.0,  # Start with longer delay for writes
    max_delay=120.0,
    max_retries=3,
)

# More aggressive initial delay for read operations to handle rate limits better
READ_CONFIG = ExponentialBackoffConfig(
    initial_delay=2.5,  # Start with longer delay to avoid hitting rate limits
    max_delay=90.0,  # Increased max delay
    max_retries=6,  # More retries for rate limit scenarios
)


def _is_retryable_error(exception: Exception) -> bool:
    """Determine if an exception is retryable.

    Args:
        exception: The exception to check

    Returns:
        True if the exception indicates a retryable condition
    """
    # Google API HTTP errors that are retryable
    if isinstance(exception, _HttpError):
        status_code = getattr(exception.resp, "status", 0)
        # Rate limiting (429), server errors (5xx), and some 4xx errors
        retryable_codes = {429, 500, 502, 503, 504, 408, 409}
        return status_code in retryable_codes

    # gspread specific errors
    if isinstance(exception, gspread.exceptions.APIError):
        # gspread wraps HttpError, check the response
        if hasattr(exception, "response") and hasattr(
            exception.response, "status_code"
        ):
            status_code = exception.response.status_code
            retryable_codes = {429, 500, 502, 503, 504, 408, 409}
            return status_code in retryable_codes
        return True  # Default to retryable for gspread API errors

    # Connection and timeout errors
    if isinstance(exception, (ConnectionError, Timeout)):
        return True

    # Some HTTP errors
    if isinstance(exception, HTTPError):
        if hasattr(exception, "response") and hasattr(
            exception.response, "status_code"
        ):
            status_code = exception.response.status_code
            retryable_codes = {429, 500, 502, 503, 504, 408, 409}
            return status_code in retryable_codes
        return True  # Default to retryable for HTTP errors

    # Google Auth errors that might be temporary
    if isinstance(exception, GoogleAuthError):
        error_msg = str(exception).lower()
        # Temporary auth flags
        if any(
            keyword in error_msg
            for keyword in ["timeout", "connection", "temporary", "server error"]
        ):
            return True

    return False


def _calculate_delay(attempt: int, config: ExponentialBackoffConfig) -> float:
    """Calculate delay for the given retry attempt.

    Args:
        attempt: Current attempt number (0-based)
        config: Backoff configuration

    Returns:
        Delay in seconds before next retry
    """
    # Calculate exponential delay
    delay = config.initial_delay * (config.multiplier**attempt)

    # Cap at maximum delay
    delay = min(delay, config.max_delay)

    # Add jitter to prevent thundering herd
    if config.jitter:
        jitter_range = delay * config.backoff_factor
        jitter = random.uniform(-jitter_range, jitter_range)
        delay = max(0, delay + jitter)

    return delay


def _log_retry_attempt(
    attempt: int,
    exception: Exception,
    delay: float,
    function_name: str,
    max_retries: int = 0,
    operation_id: Optional[str] = None,
) -> None:
    """Log retry attempt information with visual progress indicators.

    Args:
        attempt: Current attempt number (1-based)
        exception: Exception that triggered the retry
        delay: Delay before next attempt
        function_name: Name of function being retried
        max_retries: Maximum number of retries
        operation_id: Unique operation identifier for progress tracking
    """
    # Standard logging
    logger.warning(
        f"Google API call failed (attempt {attempt}), retrying in {delay:.2f}s: "
        f"{function_name} - {type(exception).__name__}: {str(exception)}"
    )

    # Visual progress indication if available
    if PROGRESS_AVAILABLE and operation_id:
        status = BackoffStatus(
            operation=function_name,
            attempt=attempt,
            max_attempts=max_retries
            + 1,  # +1 because max_retries doesn't include first attempt
            delay=delay,
            error_type=f"{type(exception).__name__}: {str(exception)[:100]}...",
            is_retrying=True,
            total_elapsed=0.0,  # Will be calculated by progress manager
        )
        show_backoff_status(operation_id, status)


def with_exponential_backoff(
    config: Optional[ExponentialBackoffConfig] = None,
    reraise_as: Optional[Type[Exception]] = None,
    operation_id: Optional[str] = None,
) -> Callable[[F], F]:
    """Decorator to add exponential backoff to Google API calls.

    Args:
        config: Backoff configuration (uses DEFAULT_CONFIG if None)
        reraise_as: Exception type to reraise non-retryable errors as
        operation_id: Unique operation identifier for progress tracking

    Returns:
        Decorated function with exponential backoff

    Example:
        >>> @with_exponential_backoff(READ_CONFIG, operation_id="sheet_read")
        ... def get_sheet_data(service, sheet_id):
        ...     return service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    """
    if config is None:
        config = DEFAULT_CONFIG

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            # Generate operation ID if not provided
            op_id = operation_id or f"{func.__name__}_{id(func)}"

            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    # Check if this is the final attempt
                    if attempt >= config.max_retries:
                        break

                    # Check if error is retryable
                    if not _is_retryable_error(e):
                        break

                    # Calculate delay and wait
                    delay = _calculate_delay(attempt, config)
                    _log_retry_attempt(
                        attempt + 1, e, delay, func.__name__, config.max_retries, op_id
                    )
                    time.sleep(delay)

            # All retries exhausted or non-retryable error
            if reraise_as and not isinstance(last_exception, reraise_as):
                if isinstance(last_exception, _HttpError):
                    status_code = getattr(last_exception.resp, "status", 0)
                    if status_code in {403, 404}:
                        # Don't wrap permission/not found errors
                        raise last_exception

                # Wrap in specified exception type
                raise reraise_as(
                    f"Google API call failed after {config.max_retries} retries: {str(last_exception)}"
                )

            # Re-raise the original exception
            raise last_exception

        return wrapper

    return decorator


def execute_with_backoff(
    func: Callable[..., Any],
    *args,
    config: Optional[ExponentialBackoffConfig] = None,
    reraise_as: Optional[Type[Exception]] = None,
    operation_id: Optional[str] = None,
    **kwargs,
) -> Any:
    """Execute a function with exponential backoff without using decorator.

    Args:
        func: Function to execute with backoff
        *args: Positional arguments for the function
        config: Backoff configuration (uses DEFAULT_CONFIG if None)
        reraise_as: Exception type to reraise non-retryable errors as
        operation_id: Unique operation identifier for progress tracking
        **kwargs: Keyword arguments for the function

    Returns:
        Result of the function call

    Example:
        >>> result = execute_with_backoff(
        ...     service.spreadsheets().get,
        ...     spreadsheetId=sheet_id,
        ...     config=READ_CONFIG,
        ...     operation_id="get_sheet_metadata",
        ... ).execute()
    """
    if config is None:
        config = DEFAULT_CONFIG

    last_exception = None
    # Generate operation ID if not provided
    op_id = operation_id or f"{func.__name__}_{id(func)}"

    for attempt in range(config.max_retries + 1):
        try:
            return func(*args, **kwargs)

        except Exception as e:
            last_exception = e

            # Check if this is the final attempt
            if attempt >= config.max_retries:
                break

            # Check if error is retryable
            if not _is_retryable_error(e):
                break

            # Calculate delay and wait
            delay = _calculate_delay(attempt, config)
            _log_retry_attempt(
                attempt + 1, e, delay, func.__name__, config.max_retries, op_id
            )
            time.sleep(delay)

    # All retries exhausted or non-retryable error
    if reraise_as and not isinstance(last_exception, reraise_as):
        if isinstance(last_exception, _HttpError):
            status_code = getattr(last_exception.resp, "status", 0)
            if status_code in {403, 404}:
                # Don't wrap permission/not found errors
                raise last_exception

        # Wrap in specified exception type
        raise reraise_as(
            f"Google API call failed after {config.max_retries} retries: {str(last_exception)}"
        )

    # Re-raise the original exception
    raise last_exception


# Convenience decorators for common use cases
def with_auth_backoff(func: F) -> F:
    """Decorator for authentication operations with conservative backoff."""
    return with_exponential_backoff(AUTH_CONFIG, AuthenticationError)(func)


def with_read_backoff(func: F) -> F:
    """Decorator for read operations with standard backoff."""
    return with_exponential_backoff(READ_CONFIG, SheetAccessError)(func)


def with_write_backoff(func: F) -> F:
    """Decorator for write operations with conservative backoff."""
    return with_exponential_backoff(WRITE_CONFIG, SheetAccessError)(func)
