"""Tests for the TabNameCaseCollisionsValidator.

This module tests the tab name case collision validator that detects
tabs differing only by case and optionally fixes them by appending
numeric suffixes.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from urarovite.validators import get_validator
from urarovite.validators.tab_name_case_collisions import (
    TabNameCaseCollisionsValidator,
    detect_tab_case_collisions,
)


class TestTabNameCaseCollisionsValidator:
    """Test cases for TabNameCaseCollisionsValidator."""

    def test_validator_registration(self):
        """Test that the validator is properly registered."""
        validator = get_validator("tab_name_case_collisions")
        assert isinstance(validator, TabNameCaseCollisionsValidator)
        assert validator.id == "tab_name_case_collisions"
        assert validator.name == "Tab Name Case Collisions"
        assert "excel-insensitive" in validator.description.lower()

    def test_detect_case_collisions_no_collisions(self):
        """Test detection with no case collisions."""
        validator = TabNameCaseCollisionsValidator()

        tab_names = ["Sheet1", "Sheet2", "Data", "Summary"]
        collisions = validator._detect_case_collisions(tab_names)

        assert collisions == {}

    def test_detect_case_collisions_simple(self):
        """Test detection with simple case collisions."""
        validator = TabNameCaseCollisionsValidator()

        tab_names = ["Sheet1", "sheet1", "SHEET1"]
        collisions = validator._detect_case_collisions(tab_names)

        assert len(collisions) == 1
        assert "sheet1" in collisions
        assert set(collisions["sheet1"]) == {"Sheet1", "sheet1", "SHEET1"}

    def test_detect_case_collisions_multiple_groups(self):
        """Test detection with multiple collision groups."""
        validator = TabNameCaseCollisionsValidator()

        tab_names = ["Sheet1", "sheet1", "Data", "DATA", "Summary"]
        collisions = validator._detect_case_collisions(tab_names)

        assert len(collisions) == 2
        assert "sheet1" in collisions
        assert "data" in collisions
        assert set(collisions["sheet1"]) == {"Sheet1", "sheet1"}
        assert set(collisions["data"]) == {"Data", "DATA"}

    def test_generate_safe_name_no_collision(self):
        """Test safe name generation when no collision exists."""
        validator = TabNameCaseCollisionsValidator()

        existing = {"sheet1", "data"}
        safe_name = validator._generate_safe_name("Summary", existing)

        assert safe_name == "Summary"

    def test_generate_safe_name_with_collision(self):
        """Test safe name generation when collision exists."""
        validator = TabNameCaseCollisionsValidator()

        existing = {"sheet1", "data", "summary"}
        safe_name = validator._generate_safe_name("Summary", existing)

        assert safe_name == "Summary (2)"

    def test_generate_safe_name_multiple_collisions(self):
        """Test safe name generation with multiple existing suffixes."""
        validator = TabNameCaseCollisionsValidator()

        existing = {"summary", "summary (2)", "summary (3)"}
        safe_name = validator._generate_safe_name("Summary", existing)

        assert safe_name == "Summary (4)"

    def test_create_rename_mapping_simple(self):
        """Test rename mapping creation for simple collision."""
        validator = TabNameCaseCollisionsValidator()

        collisions = {"sheet1": ["Sheet1", "sheet1", "SHEET1"]}

        mapping = validator._create_rename_mapping(collisions)

        # First name should stay the same, others get suffixes
        assert mapping["Sheet1"] == "Sheet1"
        assert mapping["sheet1"] == "sheet1 (2)"
        assert mapping["SHEET1"] == "SHEET1 (3)"

    def test_create_rename_mapping_multiple_groups(self):
        """Test rename mapping creation for multiple collision groups."""
        validator = TabNameCaseCollisionsValidator()

        collisions = {"sheet1": ["Sheet1", "sheet1"], "data": ["Data", "DATA"]}

        mapping = validator._create_rename_mapping(collisions)

        # Check each group
        assert mapping["Sheet1"] == "Sheet1"
        assert mapping["sheet1"] == "sheet1 (2)"
        assert mapping["Data"] == "Data"
        assert mapping["DATA"] == "DATA (2)"

    @patch("urarovite.utils.generic_spreadsheet.get_spreadsheet_tabs")
    def test_validate_no_collisions_flag_mode(self, mock_get_tabs):
        """Test validator in flag mode with no collisions."""
        mock_get_tabs.return_value = {
            "accessible": True,
            "tabs": ["Sheet1", "Sheet2", "Data", "Summary"],
            "error": None,
        }

        validator = TabNameCaseCollisionsValidator()
        mock_service = Mock()

        # Mock the spreadsheet and sheets service creation
        with patch.object(validator, "_get_spreadsheet") as mock_get_spreadsheet:
            with patch.object(
                validator, "_create_sheets_service"
            ) as mock_create_service:
                mock_spreadsheet = MagicMock()
                mock_get_spreadsheet.return_value = mock_spreadsheet
                mock_create_service.return_value = mock_service

                result = validator.validate(
                    spreadsheet_source="https://docs.google.com/spreadsheets/d/test_sheet_id/edit",
                    mode="flag",
                    auth_credentials={
                        "auth_secret": "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogInRlc3QifQ=="
                    },
                )

        assert result["flags_found"] == 0
        assert result["fixes_applied"] == 0
        assert "flags" not in result["details"]
        assert "fixes" not in result["details"]
        assert result["automated_log"] == "No case collisions found"

    @patch("urarovite.utils.generic_spreadsheet.get_spreadsheet_tabs")
    def test_validate_with_collisions_flag_mode(self, mock_get_tabs):
        """Test validator in flag mode with collisions."""
        mock_get_tabs.return_value = {
            "accessible": True,
            "tabs": ["Sheet1", "sheet1", "Data", "DATA"],
            "error": None,
        }

        validator = TabNameCaseCollisionsValidator()
        mock_service = Mock()

        # Mock the spreadsheet and sheets service creation
        with patch.object(validator, "_get_spreadsheet") as mock_get_spreadsheet:
            with patch.object(
                validator, "_create_sheets_service"
            ) as mock_create_service:
                mock_spreadsheet = MagicMock()
                mock_get_spreadsheet.return_value = mock_spreadsheet
                mock_create_service.return_value = mock_service

                result = validator.validate(
                    spreadsheet_source="https://docs.google.com/spreadsheets/d/test_sheet_id/edit",
                    mode="flag",
                    auth_credentials={
                        "auth_secret": "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogInRlc3QifQ=="
                    },
                )

        assert result["flags_found"] == 4  # Two collision groups, two tabs each
        assert result["fixes_applied"] == 0
        assert "flags" in result["details"]
        assert len(result["details"]["flags"]) == 4
        assert "Found 4 tabs with case collisions." in result["automated_log"]

    @patch("urarovite.utils.generic_spreadsheet.rename_spreadsheet_sheet")
    @patch("urarovite.utils.generic_spreadsheet.get_spreadsheet_tabs")
    def test_validate_with_collisions_fix_mode(self, mock_get_tabs, mock_rename):
        """Test validator in fix mode with collisions."""
        mock_get_tabs.return_value = {
            "accessible": True,
            "tabs": ["Sheet1", "sheet1"],
            "error": None,
        }
        mock_rename.return_value = {"success": True, "error": None}

        # Mock the sheets API responses
        mock_service = Mock()
        mock_service.spreadsheets().get().execute.return_value = {
            "sheets": [
                {"properties": {"title": "Sheet1", "sheetId": 1}},
                {"properties": {"title": "sheet1", "sheetId": 2}},
            ]
        }
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}

        validator = TabNameCaseCollisionsValidator()

        # Mock the spreadsheet and sheets service creation
        with patch.object(validator, "_get_spreadsheet") as mock_get_spreadsheet:
            with patch.object(
                validator, "_create_sheets_service"
            ) as mock_create_service:
                mock_spreadsheet = MagicMock()
                mock_get_spreadsheet.return_value = mock_spreadsheet
                mock_create_service.return_value = mock_service

                result = validator.validate(
                    spreadsheet_source="https://docs.google.com/spreadsheets/d/test_sheet_id/edit",
                    mode="fix",
                    auth_credentials={
                        "auth_secret": "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogInRlc3QifQ=="
                    },
                )

        assert result["flags_found"] == 1  # Both tabs are flags
        assert result["fixes_applied"] == 1
        assert "fixes" in result["details"]
        assert len(result["details"]["fixes"]) == 1
        assert "Fixed 1 tab name case collisions." in result["automated_log"]

        # Verify that rename was called for the second tab
        mock_rename.assert_called_once_with(
            "https://docs.google.com/spreadsheets/d/test_sheet_id/edit",
            "sheet1",
            "sheet1 (2)",
            {
                "auth_secret": "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogInRlc3QifQ=="
            },
        )

    @patch("urarovite.utils.generic_spreadsheet.get_spreadsheet_tabs")
    def test_validate_inaccessible_sheet(self, mock_get_tabs):
        """Test validator with inaccessible sheet."""
        mock_get_tabs.return_value = {
            "accessible": False,
            "tabs": [],
            "error": "forbidden_or_not_found",
        }

        validator = TabNameCaseCollisionsValidator()
        mock_service = Mock()

        # Mock the spreadsheet and sheets service creation
        with patch.object(validator, "_get_spreadsheet") as mock_get_spreadsheet:
            with patch.object(
                validator, "_create_sheets_service"
            ) as mock_create_service:
                mock_spreadsheet = MagicMock()
                mock_get_spreadsheet.return_value = mock_spreadsheet
                mock_create_service.return_value = mock_service

                result = validator.validate(
                    spreadsheet_source="https://docs.google.com/spreadsheets/d/test_sheet_id/edit",
                    mode="flag",
                    auth_credentials={
                        "auth_secret": "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogInRlc3QifQ=="
                    },
                )

        assert len(result["errors"]) > 0
        assert "Unable to access spreadsheet" in result["errors"][0]
        assert result["automated_log"] == "Sheet access failed"

    @patch("urarovite.utils.generic_spreadsheet.rename_spreadsheet_sheet")
    @patch("urarovite.utils.generic_spreadsheet.get_spreadsheet_tabs")
    def test_validate_api_error_during_fix(self, mock_get_tabs, mock_rename):
        """Test validator when API error occurs during fix."""
        mock_get_tabs.return_value = {
            "accessible": True,
            "tabs": ["Sheet1", "sheet1"],
            "error": None,
        }
        mock_rename.return_value = {
            "success": False,
            "error": "API error during rename",
        }

        # Mock API error during batchUpdate
        mock_service = Mock()
        mock_service.spreadsheets().get().execute.return_value = {
            "sheets": [
                {"properties": {"title": "Sheet1", "sheetId": 1}},
                {"properties": {"title": "sheet1", "sheetId": 2}},
            ]
        }
        mock_service.spreadsheets().batchUpdate().execute.side_effect = Exception(
            "API Error"
        )

        validator = TabNameCaseCollisionsValidator()

        # Mock the spreadsheet and sheets service creation
        with patch.object(validator, "_get_spreadsheet") as mock_get_spreadsheet:
            with patch.object(
                validator, "_create_sheets_service"
            ) as mock_create_service:
                mock_spreadsheet = MagicMock()
                mock_get_spreadsheet.return_value = mock_spreadsheet
                mock_create_service.return_value = mock_service

                result = validator.validate(
                    spreadsheet_source="https://docs.google.com/spreadsheets/d/test_sheet_id/edit",
                    mode="fix",
                    auth_credentials={
                        "auth_secret": "eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogInRlc3QifQ=="
                    },
                )

        assert result["flags_found"] == 1
        assert result["fixes_applied"] == 1  # No fixes due to error
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert "API error during rename" in result["errors"][0]


class TestDetectTabCaseCollisionsFunction:
    """Test the standalone detect_tab_case_collisions function."""

    def test_no_collisions(self):
        """Test function with no collisions."""
        tab_names = ["Sheet1", "Sheet2", "Data"]
        result = detect_tab_case_collisions(tab_names)

        assert result["has_collisions"] is False
        assert result["collisions"] == {}
        assert result["suggested_mapping"] == {}
        assert result["tabs_affected"] == 0

    def test_with_collisions(self):
        """Test function with collisions."""
        tab_names = ["Sheet1", "sheet1", "SHEET1"]
        result = detect_tab_case_collisions(tab_names)

        assert result["has_collisions"] is True
        assert len(result["collisions"]) == 1
        assert result["tabs_affected"] == 3

        # Check mapping
        mapping = result["suggested_mapping"]
        assert mapping["Sheet1"] == "Sheet1"
        assert mapping["sheet1"] == "sheet1 (2)"
        assert mapping["SHEET1"] == "SHEET1 (3)"


class TestValidatorLogic:
    """Test specific validator logic components."""

    def test_collision_detection_case_sensitivity(self):
        """Test that collision detection is truly case-insensitive."""
        validator = TabNameCaseCollisionsValidator()

        # Mix of different cases
        tab_names = ["MySheet", "MYSHEET", "mysheet", "MyShEeT"]
        collisions = validator._detect_case_collisions(tab_names)

        assert len(collisions) == 1
        assert "mysheet" in collisions
        assert len(collisions["mysheet"]) == 4

    def test_collision_detection_with_spaces_and_special_chars(self):
        """Test collision detection with spaces and special characters."""
        validator = TabNameCaseCollisionsValidator()

        tab_names = ["My Sheet-1", "MY SHEET-1", "my sheet-1"]
        collisions = validator._detect_case_collisions(tab_names)

        assert len(collisions) == 1
        assert "my sheet-1" in collisions
        assert len(collisions["my sheet-1"]) == 3

    def test_safe_name_generation_with_existing_suffixes(self):
        """Test safe name generation when numbered suffixes already exist."""
        validator = TabNameCaseCollisionsValidator()

        # Simulate existing names with some suffixes already used
        existing = {"sheet1", "sheet1 (2)", "sheet1 (3)", "sheet1 (5)"}
        safe_name = validator._generate_safe_name("Sheet1", existing)

        # Should find the next available number
        assert safe_name == "Sheet1 (4)"

    def test_rename_mapping_preserves_first_occurrence(self):
        """Test that rename mapping always preserves the first occurrence."""
        validator = TabNameCaseCollisionsValidator()

        # Different orders should preserve the first in each group
        collisions1 = {"test": ["Test", "TEST", "test"]}
        mapping1 = validator._create_rename_mapping(collisions1)
        assert mapping1["Test"] == "Test"  # First preserved

        collisions2 = {"test": ["test", "Test", "TEST"]}
        mapping2 = validator._create_rename_mapping(collisions2)
        assert mapping2["test"] == "test"  # First preserved

    def test_edge_case_empty_tab_names(self):
        """Test handling of edge cases like empty tab names."""
        validator = TabNameCaseCollisionsValidator()

        # Include empty strings and whitespace
        tab_names = ["Sheet1", "", " ", "sheet1"]
        collisions = validator._detect_case_collisions(tab_names)

        # Should still detect the Sheet1/sheet1 collision
        assert len(collisions) == 1
        assert "sheet1" in collisions

    def test_performance_with_many_tabs(self):
        """Test performance with a larger number of tabs."""
        validator = TabNameCaseCollisionsValidator()

        # Create many tabs with some collisions
        tab_names = []
        for i in range(100):
            tab_names.append(f"Sheet{i}")
            if i % 10 == 0:  # Every 10th sheet has a case collision
                tab_names.append(f"SHEET{i}")

        collisions = validator._detect_case_collisions(tab_names)

        # Should find 10 collision groups (sheets 0, 10, 20, ..., 90)
        assert len(collisions) == 10

        # Create rename mapping
        mapping = validator._create_rename_mapping(collisions)

        # Should have mappings for all colliding tabs
        assert len(mapping) == 20  # 10 pairs of colliding tabs
