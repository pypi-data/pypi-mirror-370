"""Tests for the DuplicateOverlappingRangesValidator."""

import pytest
from unittest.mock import Mock, patch

from urarovite.validators.duplicate_overlapping_ranges import (
    DuplicateOverlappingRangesValidator,
)
from urarovite.validators.base import ValidationResult
from urarovite.core.spreadsheet import SpreadsheetInterface, SheetData


class TestDuplicateOverlappingRangesValidator:
    """Test cases for DuplicateOverlappingRangesValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = DuplicateOverlappingRangesValidator()
        self.mock_spreadsheet = Mock(spec=SpreadsheetInterface)

    def test_validator_initialization(self):
        """Test validator is properly initialized."""
        assert self.validator.id == "duplicate_overlapping_ranges"
        assert "Duplicate and Overlapping Ranges" in self.validator.name
        assert "overlapping verification ranges" in self.validator.description

    def test_contains_a1_ranges(self):
        """Test A1 range detection in strings."""
        # Valid A1 ranges
        assert self.validator._contains_a1_ranges("A1:B10")
        assert self.validator._contains_a1_ranges("'Sheet1'!A1")
        assert self.validator._contains_a1_ranges("'My Sheet'!A1:B5")
        assert self.validator._contains_a1_ranges("B2")

        # Invalid or non-range strings
        assert not self.validator._contains_a1_ranges("")
        assert not self.validator._contains_a1_ranges("Hello World")
        assert not self.validator._contains_a1_ranges("123")
        assert not self.validator._contains_a1_ranges(None)

    def test_parse_cell_coordinates(self):
        """Test A1 cell coordinate parsing."""
        # Single cells
        assert self.validator._parse_cell_coordinates("A1") == (1, 1)
        assert self.validator._parse_cell_coordinates("B2") == (2, 2)
        assert self.validator._parse_cell_coordinates("Z26") == (26, 26)
        assert self.validator._parse_cell_coordinates("AA27") == (27, 27)
        assert self.validator._parse_cell_coordinates("AB28") == (28, 28)

        # Invalid cells
        assert self.validator._parse_cell_coordinates("") == (None, None)
        assert self.validator._parse_cell_coordinates("1A") == (None, None)
        assert self.validator._parse_cell_coordinates("A") == (None, None)
        assert self.validator._parse_cell_coordinates("1") == (None, None)

    def test_parse_single_range(self):
        """Test single A1 range parsing."""
        # Simple ranges
        result = self.validator._parse_single_range("A1:B10")
        assert result["sheet"] == ""
        assert result["start_cell"] == "A1"
        assert result["end_cell"] == "B10"
        assert result["start_row"] == 1
        assert result["start_col"] == 1
        assert result["end_row"] == 10
        assert result["end_col"] == 2

        # Sheet-qualified ranges
        result = self.validator._parse_single_range("'Sheet1'!A1:B5")
        assert result["sheet"] == "Sheet1"
        assert result["start_cell"] == "A1"
        assert result["end_cell"] == "B5"

        # Single cell ranges
        result = self.validator._parse_single_range("C3")
        assert result["sheet"] == ""
        assert result["start_cell"] == "C3"
        assert result["end_cell"] == "C3"
        assert result["start_row"] == 3
        assert result["start_col"] == 3

        # Invalid ranges
        assert self.validator._parse_single_range("") == {}
        assert self.validator._parse_single_range("invalid") == {}
        assert self.validator._parse_single_range("A1:B") == {}

    def test_parse_ranges_string(self):
        """Test parsing strings with multiple ranges separated by @@."""
        # Multiple ranges
        ranges = self.validator._parse_ranges_string("A1:B5@@C1:D10@@E1")
        assert len(ranges) == 3
        assert ranges[0]["start_cell"] == "A1"
        assert ranges[1]["start_cell"] == "C1"
        assert ranges[2]["start_cell"] == "E1"

        # Single range
        ranges = self.validator._parse_ranges_string("A1:B5")
        assert len(ranges) == 1
        assert ranges[0]["start_cell"] == "A1"

        # Empty or invalid strings
        assert self.validator._parse_ranges_string("") == []
        assert self.validator._parse_ranges_string("@@") == []

        # Test single cell with separators
        single_cell_ranges = self.validator._parse_ranges_string("@@A1@@")
        assert len(single_cell_ranges) == 1
        assert single_cell_ranges[0]["start_cell"] == "A1"
        assert single_cell_ranges[0]["end_cell"] == "A1"

    def test_ranges_overlap(self):
        """Test range overlap detection."""
        range1 = {
            "sheet": "Sheet1",
            "start_row": 1,
            "start_col": 1,
            "end_row": 5,
            "end_col": 5,
        }
        range2 = {
            "sheet": "Sheet1",
            "start_row": 3,
            "start_col": 3,
            "end_row": 7,
            "end_col": 7,
        }
        range3 = {
            "sheet": "Sheet1",
            "start_row": 6,
            "start_col": 6,
            "end_row": 10,
            "end_col": 10,
        }
        range4 = {
            "sheet": "Sheet2",
            "start_row": 1,
            "start_col": 1,
            "end_row": 5,
            "end_col": 5,
        }

        # Overlapping ranges
        assert self.validator._ranges_overlap(range1, range2) is True
        assert self.validator._ranges_overlap(range2, range1) is True

        # Non-overlapping ranges
        assert self.validator._ranges_overlap(range1, range3) is False
        assert self.validator._ranges_overlap(range3, range1) is False

        # Different sheets (no overlap possible)
        assert self.validator._ranges_overlap(range1, range4) is False

    def test_calculate_overlap_area(self):
        """Test overlap area calculation."""
        range1 = {
            "sheet": "Sheet1",
            "start_row": 1,
            "start_col": 1,
            "end_row": 5,
            "end_col": 5,
        }
        range2 = {
            "sheet": "Sheet1",
            "start_row": 3,
            "start_col": 3,
            "end_row": 7,
            "end_col": 7,
        }

        # Overlap area should be 3x3 = 9 cells
        overlap_area = self.validator._calculate_overlap_area(range1, range2)
        assert overlap_area == 9

        # No overlap
        range3 = {
            "sheet": "Sheet1",
            "start_row": 6,
            "start_col": 6,
            "end_row": 10,
            "end_col": 10,
        }
        overlap_area = self.validator._calculate_overlap_area(range1, range3)
        assert overlap_area == 0

    def test_find_duplicate_ranges(self):
        """Test duplicate range detection."""
        ranges = [
            {
                "sheet": "Sheet1",
                "start_row": 1,
                "start_col": 1,
                "end_row": 5,
                "end_col": 5,
                "range_string": "A1:E5",
                "source": {"cell": "A1"},
            },
            {
                "sheet": "Sheet1",
                "start_row": 1,
                "start_col": 1,
                "end_row": 5,
                "end_col": 5,
                "range_string": "A1:E5",
                "source": {"cell": "B1"},
            },
            {
                "sheet": "Sheet1",
                "start_row": 6,
                "start_col": 6,
                "end_row": 10,
                "end_col": 10,
                "range_string": "F6:J10",
                "source": {"cell": "C1"},
            },
        ]

        duplicates = self.validator._find_duplicate_ranges(ranges)
        assert len(duplicates) == 1
        assert duplicates[0]["issue"] == "Duplicate range definition"
        assert duplicates[0]["duplicate"]["source"]["cell"] == "B1"
        assert duplicates[0]["original"]["source"]["cell"] == "A1"

    def test_find_overlapping_ranges(self):
        """Test overlapping range detection."""
        ranges = [
            {
                "sheet": "Sheet1",
                "start_row": 1,
                "start_col": 1,
                "end_row": 5,
                "end_col": 5,
                "range_string": "A1:E5",
                "source": {"cell": "A1"},
            },
            {
                "sheet": "Sheet1",
                "start_row": 3,
                "start_col": 3,
                "end_row": 7,
                "end_col": 7,
                "range_string": "C3:G7",
                "source": {"cell": "B1"},
            },
            {
                "sheet": "Sheet1",
                "start_row": 8,
                "start_col": 8,
                "end_row": 12,
                "end_col": 12,
                "range_string": "H8:L12",
                "source": {"cell": "C1"},
            },
        ]

        overlaps = self.validator._find_overlapping_ranges(ranges)
        assert len(overlaps) == 1
        assert overlaps[0]["issue"] == "Overlapping ranges"
        assert overlaps[0]["overlap_area"] == 9

    def test_find_conflicting_ranges(self):
        """Test conflicting range detection."""
        ranges = [
            {
                "sheet": "Sheet1",
                "start_row": 1,
                "start_col": 1,
                "end_row": 5,
                "end_col": 5,
                "range_string": "A1:E5",
                "source": {"cell": "A1"},
            },
            {
                "sheet": "Sheet1",
                "start_row": 1,
                "start_col": 1,
                "end_row": 5,
                "end_col": 5,
                "range_string": "'Sheet1'!A1:E5",  # Different notation
                "source": {"cell": "B1"},
            },
        ]

        conflicts = self.validator._find_conflicting_ranges(ranges)
        assert len(conflicts) == 1
        assert "Same area with different notation" in conflicts[0]["conflict_type"]

    def test_generate_optimization_suggestions(self):
        """Test optimization suggestion generation."""
        ranges = [
            {
                "sheet": "Sheet1",
                "start_row": 1,
                "start_col": 1,
                "end_row": 5,
                "end_col": 5,
                "range_string": "A1:E5",
                "source": {"cell": "A1"},
            },
            {
                "sheet": "Sheet1",
                "start_row": 1,
                "start_col": 6,
                "end_row": 5,
                "end_col": 10,
                "range_string": "F1:J5",
                "source": {"cell": "B1"},
            },
            {
                "sheet": "Sheet1",
                "start_row": 6,
                "start_col": 1,
                "end_row": 6,
                "end_col": 1,
                "range_string": "A6:A6",
                "source": {"cell": "C1"},
            },
        ]

        suggestions = self.validator._generate_optimization_suggestions(ranges)
        assert len(suggestions) >= 2

        # Should suggest merging adjacent horizontal ranges
        horizontal_merge = next(
            s for s in suggestions if s["type"] == "merge_horizontal"
        )
        assert horizontal_merge is not None

        # Should suggest simplifying single cell range
        single_cell = next(
            s for s in suggestions if s["type"] == "simplify_single_cell"
        )
        assert single_cell is not None

    def test_detect_range_columns(self):
        """Test automatic detection of range columns."""
        data = [
            ["Task", "Verification Ranges", "Status"],
            ["Task1", "A1:B5@@C1:D10", "Done"],
            ["Task2", "E1:F5", "Pending"],
            ["Task3", "G1:H10@@I1:J5", "Done"],
        ]

        range_columns = self.validator._detect_range_columns(data)
        assert 2 in range_columns  # "Verification Ranges" column

    def test_get_cell_ref(self):
        """Test conversion of coordinates to A1 notation."""
        assert self.validator._get_cell_ref(1, 1) == "A1"
        assert self.validator._get_cell_ref(2, 2) == "B2"
        assert self.validator._get_cell_ref(26, 26) == "Z26"
        assert self.validator._get_cell_ref(27, 27) == "AA27"
        assert self.validator._get_cell_ref(28, 28) == "AB28"

    @patch("urarovite.validators.base.SpreadsheetFactory")
    def test_validate_empty_sheet(self, mock_factory):
        """Test validation with empty sheet."""
        # Mock empty sheet data
        mock_sheet_data = SheetData(values=[], sheet_name="Test", rows=0, cols=0)
        self.mock_spreadsheet.get_sheet_data.return_value = mock_sheet_data
        self.mock_spreadsheet.get_metadata.return_value = Mock(sheet_names=["Test"])

        mock_factory.create_spreadsheet.return_value = self.mock_spreadsheet

        result = self.validator.validate("test_url", "flag")

        assert result["flags_found"] == 0
        assert result["details"]["valid_ranges"] == 0
        assert "Sheet is empty" in result["automated_log"]

    @patch("urarovite.validators.base.SpreadsheetFactory")
    def test_validate_no_range_columns(self, mock_factory):
        """Test validation when no range columns are found."""
        # Mock sheet data without range columns
        mock_sheet_data = SheetData(
            values=[
                ["Task", "Description", "Status"],
                ["Task1", "Some description", "Done"],
                ["Task2", "Another description", "Pending"],
            ],
            sheet_name="Test",
            rows=3,
            cols=3,
        )
        self.mock_spreadsheet.get_sheet_data.return_value = mock_sheet_data
        self.mock_spreadsheet.get_metadata.return_value = Mock(sheet_names=["Test"])

        mock_factory.create_spreadsheet.return_value = self.mock_spreadsheet

        result = self.validator.validate("test_url", "flag")

        assert result["flags_found"] == 0
        assert result["details"]["valid_ranges"] == 0
        assert "No range columns detected" in result["automated_log"]

    @patch("urarovite.validators.base.SpreadsheetFactory")
    def test_validate_with_ranges(self, mock_factory):
        """Test validation with actual ranges."""
        # Mock sheet data with ranges
        mock_sheet_data = SheetData(
            values=[
                ["Task", "Verification Ranges", "Status"],
                ["Task1", "A1:B5@@C1:D10", "Done"],
                ["Task2", "A1:B5", "Pending"],  # Duplicate of Task1's first range
                ["Task3", "E1:F5@@F1:G5", "Done"],  # Overlapping ranges
            ],
            sheet_name="Test",
            rows=4,
            cols=3,
        )
        self.mock_spreadsheet.get_sheet_data.return_value = mock_sheet_data
        self.mock_spreadsheet.get_metadata.return_value = Mock(sheet_names=["Test"])

        mock_factory.create_spreadsheet.return_value = self.mock_spreadsheet

        result = self.validator.validate("test_url", "flag")

        assert result["flags_found"] > 0
        assert result["details"]["valid_ranges"] > 0
        assert len(result["details"]["duplicate_ranges"]) > 0
        assert len(result["details"]["overlapping_ranges"]) > 0
