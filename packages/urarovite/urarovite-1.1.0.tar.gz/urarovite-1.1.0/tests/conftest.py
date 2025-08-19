"""Pytest configuration and shared fixtures for Urarovite tests.

This file is automatically loaded by pytest and provides shared fixtures
and configuration that can be used across all test files.
"""

import pytest
from unittest.mock import Mock, patch
from .fixtures import (
    MockPatches,
    create_mock_spreadsheet,
    create_mock_validator,
    create_mock_duplicate_result,
    mock_successful_auth,
    get_encoded_test_credentials,
)


@pytest.fixture(autouse=True)
def mock_pandas_import():
    """Auto-mock pandas import to prevent import errors in tests."""
    with patch.dict("sys.modules", {"pandas": Mock()}):
        yield


@pytest.fixture
def auto_mock_auth():
    """Automatically mock authentication for tests that need it."""
    with MockPatches.auth_service() as mock_auth:
        mock_auth.return_value = mock_successful_auth()
        yield mock_auth


@pytest.fixture
def auto_mock_validator_registry():
    """Automatically provide a mock validator registry."""
    with MockPatches.validator_registry() as mock_registry:
        # Default empty registry
        mock_registry.return_value = {}
        yield mock_registry


@pytest.fixture
def auto_mock_duplicate_creation():
    """Automatically mock duplicate creation."""
    with MockPatches.pre_validation_duplicate() as mock_duplicate:
        mock_duplicate.return_value = create_mock_duplicate_result()
        yield mock_duplicate


@pytest.fixture
def auto_mock_spreadsheet_factory():
    """Automatically mock spreadsheet factory."""
    with MockPatches.spreadsheet_factory() as mock_factory:
        # Default to returning properly mocked spreadsheets
        mock_factory.side_effect = lambda *args, **kwargs: create_mock_spreadsheet()
        yield mock_factory


# Marker for tests that need full validation mocking
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "needs_validation_mocks: mark test as needing validation mocks"
    )
    config.addinivalue_line(
        "markers", "needs_spreadsheet_mocks: mark test as needing spreadsheet mocks"
    )
    config.addinivalue_line("markers", "integration: mark test as integration test")


@pytest.fixture(autouse=True)
def auto_apply_mocks(request):
    """Automatically apply mocks based on test markers."""
    if request.node.get_closest_marker("needs_validation_mocks"):
        # Apply validation mocks
        with (
            MockPatches.auth_service() as mock_auth,
            MockPatches.validator_registry() as mock_registry,
            MockPatches.pre_validation_duplicate() as mock_duplicate,
        ):
            mock_auth.return_value = mock_successful_auth()
            mock_registry.return_value = {
                "empty_cells": create_mock_validator(fixes_applied=3)
            }
            mock_duplicate.return_value = create_mock_duplicate_result()
            yield
    elif request.node.get_closest_marker("needs_spreadsheet_mocks"):
        # Apply spreadsheet mocks
        with MockPatches.spreadsheet_factory() as mock_factory:
            mock_factory.side_effect = lambda *args, **kwargs: create_mock_spreadsheet()
            yield
    else:
        yield
