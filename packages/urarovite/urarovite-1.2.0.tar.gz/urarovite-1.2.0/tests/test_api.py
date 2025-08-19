"""Migrated API tests using centralized mocking utilities.

This is the migrated version of test_api.py that demonstrates the dramatic
reduction in boilerplate code and improved maintainability.
"""

import pytest
from urarovite.core.api import get_available_validation_criteria, execute_validation
from urarovite.core.exceptions import (
    AuthenticationError,
    ValidationError,
    SheetAccessError,
)
from .fixtures import BaseTestCase
from .mock_manager import mock_manager, with_validation_mocks


class TestGetAvailableValidationCriteria:
    """Test the get_available_validation_criteria function."""

    def test_returns_list_of_criteria(self):
        """Test that function returns a list of validation criteria."""
        result = get_available_validation_criteria()

        assert isinstance(result, list)
        assert len(result) > 0

        # Check structure of each criterion
        for criterion in result:
            assert isinstance(criterion, dict)
            assert "id" in criterion
            assert "name" in criterion
            assert isinstance(criterion["id"], str)
            assert isinstance(criterion["name"], str)

    def test_criteria_have_required_fields(self):
        """Test that all criteria have required id and name fields."""
        result = get_available_validation_criteria()

        for criterion in result:
            # Should have both id and name
            assert criterion["id"], f"Criterion missing id: {criterion}"
            assert criterion["name"], f"Criterion missing name: {criterion}"

            # ID should be suitable for programmatic use
            assert isinstance(criterion["id"], str)
            assert len(criterion["id"]) > 0

            # Name should be human-readable
            assert isinstance(criterion["name"], str)
            assert len(criterion["name"]) > 0


class TestExecuteValidation(BaseTestCase):
    """Test the updated execute_validation function using centralized mocking."""

    def setup_method(self):
        """Set up test fixtures using BaseTestCase."""
        super().setup_method()  # Gets encoded_creds, temp_dir automatically
        self.valid_sheet_url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
        self.valid_check = {"id": "empty_cells", "mode": "fix"}

    def test_missing_check(self):
        """Test error handling when no check is provided."""
        result = execute_validation(
            check=None, sheet_url=self.valid_sheet_url, auth_secret=self.encoded_creds
        )

        assert result["fixes_applied"] == 0
        assert result["flags_flagged"] == 0
        assert len(result["errors"]) == 1
        assert "No validation check specified" in result["errors"][0]
        assert "automated_logs" in result

    def test_empty_check(self):
        """Test error handling when empty check is provided."""
        result = execute_validation(
            check={}, sheet_url=self.valid_sheet_url, auth_secret=self.encoded_creds
        )

        assert result["fixes_applied"] == 0
        assert result["flags_flagged"] == 0
        assert len(result["errors"]) == 1
        assert "No validation check specified" in result["errors"][0]

    def test_check_missing_id_field(self):
        """Test error handling when check is missing 'id' field."""
        with mock_manager.validation_scenario():
            result = execute_validation(
                check={"mode": "fix"},  # Missing 'id' field
                sheet_url=self.valid_sheet_url,
                auth_secret=self.encoded_creds,
            )

            assert result["fixes_applied"] == 0
            assert result["flags_flagged"] == 0
            assert len(result["errors"]) == 1
            assert "Check missing required 'id' field" in result["errors"][0]

    def test_missing_sheet_url(self):
        """Test error handling when sheet URL is missing."""
        result = execute_validation(
            check=self.valid_check, sheet_url="", auth_secret=self.encoded_creds
        )

        assert result["fixes_applied"] == 0
        assert result["flags_flagged"] == 0
        assert len(result["errors"]) == 1
        assert (
            "Input source" in result["errors"][0]
            and "is required" in result["errors"][0]
        )

    def test_missing_auth_secret(self):
        """Test error handling when auth secret is missing for Google Sheets."""
        result = execute_validation(
            check=self.valid_check, sheet_url=self.valid_sheet_url, auth_secret=None
        )

        assert result["fixes_applied"] == 0
        assert result["flags_flagged"] == 0
        assert len(result["errors"]) == 1
        assert "Authentication credentials are required" in result["errors"][0]

    def test_invalid_sheet_url(self):
        """Test error handling for invalid sheet URL."""
        result = execute_validation(
            check=self.valid_check,
            sheet_url="https://invalid-url.com",
            auth_secret=self.encoded_creds,
        )

        assert result["fixes_applied"] == 0
        assert result["flags_flagged"] == 0
        assert len(result["errors"]) == 1
        assert "Invalid input source" in result["errors"][0]

    def test_invalid_mode(self):
        """Test error handling for invalid validation mode."""
        with mock_manager.validation_scenario():
            invalid_check = {"id": "empty_cells", "mode": "invalid_mode"}

            result = execute_validation(
                check=invalid_check,
                sheet_url=self.valid_sheet_url,
                auth_secret=self.encoded_creds,
            )

            assert result["fixes_applied"] == 0
            assert result["flags_flagged"] == 0
            assert len(result["errors"]) == 1
            assert "Invalid mode 'invalid_mode'" in result["errors"][0]

    def test_default_mode_is_flag(self):
        """Test that default mode is 'flag' when not specified."""
        check_without_mode = {"id": "empty_cells"}

        with mock_manager.validation_scenario(
            {"empty_cells": {"fixes_applied": 0, "flags_found": 2}}
        ):
            result = execute_validation(
                check=check_without_mode,
                sheet_url=self.valid_sheet_url,
                auth_secret=self.encoded_creds,
            )

            # Should use flag mode by default
            assert result["fixes_applied"] == 0
            assert result["flags_flagged"] == 2

    def test_authentication_failure(self):
        """Test handling of authentication failures."""
        with mock_manager.validation_scenario(auth_success=False):
            result = execute_validation(
                check=self.valid_check,
                sheet_url=self.valid_sheet_url,
                auth_secret=self.encoded_creds,
            )

            assert result["fixes_applied"] == 0
            assert result["flags_flagged"] == 0
            assert len(result["errors"]) == 1
            assert "Authentication failed: Auth failed" in result["errors"][0]

    def test_unknown_validation_check(self):
        """Test handling of unknown validation check IDs."""
        with mock_manager.validation_scenario():  # Empty registry
            unknown_check = {"id": "unknown_check", "mode": "fix"}

            result = execute_validation(
                check=unknown_check,
                sheet_url=self.valid_sheet_url,
                auth_secret=self.encoded_creds,
            )

            assert result["fixes_applied"] == 0
            assert result["flags_flagged"] == 0
            assert len(result["errors"]) == 1
            assert "Unknown validation check: 'unknown_check'" in result["errors"][0]

    def test_successful_fix_mode(self):
        """Test successful validation in fix mode."""
        with mock_manager.validation_scenario(
            {
                "empty_cells": {
                    "fixes_applied": 3,
                    "flags_found": 0,
                    "automated_log": "Fixed empty cells at positions: [(2, 1), (3, 2), (4, 1)]",
                }
            }
        ):
            result = execute_validation(
                check={"id": "empty_cells", "mode": "fix"},
                sheet_url=self.valid_sheet_url,
                auth_secret=self.encoded_creds,
            )

            assert result["fixes_applied"] == 3
            assert result["flags_flagged"] == 0
            assert result["errors"] == []
            assert "Fixed empty cells at positions" in result["automated_logs"]

    def test_successful_flag_mode(self):
        """Test successful validation in flag mode."""
        with mock_manager.validation_scenario(
            {
                "duplicate_rows": {
                    "fixes_applied": 0,
                    "flags_found": 7,
                    "automated_log": "Duplicate rows found at positions: [(5, 1), (6, 1)]",
                }
            }
        ):
            result = execute_validation(
                check={"id": "duplicate_rows", "mode": "flag"},
                sheet_url=self.valid_sheet_url,
                auth_secret=self.encoded_creds,
            )

            assert result["fixes_applied"] == 0
            assert result["flags_flagged"] == 7
            assert result["errors"] == []
            assert "Duplicate rows found" in result["automated_logs"]

    def test_no_flags_found(self):
        """Test when validation finds no flags."""
        with mock_manager.validation_scenario(
            {
                "empty_cells": {
                    "fixes_applied": 0,
                    "flags_found": 0,
                    "automated_log": "No flags found",
                }
            }
        ):
            result = execute_validation(
                check={"id": "empty_cells", "mode": "flag"},
                sheet_url=self.valid_sheet_url,
                auth_secret=self.encoded_creds,
            )

            assert result["fixes_applied"] == 0
            assert result["flags_flagged"] == 0
            assert result["errors"] == []
            assert "No flags found" in result["automated_logs"]

    def test_validator_errors_included(self):
        """Test that validator errors are included in results."""
        with mock_manager.validation_scenario(
            {
                "empty_cells": {
                    "fixes_applied": 1,
                    "flags_found": 0,
                    "errors": ["Warning: Could not fix row 5", "Sheet is protected"],
                }
            }
        ):
            result = execute_validation(
                check={"id": "empty_cells", "mode": "fix"},
                sheet_url=self.valid_sheet_url,
                auth_secret=self.encoded_creds,
            )

            assert result["fixes_applied"] == 1
            assert result["flags_flagged"] == 0
            assert len(result["errors"]) == 2
            assert "Warning: Could not fix row 5" in result["errors"]
            assert "Sheet is protected" in result["errors"]

    def test_subject_parameter_passed(self):
        """Test that subject parameter is passed to authentication."""
        with mock_manager.validation_scenario(
            {"empty_cells": {"fixes_applied": 2}}
        ) as mocks:
            result = execute_validation(
                check={"id": "empty_cells", "mode": "fix"},
                sheet_url=self.valid_sheet_url,
                auth_secret=self.encoded_creds,
                subject="user@example.com",
            )

            assert result["fixes_applied"] == 2
            # Verify subject was passed to authentication
            mocks["auth"].assert_called_with(self.encoded_creds, "user@example.com")

    def test_validation_error_handling(self):
        """Test handling of ValidationError exceptions."""
        with mock_manager.validation_scenario(
            {"empty_cells": {"fixes_applied": 0, "flags_found": 0}}
        ) as mocks:
            # Make validator raise ValidationError
            mocks["validators"]["empty_cells"].validate.side_effect = ValidationError(
                "Validation failed"
            )

            result = execute_validation(
                check=self.valid_check,
                sheet_url=self.valid_sheet_url,
                auth_secret=self.encoded_creds,
            )

            assert result["fixes_applied"] == 0
            assert result["flags_flagged"] == 0
            assert len(result["errors"]) == 1
            assert (
                "Validation error in check 'empty_cells': Validation failed"
                in result["errors"][0]
            )

    def test_unexpected_error_handling(self):
        """Test handling of unexpected exceptions."""
        with mock_manager.validation_scenario(
            {"empty_cells": {"fixes_applied": 0, "flags_found": 0}}
        ) as mocks:
            # Make validator raise unexpected error
            mocks["validators"]["empty_cells"].validate.side_effect = RuntimeError(
                "Unexpected error"
            )

            result = execute_validation(
                check=self.valid_check,
                sheet_url=self.valid_sheet_url,
                auth_secret=self.encoded_creds,
            )

            assert result["fixes_applied"] == 0
            assert result["flags_flagged"] == 0
            assert len(result["errors"]) == 1
            assert (
                "Unexpected error in check 'empty_cells': Unexpected error"
                in result["errors"][0]
            )

    def test_result_structure(self):
        """Test that result has the expected structure."""
        with mock_manager.validation_scenario(
            {"empty_cells": {"fixes_applied": 1, "flags_found": 0}}
        ):
            result = execute_validation(
                check=self.valid_check,
                sheet_url=self.valid_sheet_url,
                auth_secret=self.encoded_creds,
            )

            # Check all required fields are present
            required_fields = [
                "fixes_applied",
                "flags_flagged",
                "errors",
                "automated_logs",
            ]
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"

            # Check field types
            assert isinstance(result["fixes_applied"], int)
            assert isinstance(result["flags_flagged"], int)
            assert isinstance(result["errors"], list)
            assert isinstance(result["automated_logs"], str)


# Comparison of old vs new approach:

"""
OLD APPROACH (original test_api.py):
=====================================

@patch("urarovite.core.api._create_pre_validation_duplicate")
@patch("urarovite.core.api.create_sheets_service_from_encoded_creds")
@patch("urarovite.core.api.get_validator_registry")
def test_successful_fix_mode(self, mock_get_registry, mock_create_service, mock_create_duplicate):
    # Mock successful authentication
    mock_service = Mock()
    mock_create_service.return_value = mock_service

    # Mock successful duplicate creation
    mock_create_duplicate.return_value = {
        "success": True,
        "working_path": "https://docs.google.com/spreadsheets/d/duplicate123/edit",
        "output_path": "https://docs.google.com/spreadsheets/d/duplicate123/edit",
        "error": None
    }

    # Mock validator registry
    mock_validator = Mock()
    mock_validator.validate.return_value = {
        "fixes_applied": 3,
        "flags_found": 0,
        "errors": [],
        "details": {
            "fixed_cells": [(2, 1), (3, 2), (4, 1)]
        },
        "automated_log": "Fixed empty cells at positions: [(2, 1), (3, 2), (4, 1)]"
    }
    mock_registry = {"empty_cells": mock_validator}
    mock_get_registry.return_value = mock_registry

    result = execute_validation(
        check={"id": "empty_cells", "mode": "fix"},
        sheet_url=self.valid_sheet_url,
        auth_secret=self.encoded_creds,
    )

    assert result["fixes_applied"] == 3
    assert result["flags_flagged"] == 0
    assert result["errors"] == []
    assert "Fixed empty cells at positions" in result["automated_logs"]

LINES OF CODE: ~25 lines of setup + test logic


NEW APPROACH (this migrated file):
==================================

def test_successful_fix_mode(self):
    with mock_manager.validation_scenario({
        "empty_cells": {"fixes_applied": 3, "flags_found": 0, "automated_log": "Fixed empty cells at positions: [(2, 1), (3, 2), (4, 1)]"}
    }) as mocks:
        result = execute_validation(
            check={"id": "empty_cells", "mode": "fix"},
            sheet_url=self.valid_sheet_url,
            auth_secret=self.encoded_creds,
        )

        assert result["fixes_applied"] == 3
        assert result["flags_flagged"] == 0
        assert result["errors"] == []
        assert "Fixed empty cells at positions" in result["automated_logs"]

LINES OF CODE: ~12 lines total

REDUCTION: ~52% fewer lines, 100% more readable, 0% boilerplate
"""
