"""Centralized test fixtures and mocking utilities for Urarovite tests.

This module provides reusable mocks, fixtures, and decorators to reduce
code duplication across test files and ensure consistent mocking patterns.
"""

import base64
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any, Optional, List
import pytest


# Standard test service account credentials
SAMPLE_SERVICE_ACCOUNT = {
    "type": "service_account",
    "project_id": "test-project",
    "private_key_id": "key123",
    "private_key": "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----\n",
    "client_email": "test@test-project.iam.gserviceaccount.com",
    "client_id": "123456789",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test%40test-project.iam.gserviceaccount.com",
}


def get_encoded_test_credentials() -> str:
    """Get base64 encoded test service account credentials."""
    return base64.b64encode(json.dumps(SAMPLE_SERVICE_ACCOUNT).encode()).decode()


def create_mock_spreadsheet(**kwargs) -> Mock:
    """Create a properly mocked spreadsheet with context manager support.

    Args:
        **kwargs: Additional attributes to set on the mock

    Returns:
        Mock object with spreadsheet interface and context manager support
    """
    mock_spreadsheet = Mock()
    mock_spreadsheet.__enter__ = Mock(return_value=mock_spreadsheet)
    mock_spreadsheet.__exit__ = Mock(return_value=None)

    # Set default methods
    mock_spreadsheet.get_metadata = Mock()
    mock_spreadsheet.get_sheet_data = Mock()
    mock_spreadsheet.delete_sheet = Mock()
    mock_spreadsheet.create_sheet = Mock()
    mock_spreadsheet.update_sheet_data = Mock()
    mock_spreadsheet.save = Mock()

    # Apply any custom attributes
    for key, value in kwargs.items():
        setattr(mock_spreadsheet, key, value)

    return mock_spreadsheet


def create_mock_validator(
    fixes_applied: int = 0,
    flags_found: int = 0,
    errors: Optional[List[str]] = None,
    automated_log: str = "Test validation completed",
) -> Mock:
    """Create a mock validator with standard return values.

    Args:
        fixes_applied: Number of fixes applied
        flags_found: Number of flags found
        errors: List of error messages
        automated_log: Automated log message

    Returns:
        Mock validator object
    """
    mock_validator = Mock()
    mock_validator.validate.return_value = {
        "fixes_applied": fixes_applied,
        "flags_found": flags_found,
        "errors": errors or [],
        "automated_log": automated_log,
    }
    return mock_validator


def create_mock_duplicate_result(
    success: bool = True,
    working_path: str = "https://docs.google.com/spreadsheets/d/duplicate123/edit",
    output_path: str = "https://docs.google.com/spreadsheets/d/duplicate123/edit",
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a mock duplicate creation result.

    Args:
        success: Whether the duplication was successful
        working_path: Path to use for validation
        output_path: Final output path
        error: Error message if failed

    Returns:
        Dictionary with duplication result
    """
    return {
        "success": success,
        "working_path": working_path,
        "output_path": output_path,
        "error": error,
    }


class MockPatches:
    """Centralized patch decorators for common mocking patterns."""

    @staticmethod
    def auth_service():
        """Patch Google Sheets service creation."""
        return patch("urarovite.core.api.create_sheets_service_from_encoded_creds")

    @staticmethod
    def validator_registry():
        """Patch validator registry."""
        return patch("urarovite.core.api.get_validator_registry")

    @staticmethod
    def pre_validation_duplicate():
        """Patch pre-validation duplicate creation."""
        return patch("urarovite.core.api._create_pre_validation_duplicate")

    @staticmethod
    def spreadsheet_factory():
        """Patch spreadsheet factory."""
        return patch(
            "urarovite.utils.generic_spreadsheet.SpreadsheetFactory.create_spreadsheet"
        )

    @staticmethod
    def convert_spreadsheet_format():
        """Patch spreadsheet format conversion."""
        return patch("urarovite.utils.generic_spreadsheet.convert_spreadsheet_format")

    @staticmethod
    def drive_folder_duplicate():
        """Patch drive folder duplicate creation."""
        return patch("urarovite.core.api._create_drive_folder_duplicate")

    @staticmethod
    def drive_service():
        """Patch Google Drive service creation."""
        return patch(
            "urarovite.auth.google_drive.create_drive_service_from_encoded_creds"
        )

    @staticmethod
    def sheets_service():
        """Patch Google Sheets service creation."""
        return patch(
            "urarovite.auth.google_sheets.create_sheets_service_from_encoded_creds"
        )

    @staticmethod
    def duplicate_file_to_drive_folder():
        """Patch duplicate file to drive folder function."""
        return patch("urarovite.utils.drive.duplicate_file_to_drive_folder")


def mock_successful_auth():
    """Set up successful authentication mocks."""
    mock_service = Mock()
    return mock_service


def mock_validator_registry(validators: Dict[str, Mock]) -> Mock:
    """Create a mock validator registry.

    Args:
        validators: Dictionary of validator_id -> mock_validator

    Returns:
        Mock registry function
    """
    mock_registry = Mock()
    mock_registry.return_value = validators
    return mock_registry


@pytest.fixture
def temp_dir():
    """Provide a temporary directory that's cleaned up after the test."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    if temp_path.exists():
        import shutil

        shutil.rmtree(temp_path)


@pytest.fixture
def encoded_creds():
    """Provide encoded test credentials."""
    return get_encoded_test_credentials()


@pytest.fixture
def mock_auth_service():
    """Provide a mocked authentication service."""
    with MockPatches.auth_service() as mock:
        mock.return_value = mock_successful_auth()
        yield mock


@pytest.fixture
def mock_empty_validator():
    """Provide a mock validator for empty cells."""
    return create_mock_validator(
        fixes_applied=3, flags_found=0, automated_log="Fixed 3 empty cells"
    )


@pytest.fixture
def mock_duplicate_creation():
    """Provide a mock for successful duplicate creation."""
    with MockPatches.pre_validation_duplicate() as mock:
        mock.return_value = create_mock_duplicate_result()
        yield mock


class BaseTestCase:
    """Base test case with common setup and utilities."""

    def setup_method(self):
        """Set up common test fixtures."""
        self.encoded_creds = get_encoded_test_credentials()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        if hasattr(self, "temp_dir") and self.temp_dir.exists():
            import shutil

            shutil.rmtree(self.temp_dir)

    def create_mock_spreadsheet(self, **kwargs):
        """Convenience method to create mock spreadsheet."""
        return create_mock_spreadsheet(**kwargs)

    def create_mock_validator(self, **kwargs):
        """Convenience method to create mock validator."""
        return create_mock_validator(**kwargs)


# Decorator for common test patterns
def with_mocked_validation(
    validator_id: str = "empty_cells",
    fixes_applied: int = 3,
    flags_found: int = 0,
    duplicate_success: bool = True,
):
    """Decorator that sets up common validation mocking pattern.

    Args:
        validator_id: ID of the validator to mock
        fixes_applied: Number of fixes to return
        flags_found: Number of flags to return
        duplicate_success: Whether duplicate creation should succeed
    """

    def decorator(test_func):
        @MockPatches.auth_service()
        @MockPatches.validator_registry()
        @MockPatches.pre_validation_duplicate()
        def wrapper(self, mock_duplicate, mock_registry, mock_auth, *args, **kwargs):
            # Set up auth mock
            mock_auth.return_value = mock_successful_auth()

            # Set up validator mock
            mock_validator = create_mock_validator(
                fixes_applied=fixes_applied, flags_found=flags_found
            )
            mock_registry.return_value = {validator_id: mock_validator}

            # Set up duplicate mock
            mock_duplicate.return_value = create_mock_duplicate_result(
                success=duplicate_success
            )

            # Call the original test function
            return test_func(self, *args, **kwargs)

        return wrapper

    return decorator
