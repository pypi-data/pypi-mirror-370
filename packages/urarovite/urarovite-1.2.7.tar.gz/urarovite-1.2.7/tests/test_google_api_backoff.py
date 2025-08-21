"""Tests for the Google API exponential backoff utility."""

import time
from unittest.mock import Mock, patch
import pytest

from googleapiclient.errors import HttpError
from requests.exceptions import ConnectionError, Timeout
import gspread

from urarovite.utils.google_api_backoff import (
    ExponentialBackoffConfig,
    with_exponential_backoff,
    execute_with_backoff,
    with_auth_backoff,
    with_read_backoff,
    with_write_backoff,
    _is_retryable_error,
    _calculate_delay,
)
from urarovite.core.exceptions import AuthenticationError, SheetAccessError


class TestExponentialBackoffConfig:
    """Test exponential backoff configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ExponentialBackoffConfig()
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.multiplier == 2.0
        assert config.max_retries == 5
        assert config.jitter is True
        assert config.backoff_factor == 0.1

    def test_custom_config(self):
        """Test custom configuration values."""
        config = ExponentialBackoffConfig(
            initial_delay=2.0,
            max_delay=120.0,
            multiplier=3.0,
            max_retries=3,
            jitter=False,
            backoff_factor=0.2,
        )
        assert config.initial_delay == 2.0
        assert config.max_delay == 120.0
        assert config.multiplier == 3.0
        assert config.max_retries == 3
        assert config.jitter is False
        assert config.backoff_factor == 0.2

    def test_invalid_config_validation(self):
        """Test configuration validation."""
        with pytest.raises(ValueError, match="initial_delay must be non-negative"):
            ExponentialBackoffConfig(initial_delay=-1.0)

        with pytest.raises(ValueError, match="max_delay must be >= initial_delay"):
            ExponentialBackoffConfig(initial_delay=10.0, max_delay=5.0)

        with pytest.raises(ValueError, match="multiplier must be > 1.0"):
            ExponentialBackoffConfig(multiplier=1.0)

        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            ExponentialBackoffConfig(max_retries=-1)

        with pytest.raises(
            ValueError, match="backoff_factor must be between 0.0 and 1.0"
        ):
            ExponentialBackoffConfig(backoff_factor=1.5)


class TestRetryableErrors:
    """Test retryable error detection."""

    def test_http_error_retryable(self):
        """Test HttpError retryable status codes."""
        # Mock HttpError with retryable status codes
        for status_code in [429, 500, 502, 503, 504, 408, 409]:
            mock_response = Mock()
            mock_response.status = status_code
            error = HttpError(mock_response, b"error content")
            assert _is_retryable_error(error)

    def test_http_error_not_retryable(self):
        """Test HttpError non-retryable status codes."""
        for status_code in [400, 401, 403, 404]:
            mock_response = Mock()
            mock_response.status = status_code
            error = HttpError(mock_response, b"error content")
            assert not _is_retryable_error(error)

    def test_connection_errors_retryable(self):
        """Test connection errors are retryable."""
        assert _is_retryable_error(ConnectionError("Connection failed"))
        assert _is_retryable_error(Timeout("Request timed out"))

    def test_gspread_api_error_retryable(self):
        """Test gspread API errors are retryable."""
        mock_response = Mock()
        mock_response.status_code = 429
        error = gspread.exceptions.APIError(mock_response)
        assert _is_retryable_error(error)

    def test_non_retryable_errors(self):
        """Test non-retryable errors."""
        assert not _is_retryable_error(ValueError("Invalid value"))
        assert not _is_retryable_error(KeyError("Missing key"))


class TestDelayCalculation:
    """Test delay calculation logic."""

    def test_exponential_delay_calculation(self):
        """Test exponential delay calculation without jitter."""
        config = ExponentialBackoffConfig(
            initial_delay=1.0, multiplier=2.0, max_delay=60.0, jitter=False
        )

        # Test exponential growth
        assert _calculate_delay(0, config) == 1.0
        assert _calculate_delay(1, config) == 2.0
        assert _calculate_delay(2, config) == 4.0
        assert _calculate_delay(3, config) == 8.0

    def test_max_delay_cap(self):
        """Test delay is capped at max_delay."""
        config = ExponentialBackoffConfig(
            initial_delay=1.0, multiplier=2.0, max_delay=10.0, jitter=False
        )

        # Large attempt should be capped at max_delay
        assert _calculate_delay(10, config) == 10.0

    def test_jitter_adds_randomness(self):
        """Test jitter adds randomness to delay."""
        config = ExponentialBackoffConfig(
            initial_delay=10.0, multiplier=2.0, jitter=True, backoff_factor=0.1
        )

        # With jitter, delays should vary
        delays = [_calculate_delay(1, config) for _ in range(10)]
        assert len(set(delays)) > 1  # Should have some variation


class TestBackoffDecorator:
    """Test exponential backoff decorator."""

    @patch("urarovite.utils.google_api_backoff.time.sleep")
    def test_successful_call_no_retry(self, mock_sleep):
        """Test successful call requires no retry."""

        @with_exponential_backoff()
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"
        mock_sleep.assert_not_called()

    @patch("urarovite.utils.google_api_backoff.time.sleep")
    def test_retry_on_retryable_error(self, mock_sleep):
        """Test retry behavior on retryable errors."""
        config = ExponentialBackoffConfig(max_retries=2, initial_delay=0.1)
        call_count = 0

        @with_exponential_backoff(config)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                # Simulate retryable error
                mock_response = Mock()
                mock_response.status = 429
                raise HttpError(mock_response, b"rate limited")
            return "success after retries"

        result = failing_function()
        assert result == "success after retries"
        assert call_count == 3
        assert mock_sleep.call_count == 2  # 2 retries

    @patch("urarovite.utils.google_api_backoff.time.sleep")
    def test_no_retry_on_non_retryable_error(self, mock_sleep):
        """Test no retry on non-retryable errors."""

        @with_exponential_backoff()
        def failing_function():
            raise ValueError("Non-retryable error")

        with pytest.raises(ValueError):
            failing_function()

        mock_sleep.assert_not_called()

    @patch("urarovite.utils.google_api_backoff.time.sleep")
    def test_max_retries_exhausted(self, mock_sleep):
        """Test behavior when max retries are exhausted."""
        config = ExponentialBackoffConfig(max_retries=1, initial_delay=0.1)

        @with_exponential_backoff(config)
        def always_failing_function():
            mock_response = Mock()
            mock_response.status = 500
            raise HttpError(mock_response, b"server error")

        with pytest.raises(HttpError):
            always_failing_function()

        assert mock_sleep.call_count == 1  # Only 1 retry

    @patch("urarovite.utils.google_api_backoff.time.sleep")
    def test_reraise_as_custom_exception(self, mock_sleep):
        """Test reraising as custom exception type."""
        config = ExponentialBackoffConfig(max_retries=1, initial_delay=0.1)

        @with_exponential_backoff(config, reraise_as=AuthenticationError)
        def failing_function():
            mock_response = Mock()
            mock_response.status = 500
            raise HttpError(mock_response, b"server error")

        with pytest.raises(AuthenticationError):
            failing_function()


class TestExecuteWithBackoff:
    """Test execute_with_backoff function."""

    @patch("urarovite.utils.google_api_backoff.time.sleep")
    def test_execute_with_backoff_success(self, mock_sleep):
        """Test execute_with_backoff with successful call."""

        def successful_function(arg1, arg2, kwarg1=None):
            return f"{arg1}-{arg2}-{kwarg1}"

        result = execute_with_backoff(successful_function, "a", "b", kwarg1="c")
        assert result == "a-b-c"
        mock_sleep.assert_not_called()

    @patch("urarovite.utils.google_api_backoff.time.sleep")
    def test_execute_with_backoff_retry(self, mock_sleep):
        """Test execute_with_backoff with retries."""
        config = ExponentialBackoffConfig(max_retries=2, initial_delay=0.1)
        call_count = 0

        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Connection failed")
            return "success"

        result = execute_with_backoff(failing_function, config=config)
        assert result == "success"
        assert call_count == 3
        assert mock_sleep.call_count == 2


class TestConvenienceDecorators:
    """Test convenience decorators."""

    @patch("urarovite.utils.google_api_backoff.time.sleep")
    def test_with_auth_backoff(self, mock_sleep):
        """Test with_auth_backoff decorator."""

        @with_auth_backoff
        def auth_function():
            return "authenticated"

        result = auth_function()
        assert result == "authenticated"

    @patch("urarovite.utils.google_api_backoff.time.sleep")
    def test_with_read_backoff(self, mock_sleep):
        """Test with_read_backoff decorator."""

        @with_read_backoff
        def read_function():
            return "data"

        result = read_function()
        assert result == "data"

    @patch("urarovite.utils.google_api_backoff.time.sleep")
    def test_with_write_backoff(self, mock_sleep):
        """Test with_write_backoff decorator."""

        @with_write_backoff
        def write_function():
            return "written"

        result = write_function()
        assert result == "written"

    @patch("urarovite.utils.google_api_backoff.time.sleep")
    def test_auth_backoff_reraises_as_auth_error(self, mock_sleep):
        """Test auth backoff reraises as AuthenticationError."""
        ExponentialBackoffConfig(max_retries=1, initial_delay=0.1)

        @with_auth_backoff
        def failing_auth_function():
            raise ConnectionError("Connection failed")

        with pytest.raises(AuthenticationError):
            failing_auth_function()

    @patch("urarovite.utils.google_api_backoff.time.sleep")
    def test_read_backoff_reraises_as_sheet_error(self, mock_sleep):
        """Test read backoff reraises as SheetAccessError."""

        @with_read_backoff
        def failing_read_function():
            raise ConnectionError("Connection failed")

        with pytest.raises(SheetAccessError):
            failing_read_function()
