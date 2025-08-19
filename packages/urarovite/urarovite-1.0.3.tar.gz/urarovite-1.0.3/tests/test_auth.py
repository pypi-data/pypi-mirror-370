"""Tests for the new authentication module with gspread and base64 credentials."""

import base64
import json
import pytest
from unittest.mock import patch, Mock, MagicMock

from urarovite.auth.google_sheets import (
    decode_service_account,
    _create_gspread_client,
    get_gspread_client,
    create_sheets_service_from_encoded_creds,
    clear_client_cache,
)
from urarovite.core.exceptions import AuthenticationError


# Sample service account credentials for testing
SAMPLE_SERVICE_ACCOUNT = {
    "type": "service_account",
    "project_id": "test-project",
    "private_key_id": "key123",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
    "client_email": "test@test-project.iam.gserviceaccount.com",
    "client_id": "123456789",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
}


class TestDecodeServiceAccount:
    """Test the decode_service_account function."""

    def test_decode_valid_credentials(self):
        """Test decoding valid base64 encoded credentials."""
        # Encode the sample credentials
        encoded = base64.b64encode(json.dumps(SAMPLE_SERVICE_ACCOUNT).encode()).decode()

        # Decode and verify
        result = decode_service_account(encoded)
        assert result == SAMPLE_SERVICE_ACCOUNT
        assert result["type"] == "service_account"
        assert result["project_id"] == "test-project"

    def test_decode_invalid_base64(self):
        """Test error handling for invalid base64."""
        with pytest.raises(AuthenticationError) as exc_info:
            decode_service_account("invalid-base64!")
        assert "Failed to decode service account credentials" in str(exc_info.value)

    def test_decode_invalid_json(self):
        """Test error handling for invalid JSON after base64 decode."""
        invalid_json = base64.b64encode(b"not-json").decode()
        with pytest.raises(AuthenticationError) as exc_info:
            decode_service_account(invalid_json)
        assert "Failed to decode service account credentials" in str(exc_info.value)

    def test_decode_empty_string(self):
        """Test error handling for empty string."""
        with pytest.raises(AuthenticationError):
            decode_service_account("")


class TestCreateGspreadClient:
    """Test the _create_gspread_client function."""

    @patch("urarovite.auth.google_sheets.gspread.Client")
    @patch("urarovite.auth.google_sheets.ServiceAccountCredentials")
    def test_create_client_success(self, mock_creds_class, mock_client_class):
        """Test successful gspread client creation."""
        # Setup mocks
        mock_creds = Mock()
        mock_creds_class.from_service_account_info.return_value = mock_creds
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Encode credentials
        encoded = base64.b64encode(json.dumps(SAMPLE_SERVICE_ACCOUNT).encode()).decode()

        # Create client
        result = _create_gspread_client(encoded)

        # Verify calls
        mock_creds_class.from_service_account_info.assert_called_once()
        mock_client_class.assert_called_once_with(auth=mock_creds)
        assert result == mock_client

    @patch("urarovite.auth.google_sheets.gspread.Client")
    @patch("urarovite.auth.google_sheets.ServiceAccountCredentials")
    def test_create_client_with_subject(self, mock_creds_class, mock_client_class):
        """Test gspread client creation with subject delegation."""
        # Setup mocks
        mock_creds = Mock()
        mock_delegated_creds = Mock()
        mock_creds.with_subject.return_value = mock_delegated_creds
        mock_creds_class.from_service_account_info.return_value = mock_creds
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Encode credentials
        encoded = base64.b64encode(json.dumps(SAMPLE_SERVICE_ACCOUNT).encode()).decode()

        # Create client with subject
        result = _create_gspread_client(encoded, subject="user@example.com")

        # Verify delegation was attempted
        mock_creds.with_subject.assert_called_once_with("user@example.com")
        mock_client_class.assert_called_once_with(auth=mock_delegated_creds)
        assert result == mock_client

    @patch("urarovite.auth.google_sheets.gspread.Client")
    @patch("urarovite.auth.google_sheets.ServiceAccountCredentials")
    def test_create_client_delegation_fails(self, mock_creds_class, mock_client_class):
        """Test client creation when delegation fails but continues."""
        # Setup mocks
        mock_creds = Mock()
        mock_creds.with_subject.side_effect = Exception("Delegation failed")
        mock_creds_class.from_service_account_info.return_value = mock_creds
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Encode credentials
        encoded = base64.b64encode(json.dumps(SAMPLE_SERVICE_ACCOUNT).encode()).decode()

        # Create client - should continue despite delegation failure
        with patch("logging.warning") as mock_warning:
            result = _create_gspread_client(encoded, subject="user@example.com")

        # Verify warning was logged and original credentials used
        mock_warning.assert_called_once()
        mock_client_class.assert_called_once_with(auth=mock_creds)
        assert result == mock_client

    def test_create_client_invalid_credentials(self):
        """Test error handling for invalid credentials."""
        with pytest.raises(AuthenticationError) as exc_info:
            _create_gspread_client("invalid-base64!")
        assert "Failed to decode service account credentials" in str(exc_info.value)


class TestGetGspreadClient:
    """Test the get_gspread_client function with caching."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_client_cache()

    @patch("urarovite.auth.google_sheets._create_gspread_client")
    def test_get_client_first_call(self, mock_create):
        """Test first call creates and caches client."""
        mock_client = Mock()
        mock_create.return_value = mock_client

        encoded = base64.b64encode(json.dumps(SAMPLE_SERVICE_ACCOUNT).encode()).decode()

        result = get_gspread_client(encoded)

        mock_create.assert_called_once_with(encoded, None)
        assert result == mock_client

    @patch("urarovite.auth.google_sheets._create_gspread_client")
    def test_get_client_cached(self, mock_create):
        """Test second call uses cached client."""
        mock_client = Mock()
        mock_create.return_value = mock_client

        encoded = base64.b64encode(json.dumps(SAMPLE_SERVICE_ACCOUNT).encode()).decode()

        # First call
        result1 = get_gspread_client(encoded)
        # Second call
        result2 = get_gspread_client(encoded)

        # Should only create once
        mock_create.assert_called_once()
        assert result1 == result2 == mock_client

    @patch("urarovite.auth.google_sheets._create_gspread_client")
    def test_get_client_no_cache(self, mock_create):
        """Test bypassing cache when use_cache=False."""
        mock_client1 = Mock()
        mock_client2 = Mock()
        mock_create.side_effect = [mock_client1, mock_client2]

        encoded = base64.b64encode(json.dumps(SAMPLE_SERVICE_ACCOUNT).encode()).decode()

        # Two calls with use_cache=False
        result1 = get_gspread_client(encoded, use_cache=False)
        result2 = get_gspread_client(encoded, use_cache=False)

        # Should create twice
        assert mock_create.call_count == 2
        assert result1 == mock_client1
        assert result2 == mock_client2


class TestCreateSheetsServiceFromEncodedCreds:
    """Test the create_sheets_service_from_encoded_creds function."""

    @patch("urarovite.auth.google_sheets.build")
    @patch("urarovite.auth.google_sheets.ServiceAccountCredentials")
    def test_create_service_success(self, mock_creds_class, mock_build):
        """Test successful Google Sheets API service creation."""
        # Setup mocks
        mock_creds = Mock()
        mock_creds_class.from_service_account_info.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Encode credentials
        encoded = base64.b64encode(json.dumps(SAMPLE_SERVICE_ACCOUNT).encode()).decode()

        # Create service
        result = create_sheets_service_from_encoded_creds(encoded)

        # Verify calls
        mock_creds_class.from_service_account_info.assert_called_once()
        call_args = mock_creds_class.from_service_account_info.call_args
        assert call_args[1]["scopes"] == [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        mock_build.assert_called_once_with("sheets", "v4", credentials=mock_creds)
        assert result == mock_service

    @patch("urarovite.auth.google_sheets.build")
    @patch("urarovite.auth.google_sheets.ServiceAccountCredentials")
    def test_create_service_with_subject(self, mock_creds_class, mock_build):
        """Test service creation with subject delegation."""
        # Setup mocks
        mock_creds = Mock()
        mock_delegated_creds = Mock()
        mock_creds.with_subject.return_value = mock_delegated_creds
        mock_creds_class.from_service_account_info.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Encode credentials
        encoded = base64.b64encode(json.dumps(SAMPLE_SERVICE_ACCOUNT).encode()).decode()

        # Create service with subject
        result = create_sheets_service_from_encoded_creds(
            encoded, subject="user@example.com"
        )

        # Verify delegation
        mock_creds.with_subject.assert_called_once_with("user@example.com")
        mock_build.assert_called_once_with(
            "sheets", "v4", credentials=mock_delegated_creds
        )
        assert result == mock_service

    def test_create_service_invalid_credentials(self):
        """Test error handling for invalid credentials."""
        with pytest.raises(AuthenticationError) as exc_info:
            create_sheets_service_from_encoded_creds("invalid-base64!")
        assert "Failed to decode service account credentials" in str(exc_info.value)


class TestClearClientCache:
    """Test the clear_client_cache function."""

    @patch("urarovite.auth.google_sheets._create_gspread_client")
    def test_clear_cache(self, mock_create):
        """Test that clearing cache forces new client creation."""
        # Clear any existing cache first
        clear_client_cache()

        mock_client1 = Mock()
        mock_client2 = Mock()
        mock_create.side_effect = [mock_client1, mock_client2]

        encoded = base64.b64encode(json.dumps(SAMPLE_SERVICE_ACCOUNT).encode()).decode()

        # First call
        result1 = get_gspread_client(encoded)

        # Clear cache
        clear_client_cache()

        # Second call should create new client
        result2 = get_gspread_client(encoded)

        assert mock_create.call_count == 2
        assert result1 == mock_client1
        assert result2 == mock_client2
