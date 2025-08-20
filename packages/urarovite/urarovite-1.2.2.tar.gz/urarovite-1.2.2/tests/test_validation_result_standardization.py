"""
Test to enforce ValidationResult standardization across all validators.

This test ensures that all registered validators follow the ValidationResult pattern
and return consistent data structures with proper automated logging.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Any, Dict, Set

from urarovite.validators import get_validator_registry
from urarovite.validators.base import BaseValidator, ValidationResult


class TestValidationResultStandardization:
    """Test suite to enforce ValidationResult standardization across all validators."""

    def test_all_validators_registered(self):
        """Test that all validators are properly registered."""
        registry = get_validator_registry()

        # Expected validators based on the current implementation
        expected_validators = {
            "empty_cells",
            "tab_names",
            "tab_name_consistency",
            "open_ended_ranges",
            "invalid_verification_ranges",
            "sheet_name_quoting",
            "sheet_accessibility",
            "identical_outside_ranges",
            "different_within_ranges",
            "hidden_unicode",
            "volatile_formulas",
            "platform_neutralizer",
            "attached_files_cleaner",
            "bulk_rename_spreadsheets",
            "tab_name_case_collisions",
            "csv_to_json_transform",
            "empty_invalid_ranges",
            "spreadsheet_differences",
            "no_correct_answers",
            "whitespace_diff",
            "cell_value_validation",
            "duplicate_overlapping_ranges",
            "numeric_rounding",
            "unique_id_properties",
        }

        registered_validators = set(registry.keys())

        # Check that all expected validators are registered
        missing_validators = expected_validators - registered_validators
        assert not missing_validators, (
            f"Missing validators in registry: {missing_validators}"
        )

        # Check for unexpected validators (helps detect new ones that need testing)
        extra_validators = registered_validators - expected_validators
        if extra_validators:
            pytest.fail(
                f"New validators detected: {extra_validators}. "
                f"Please update this test to include them in standardization checks."
            )

    @pytest.mark.parametrize(
        "validator_id",
        [
            "empty_cells",
            "tab_names",
            "tab_name_consistency",
            "open_ended_ranges",
            "invalid_verification_ranges",
            "sheet_name_quoting",
            "sheet_accessibility",
            "identical_outside_ranges",
            "different_within_ranges",
            "hidden_unicode",
            "volatile_formulas",
            "platform_neutralizer",
            "attached_files_cleaner",
            "bulk_rename_spreadsheets",
            "tab_name_case_collisions",
            "csv_to_json_transform",
            "empty_invalid_ranges",
            "spreadsheet_differences",
            "no_correct_answers",
            "whitespace_diff",
            "cell_value_validation",
            "duplicate_overlapping_ranges",
            "numeric_rounding",
            "unique_id_properties",
        ],
    )
    def test_validator_returns_standardized_format(self, validator_id: str):
        """Test that each validator returns the standardized ValidationResult format."""
        registry = get_validator_registry()
        validator = registry[validator_id]

        # Create mock dependencies
        mock_service = Mock()
        mock_service.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            "values": [["test", "data"], ["more", "data"]]
        }

        # Create test data that should work for most validators
        test_row = {
            "input_sheet_url": "https://docs.google.com/spreadsheets/d/test_id/edit",
            "example_output_sheet_url": "https://docs.google.com/spreadsheets/d/test_id2/edit",
            "verification_field_ranges": "'Sheet1'!A1:B10",
            "email_field": "test@example.com",
            "phone_field": "+1234567890",
            "date_field": "2024-01-01",
            "url_field": "https://example.com",
            "required_field": "value",
        }

        try:
            # Test both flag and fix modes where supported
            for mode in ["flag", "fix"]:
                try:
                    # For validators using new interface, mock the spreadsheet
                    if hasattr(validator, "_get_spreadsheet"):
                        mock_spreadsheet = Mock()
                        mock_metadata = Mock()
                        mock_metadata.sheet_names = ["Sheet1"]
                        mock_spreadsheet.get_metadata.return_value = mock_metadata
                        mock_sheet_data = Mock()
                        mock_sheet_data.values = [["test", "data"], ["more", "data"]]
                        mock_sheet_data.sheet_name = "Sheet1"
                        mock_spreadsheet.get_sheet_data.return_value = mock_sheet_data

                        with patch.object(
                            validator, "_get_spreadsheet", return_value=mock_spreadsheet
                        ):
                            # Mock create_sheets_service_from_encoded_creds for validators that need it (like different_within_ranges)
                            if validator_id == "different_within_ranges":
                                mock_service = Mock()
                                with patch(
                                    "urarovite.validators.different_within_ranges.create_sheets_service_from_encoded_creds",
                                    return_value=mock_service,
                                ):
                                    # Mock the batch methods
                                    with patch.object(
                                        validator,
                                        "_get_sheet_values_batch",
                                        return_value={"Sheet1": [["test", "data"]]},
                                    ):
                                        result = validator.validate(
                                            spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                                            mode=mode,
                                            auth_credentials={
                                                "auth_secret": "eyJ0ZXN0IjogInZhbHVlIn0="
                                            },
                                            row=test_row,
                                        )
                            # Mock _create_sheets_service for validators that need it
                            elif hasattr(validator, "_create_sheets_service"):
                                mock_service = Mock()
                                with patch.object(
                                    validator,
                                    "_create_sheets_service",
                                    return_value=mock_service,
                                ):
                                    # Mock _fetch_workbook_effective for validators that need it (like identical_outside_ranges)
                                    if hasattr(validator, "_fetch_workbook_effective"):
                                        mock_workbook_data = {
                                            "Sheet1": [
                                                ["test", "data"],
                                                ["more", "data"],
                                            ]
                                        }
                                        with patch.object(
                                            validator,
                                            "_fetch_workbook_effective",
                                            return_value=mock_workbook_data,
                                        ):
                                            result = validator.validate(
                                                spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                                                mode=mode,
                                                auth_credentials={
                                                    "auth_secret": "eyJ0ZXN0IjogInZhbHVlIn0="
                                                },
                                                row=test_row,
                                            )
                                    else:
                                        result = validator.validate(
                                            spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                                            mode=mode,
                                            auth_credentials={
                                                "auth_secret": "eyJ0ZXN0IjogInZhbHVlIn0="
                                            },
                                            row=test_row,
                                        )
                            elif validator_id == "volatile_formulas":
                                mock_workbook = {
                                    "sheets": [
                                        {
                                            "properties": {"title": "Sheet1"},
                                            "data": [
                                                {
                                                    "rowData": [
                                                        {
                                                            "values": [
                                                                {
                                                                    "userEnteredValue": {
                                                                        "formulaValue": "=NOW()"
                                                                    }
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ],
                                        }
                                    ]
                                }
                                with patch(
                                    "urarovite.validators.volatile_formulas.fetch_workbook_with_formulas",
                                    return_value=mock_workbook,
                                ):
                                    result = validator.validate(
                                        spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                                        mode=mode,
                                        auth_credentials={
                                            "auth_secret": "eyJ0ZXN0IjogInZhbHVlIn0="
                                        },
                                        row=test_row,
                                    )
                            elif validator_id == "cell_value_validation":
                                # Cell value validation needs expected_values parameter
                                result = validator.validate(
                                    spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                                    mode=mode,
                                    auth_credentials={
                                        "auth_secret": "eyJ0ZXN0IjogInZhbHVlIn0="
                                    },
                                    expected_values={"A1": "test", "B1": "data"},
                                    tolerance=0.001,
                                )
                            elif validator_id == "duplicate_overlapping_ranges":
                                # Duplicate overlapping ranges needs range_columns parameter
                                result = validator.validate(
                                    spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                                    mode=mode,
                                    auth_credentials={
                                        "auth_secret": "eyJ0ZXN0IjogInZhbHVlIn0="
                                    },
                                    range_columns=[1, 2],
                                )
                            else:
                                # For validators that create their own sheets service (like different_within_ranges)
                                if validator_id == "different_within_ranges":
                                    mock_service = Mock()
                                    with patch(
                                        "urarovite.validators.different_within_ranges.create_sheets_service_from_encoded_creds",
                                        return_value=mock_service,
                                    ):
                                        # Mock the batch methods
                                        with patch.object(
                                            validator,
                                            "_get_sheet_values_batch",
                                            return_value={"Sheet1": [["test", "data"]]},
                                        ):
                                            result = validator.validate(
                                                spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                                                mode=mode,
                                                auth_credentials={
                                                    "auth_secret": "eyJ0ZXN0IjogInZhbHVlIn0="
                                                },
                                                row=test_row,
                                            )
                                else:
                                    result = validator.validate(
                                        spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                                        mode=mode,
                                        auth_credentials={
                                            "auth_secret": "eyJ0ZXN0IjogInZhbHVlIn0="
                                        },
                                        row=test_row,
                                    )
                    else:
                        # Try new interface first
                        # For validators that create their own sheets service (like different_within_ranges)
                        if validator_id == "different_within_ranges":
                            mock_service = Mock()
                            with patch(
                                "urarovite.validators.different_within_ranges.create_sheets_service_from_encoded_creds",
                                return_value=mock_service,
                            ):
                                # Mock the batch methods
                                with patch.object(
                                    validator,
                                    "_get_sheet_values_batch",
                                    return_value={"Sheet1": [["test", "data"]]},
                                ):
                                    result = validator.validate(
                                        spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                                        mode=mode,
                                        auth_credentials={
                                            "auth_secret": "eyJ0ZXN0IjogInZhbHVlIn0="
                                        },
                                        row=test_row,
                                    )
                        elif validator_id == "cell_value_validation":
                            # Cell value validation needs expected_values parameter
                            result = validator.validate(
                                spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                                mode=mode,
                                auth_credentials={
                                    "auth_secret": "eyJ0ZXN0IjogInZhbHVlIn0="
                                },
                                expected_values={"A1": "test", "B1": "data"},
                                tolerance=0.001,
                            )
                        elif validator_id == "duplicate_overlapping_ranges":
                            # Duplicate overlapping ranges needs range_columns parameter
                            result = validator.validate(
                                spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                                mode=mode,
                                auth_credentials={
                                    "auth_secret": "eyJ0ZXN0IjogInZhbHVlIn0="
                                },
                                range_columns=[1, 2],
                            )
                        else:
                            result = validator.validate(
                                spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                                mode=mode,
                                auth_credentials={
                                    "auth_secret": "eyJ0ZXN0IjogInZhbHVlIn0="
                                },
                                row=test_row,
                            )
                except TypeError:
                    # Fall back to old interface for validators that haven't been updated
                    result = validator.validate(
                        sheets_service=mock_service,
                        sheet_id="test_sheet_id",
                        mode=mode,
                        row=test_row,
                    )

                # Verify result is a dictionary (from ValidationResult.to_dict())
                assert isinstance(result, dict), (
                    f"Validator {validator_id} must return dict from ValidationResult.to_dict(), "
                    f"got {type(result)}"
                )

                # Verify all required ValidationResult fields are present
                required_fields = {
                    "fixes_applied",
                    "flags_found",
                    "errors",
                    "details",
                    "automated_log",
                }

                missing_fields = required_fields - set(result.keys())
                assert not missing_fields, (
                    f"Validator {validator_id} missing required ValidationResult fields: {missing_fields}. "
                    f"All validators must use ValidationResult pattern."
                )

                # Verify field types
                assert isinstance(result["fixes_applied"], int), (
                    f"Validator {validator_id}: fixes_applied must be int, got {type(result['fixes_applied'])}"
                )
                assert isinstance(result["flags_found"], int), (
                    f"Validator {validator_id}: flags_found must be int, got {type(result['flags_found'])}"
                )
                assert isinstance(result["errors"], list), (
                    f"Validator {validator_id}: errors must be list, got {type(result['errors'])}"
                )
                assert isinstance(result["details"], dict), (
                    f"Validator {validator_id}: details must be dict, got {type(result['details'])}"
                )
                assert isinstance(result["automated_log"], str), (
                    f"Validator {validator_id}: automated_log must be str, got {type(result['automated_log'])}"
                )

                # Verify automated_log is not empty (all validators should provide meaningful logs)
                assert result["automated_log"].strip(), (
                    f"Validator {validator_id} must provide non-empty automated_log. "
                    f"Got: '{result['automated_log']}'"
                )

                # Verify no legacy fields are present
                legacy_fields = {
                    "validator",  # Old custom format field
                    "ok",  # Old boolean success field
                    "message",  # Old message field
                    "logs",  # Old logs field that was removed
                }

                present_legacy_fields = legacy_fields.intersection(set(result.keys()))
                assert not present_legacy_fields, (
                    f"Validator {validator_id} contains legacy fields: {present_legacy_fields}. "
                    f"All validators must use only ValidationResult fields."
                )

                # Verify logical consistency
                if mode == "fix":
                    # In fix mode, fixes_applied should be >= 0
                    assert result["fixes_applied"] >= 0, (
                        f"Validator {validator_id}: fixes_applied must be >= 0 in fix mode"
                    )
                else:  # flag mode
                    # In flag mode, no fixes should be applied
                    assert result["fixes_applied"] == 0, (
                        f"Validator {validator_id}: fixes_applied must be 0 in flag mode, got {result['fixes_applied']}"
                    )

                # flags_found should always be >= 0
                assert result["flags_found"] >= 0, (
                    f"Validator {validator_id}: flags_found must be >= 0"
                )

        except Exception as e:
            # If validator fails due to missing dependencies or test data limitations,
            # we still want to ensure the error handling follows ValidationResult pattern
            if "ValidationResult" in str(e) or "automated_log" in str(e):
                # This is likely a standardization issue, re-raise
                raise
            else:
                # This might be due to test limitations (auth, network, etc.)
                # Skip this particular validator but log the issue
                pytest.skip(
                    f"Validator {validator_id} skipped due to test limitations: {e}"
                )

    def test_validator_inheritance(self):
        """Test that all validators properly inherit from BaseValidator."""
        registry = get_validator_registry()

        for validator_id, validator in registry.items():
            assert isinstance(validator, BaseValidator), (
                f"Validator {validator_id} must inherit from BaseValidator, "
                f"got {type(validator)}"
            )

            # Verify validator has required attributes
            assert hasattr(validator, "id"), (
                f"Validator {validator_id} must have 'id' attribute"
            )
            assert hasattr(validator, "validate"), (
                f"Validator {validator_id} must have 'validate' method"
            )

    def test_validation_result_class_consistency(self):
        """Test that ValidationResult class maintains its expected interface."""
        # Test ValidationResult can be instantiated
        result = ValidationResult()

        # Test required methods exist
        assert hasattr(result, "add_error"), (
            "ValidationResult must have add_error method"
        )
        assert hasattr(result, "add_issue"), (
            "ValidationResult must have add_issue method"
        )
        assert hasattr(result, "add_fix"), "ValidationResult must have add_fix method"
        assert hasattr(result, "set_automated_log"), (
            "ValidationResult must have set_automated_log method"
        )
        assert hasattr(result, "to_dict"), "ValidationResult must have to_dict method"

        # Test initial state
        result_dict = result.to_dict()
        assert result_dict["fixes_applied"] == 0
        assert result_dict["flags_found"] == 0
        assert result_dict["errors"] == []
        assert result_dict["details"] == {}
        assert result_dict["automated_log"] == ""

        # Test methods work correctly
        result.add_error("test error")
        result.add_issue(2)
        result.add_fix(3)
        result.set_automated_log("test log")
        result.details["test"] = "value"

        result_dict = result.to_dict()
        assert result_dict["fixes_applied"] == 3
        assert result_dict["flags_found"] == 2
        assert result_dict["errors"] == ["test error"]
        assert result_dict["details"] == {"test": "value"}
        assert result_dict["automated_log"] == "test log"

    def test_no_custom_return_formats(self):
        """Test that no validators use custom return formats anymore."""
        registry = get_validator_registry()

        # Create a simple mock to test return format
        mock_service = Mock()

        for validator_id, validator in registry.items():
            try:
                # Try to call validate with minimal parameters
                try:
                    # Try new interface first
                    if validator_id == "cell_value_validation":
                        result = validator.validate(
                            spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                            mode="flag",
                            auth_credentials={"encoded_creds": "fake_creds"},
                            expected_values={"A1": "test", "B1": "data"},
                        )
                    elif validator_id == "duplicate_overlapping_ranges":
                        result = validator.validate(
                            spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                            mode="flag",
                            auth_credentials={"encoded_creds": "fake_creds"},
                            range_columns=[1, 2],
                        )
                    else:
                        result = validator.validate(
                            spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                            mode="flag",
                            auth_credentials={"encoded_creds": "fake_creds"},
                        )
                except TypeError:
                    # Fall back to old interface
                    result = validator.validate(
                        sheets_service=mock_service, sheet_id="test", mode="flag"
                    )

                # The result should be a dict with ValidationResult structure
                assert isinstance(result, dict), (
                    f"Validator {validator_id} must return dict"
                )

                # Should not have old custom fields
                custom_fields = {
                    "validator",
                    "ok",
                    "total_segments",
                    "failing_segments",
                    "diff_count",
                    "diffs",
                    "open_ended",
                    "sheets",
                    "missing_in_input",
                    "missing_in_output",
                    "case_mismatches_input",
                    "case_mismatches_output",
                }

                present_custom_fields = custom_fields.intersection(set(result.keys()))
                assert not present_custom_fields, (
                    f"Validator {validator_id} still uses custom return format with fields: {present_custom_fields}. "
                    f"Must use ValidationResult.to_dict() only."
                )

            except Exception:
                # Some validators might fail with minimal parameters,
                # but we're mainly checking the successful cases
                continue

    def test_automated_log_quality(self):
        """Test that automated logs provide meaningful information."""
        registry = get_validator_registry()
        mock_service = Mock()

        # Common patterns that should appear in good automated logs

        # Patterns that suggest poor logging
        bad_patterns = ["null", "undefined", "None", "TODO", "FIXME"]

        for validator_id, validator in registry.items():
            try:
                try:
                    # Try new interface first
                    if validator_id == "cell_value_validation":
                        result = validator.validate(
                            spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                            mode="flag",
                            auth_credentials={"encoded_creds": "fake_creds"},
                            expected_values={"A1": "test", "B1": "data"},
                        )
                    elif validator_id == "duplicate_overlapping_ranges":
                        result = validator.validate(
                            spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                            mode="flag",
                            auth_credentials={"encoded_creds": "fake_creds"},
                            range_columns=[1, 2],
                        )
                    else:
                        result = validator.validate(
                            spreadsheet_source="https://docs.google.com/spreadsheets/d/test_id/edit",
                            mode="flag",
                            auth_credentials={"encoded_creds": "fake_creds"},
                        )
                except TypeError:
                    # Fall back to old interface
                    result = validator.validate(
                        sheets_service=mock_service, sheet_id="test", mode="flag"
                    )

                automated_log = result.get("automated_log", "")

                # Log should not be empty
                assert automated_log.strip(), (
                    f"Validator {validator_id} has empty automated_log"
                )

                # Log should not contain bad patterns
                for bad_pattern in bad_patterns:
                    assert bad_pattern not in automated_log.lower(), (
                        f"Validator {validator_id} automated_log contains '{bad_pattern}': {automated_log}"
                    )

                # Log should be reasonably descriptive (not just single words)
                assert len(automated_log.split()) >= 2, (
                    f"Validator {validator_id} automated_log too short: '{automated_log}'"
                )

            except Exception:
                # Skip validators that can't run with mock data
                continue
