"""Tests for the FixedVerificationRangesValidator.

This module tests the Fixed Verification Field Ranges validator that ensures
proper tab name formatting in verification ranges with single apostrophes.
"""

from unittest.mock import patch, MagicMock


from urarovite.validators import get_validator
from urarovite.validators.fixed_verification_ranges import (
    run,
    FixedVerificationRangesValidator,
)
from urarovite.core.spreadsheet import SpreadsheetMetadata


class TestFixedVerificationRangesValidator:
    """Test cases for FixedVerificationRangesValidator."""

    def test_validator_registration(self):
        """Test that the validator is properly registered."""
        validator = get_validator("fixed_verification_ranges")
        assert isinstance(validator, FixedVerificationRangesValidator)
        assert validator.id == "fixed_verification_ranges"
        assert validator.name == "Fixed Verification Field Ranges"
        assert "apostrophes" in validator.description

    def test_parse_range_entry_valid(self):
        """Test parsing of valid range entries."""
        validator = FixedVerificationRangesValidator()

        valid_entries = [
            "'FY2015_Present'!H2:H201",
            "'Grants'!A3:A143",
            "'Sale Price Import'!A3:I594",
            "'Transactions'!D2:D71",
        ]

        for entry in valid_entries:
            issue_type, fixed_entry, can_fix = validator._parse_range_entry(entry)
            assert issue_type == "valid", f"'{entry}' should be valid"
            assert fixed_entry == entry
            assert can_fix is True

    def test_parse_range_entry_missing_quotes_fixable(self):
        """Test parsing of entries with missing quotes (fixable)."""
        validator = FixedVerificationRangesValidator()

        test_cases = [
            ("Transactions!D2:D71", "'Transactions'!D2:D71"),
            ("Grants!A3:A143", "'Grants'!A3:A143"),
            ("FY2015_Present!H2:H201", "'FY2015_Present'!H2:H201"),
        ]

        for original, expected in test_cases:
            issue_type, fixed_entry, can_fix = validator._parse_range_entry(original)
            assert issue_type == "missing_quotes", (
                f"'{original}' should be missing_quotes"
            )
            assert fixed_entry == expected
            assert can_fix is True

    def test_parse_range_entry_missing_one_quote_fixable(self):
        """Test parsing of entries with one missing quote (fixable)."""
        validator = FixedVerificationRangesValidator()

        test_cases = [
            ("Transactions'!D2:D71", "'Transactions'!D2:D71"),
            ("'Grants!O3:O143", "'Grants'!O3:O143"),
            ("'FY2015_Present!H2", "'FY2015_Present'!H2"),
        ]

        for original, expected in test_cases:
            issue_type, fixed_entry, can_fix = validator._parse_range_entry(original)
            assert issue_type == "missing_one_quote", (
                f"'{original}' should be missing_one_quote"
            )
            assert fixed_entry == expected
            assert can_fix is True

    def test_parse_range_entry_no_tab_flag_only(self):
        """Test parsing of entries without tab names (flag only)."""
        validator = FixedVerificationRangesValidator()

        no_tab_entries = ["A1:K387", "H2:H201", "B5:C10", "A1"]

        for entry in no_tab_entries:
            issue_type, fixed_entry, can_fix = validator._parse_range_entry(entry)
            assert issue_type == "no_tab", f"'{entry}' should be no_tab"
            assert fixed_entry == entry
            assert can_fix is False

    def test_parse_range_entry_invalid_format_flag_only(self):
        """Test parsing of invalid format entries (flag only)."""
        validator = FixedVerificationRangesValidator()

        invalid_entries = [
            "'F61'",  # Single cell in quotes but no range
            "'B35'",
            "'I53'",
        ]

        for entry in invalid_entries:
            issue_type, fixed_entry, can_fix = validator._parse_range_entry(entry)
            assert issue_type == "invalid", f"'{entry}' should be invalid"
            assert fixed_entry == entry
            assert can_fix is False

    def test_split_range_entries(self):
        """Test splitting of comma-separated range entries."""
        validator = FixedVerificationRangesValidator()

        test_cases = [
            (
                "'Grants'!A3:A143, 'Grants'!O3:O143",
                ["'Grants'!A3:A143", "'Grants'!O3:O143"],
            ),
            (
                "'Sale Price Import'!A3:I594, 'Shipments'!A1:J62",
                ["'Sale Price Import'!A3:I594", "'Shipments'!A1:J62"],
            ),
            ("Transactions!D2:D71", ["Transactions!D2:D71"]),
            ("", []),
            ("   ", []),
        ]

        for ranges_str, expected in test_cases:
            result = validator._split_range_entries(ranges_str)
            assert result == expected, f"'{ranges_str}' should split to {expected}"

    def test_validator_flag_mode_with_mixed_issues(self):
        """Test validator in flag mode with mixed formatting issues."""
        validator = FixedVerificationRangesValidator()

        # Create mock spreadsheet data with mixed range formats
        data = [
            ["Fixed Verification Field Ranges"],  # Header
            ["'Grants'!A3:A143, Grants!O3:O143"],  # Mixed: one good, one fixable
            [
                "Transactions!D2:D71, 'Transactions'!E2:E71"
            ],  # Mixed: one fixable, one good
            ["A1:K387, 'FY2015'!B1:B10"],  # Mixed: one flag-only, one good
            ["'F61', 'B35'"],  # Flag-only: invalid formats
        ]

        # Mock the spreadsheet interface
        mock_spreadsheet = MagicMock()
        mock_metadata = SpreadsheetMetadata(
            spreadsheet_id="test_id",
            title="Test Sheet",
            sheet_names=["Sheet1"],
            spreadsheet_type="google_sheets",
        )
        mock_spreadsheet.get_metadata.return_value = mock_metadata
        mock_sheet_data = MagicMock()
        mock_sheet_data.values = data
        mock_spreadsheet.get_sheet_data.return_value = mock_sheet_data

        with patch.object(validator, "_get_spreadsheet", return_value=mock_spreadsheet):
            result = validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/test123/edit",
                mode="flag",
                auth_credentials={"auth_secret": "fake_creds"},
            )

        # Should find multiple issues
        assert result["flags_found"] > 0
        assert "flags" in result["details"]
        assert len(result["details"]["flags"]) > 0
        assert "formatting issues" in result["automated_log"]

    def test_validator_fix_mode_applies_fixes(self):
        """Test validator in fix mode applies fixes correctly."""
        validator = FixedVerificationRangesValidator()

        # Create mock spreadsheet data with fixable issues
        data = [
            ["Fixed Verification Field Ranges"],  # Header
            ["Transactions!D2:D71, 'Grants!O3:O143"],  # Both fixable
        ]

        # Mock the spreadsheet interface
        mock_spreadsheet = MagicMock()
        mock_metadata = SpreadsheetMetadata(
            spreadsheet_id="test_id",
            title="Test Sheet",
            sheet_names=["Sheet1"],
            spreadsheet_type="google_sheets",
        )
        mock_spreadsheet.get_metadata.return_value = mock_metadata
        mock_sheet_data = MagicMock()
        mock_sheet_data.values = data
        mock_spreadsheet.get_sheet_data.return_value = mock_sheet_data

        with patch.object(validator, "_get_spreadsheet", return_value=mock_spreadsheet):
            result = validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/test123/edit",
                mode="fix",
                auth_credentials={"auth_secret": "fake_creds"},
            )

        # Should apply fixes
        assert result["fixes_applied"] > 0
        assert "fixes" in result["details"]
        assert len(result["details"]["fixes"]) > 0

        # Verify the spreadsheet save method was called
        mock_spreadsheet.save.assert_called_once()

    def test_validator_no_issues_found(self):
        """Test validator with properly formatted ranges."""
        validator = FixedVerificationRangesValidator()

        # Create mock spreadsheet data with no issues
        data = [
            ["Fixed Verification Field Ranges"],  # Header
            ["'FY2015_Present'!H2:H201"],
            ["'Grants'!A3:A143, 'Grants'!O3:O143"],
            ["'Sale Price Import'!A3:I594"],
        ]

        # Mock the spreadsheet interface
        mock_spreadsheet = MagicMock()
        mock_metadata = SpreadsheetMetadata(
            spreadsheet_id="test_id",
            title="Test Sheet",
            sheet_names=["Sheet1"],
            spreadsheet_type="google_sheets",
        )
        mock_spreadsheet.get_metadata.return_value = mock_metadata
        mock_sheet_data = MagicMock()
        mock_sheet_data.values = data
        mock_spreadsheet.get_sheet_data.return_value = mock_sheet_data

        with patch.object(validator, "_get_spreadsheet", return_value=mock_spreadsheet):
            result = validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/test123/edit",
                mode="flag",
                auth_credentials={"auth_secret": "fake_creds"},
            )

        # Should find no issues
        assert result["flags_found"] == 0
        assert result["fixes_applied"] == 0
        assert "No tab name formatting issues found" in result["automated_log"]

    def test_validator_empty_sheet(self):
        """Test validator with empty sheet."""
        validator = FixedVerificationRangesValidator()

        # Mock empty spreadsheet
        mock_spreadsheet = MagicMock()
        mock_metadata = SpreadsheetMetadata(
            spreadsheet_id="test_id",
            title="Test Sheet",
            sheet_names=["Sheet1"],
            spreadsheet_type="google_sheets",
        )
        mock_spreadsheet.get_metadata.return_value = mock_metadata
        mock_sheet_data = MagicMock()
        mock_sheet_data.values = []
        mock_spreadsheet.get_sheet_data.return_value = mock_sheet_data

        with patch.object(validator, "_get_spreadsheet", return_value=mock_spreadsheet):
            result = validator.validate(
                spreadsheet_source="https://docs.google.com/spreadsheets/d/test123/edit",
                mode="flag",
                auth_credentials={"auth_secret": "fake_creds"},
            )

        assert result["flags_found"] == 0
        assert result["fixes_applied"] == 0


class TestBackwardCompatibility:
    """Test backward compatibility with the direct run function."""

    def test_run_function_with_valid_ranges(self):
        """Test the run() function with valid ranges."""
        ranges_str = "'FY2015_Present'!H2:H201, 'Grants'!A3:A143"
        result = run(ranges_str, mode="flag")

        assert result["flags_found"] == 0
        assert result["details"]["total_entries"] == 2
        assert result["details"]["original"] == ranges_str
        assert "No tab name formatting issues found" in result["automated_log"]

    def test_run_function_with_fixable_issues_flag_mode(self):
        """Test the run() function with fixable issues in flag mode."""
        ranges_str = "Transactions!D2:D71, 'Grants!O3:O143"
        result = run(ranges_str, mode="flag")

        assert result["flags_found"] == 2  # Both entries have issues
        assert result["details"]["total_entries"] == 2
        assert result["details"]["original"] == ranges_str
        assert "formatting issues" in result["automated_log"]

    def test_run_function_with_fixable_issues_fix_mode(self):
        """Test the run() function with fixable issues in fix mode."""
        ranges_str = "Transactions!D2:D71, 'Grants!O3:O143"
        result = run(ranges_str, mode="fix")

        assert result["fixes_applied"] == 2  # Both entries can be fixed
        assert result["details"]["total_entries"] == 2
        assert result["details"]["original"] == ranges_str
        assert "fixed_ranges" in result["details"]
        assert (
            "'Transactions'!D2:D71, 'Grants'!O3:O143"
            in result["details"]["fixed_ranges"]
        )

    def test_run_function_with_flag_only_issues(self):
        """Test the run() function with flag-only issues."""
        ranges_str = "A1:K387, 'F61'"
        result = run(ranges_str, mode="flag")

        assert result["flags_found"] == 2  # Both entries have issues
        assert result["details"]["total_entries"] == 2
        assert result["details"]["original"] == ranges_str

    def test_run_function_with_flag_only_issues_fix_mode(self):
        """Test the run() function with flag-only issues in fix mode."""
        ranges_str = "A1:K387, 'F61'"
        result = run(ranges_str, mode="fix")

        # These can't be fixed, so should be flagged instead
        assert result["fixes_applied"] == 0
        assert result["flags_found"] == 2
        assert result["details"]["total_entries"] == 2

    def test_run_function_with_empty_string(self):
        """Test the run() function with empty ranges string."""
        result = run("", mode="flag")

        assert result["flags_found"] == 0
        assert result["fixes_applied"] == 0
        assert result["details"]["total_entries"] == 0
        assert result["details"]["original"] == ""

    def test_run_function_error_handling(self):
        """Test the run() function error handling."""
        # Test with invalid input that might cause an exception
        result = run(None, mode="flag")

        assert result["flags_found"] == 0
        assert "errors" in result
        assert len(result["errors"]) > 0


class TestValidatorLogic:
    """Test specific validator logic components."""

    def test_edge_cases_parsing(self):
        """Test edge cases in range parsing."""
        validator = FixedVerificationRangesValidator()

        edge_cases = [
            ("", ("empty", "", False)),
            ("   ", ("empty", "", False)),
            ("'Sheet'!", ("unknown", "'Sheet'!", False)),  # Missing range part
            ("!'A1:B2", ("unknown", "!'A1:B2", False)),  # Missing sheet name
            (
                "Sheet!A1:B2:C3",
                ("unknown", "Sheet!A1:B2:C3", False),
            ),  # Invalid range format
        ]

        for entry, expected in edge_cases:
            result = validator._parse_range_entry(entry)
            assert result == expected, f"'{entry}' should result in {expected}"

    def test_complex_sheet_names(self):
        """Test parsing with complex sheet names."""
        validator = FixedVerificationRangesValidator()

        complex_cases = [
            ("'Sheet With Spaces'!A1:B2", ("valid", "'Sheet With Spaces'!A1:B2", True)),
            ("'Sheet-With-Dashes'!A1", ("valid", "'Sheet-With-Dashes'!A1", True)),
            (
                "'Sheet_With_Underscores'!A1:Z99",
                ("valid", "'Sheet_With_Underscores'!A1:Z99", True),
            ),
            (
                "Sheet With Spaces!A1:B2",
                ("missing_quotes", "'Sheet With Spaces'!A1:B2", True),
            ),
            (
                "'Sheet With Spaces!A1:B2",
                ("missing_one_quote", "'Sheet With Spaces'!A1:B2", True),
            ),
        ]

        for entry, expected in complex_cases:
            result = validator._parse_range_entry(entry)
            assert result == expected, f"'{entry}' should result in {expected}"

    def test_range_variations(self):
        """Test different range format variations."""
        validator = FixedVerificationRangesValidator()

        range_variations = [
            ("'Sheet'!A1", ("valid", "'Sheet'!A1", True)),  # Single cell
            ("'Sheet'!A1:B1", ("valid", "'Sheet'!A1:B1", True)),  # Single row
            ("'Sheet'!A1:A10", ("valid", "'Sheet'!A1:A10", True)),  # Single column
            ("'Sheet'!A1:Z999", ("valid", "'Sheet'!A1:Z999", True)),  # Large range
            (
                "Sheet!AA1:ZZ100",
                ("missing_quotes", "'Sheet'!AA1:ZZ100", True),
            ),  # Double letters
        ]

        for entry, expected in range_variations:
            result = validator._parse_range_entry(entry)
            assert result == expected, f"'{entry}' should result in {expected}"
