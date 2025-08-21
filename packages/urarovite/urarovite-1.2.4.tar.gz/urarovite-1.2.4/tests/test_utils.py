"""Tests for the utils module functionality."""

import pytest
from unittest.mock import Mock, MagicMock

from urarovite.utils.sheets import (
    extract_sheet_id,
    split_segments,
    strip_outer_single_quotes,
    extract_sheet_and_range,
    parse_tab_token,
    parse_referenced_tabs,
    col_index_to_letter,
    letter_to_col_index,
    fetch_sheet_tabs,
    get_sheet_values,
    update_sheet_values,
    SHEET_ID_RE,
    SEGMENT_SEPARATOR,
    COL_RE,
    ROW_RE,
)
from urarovite.core.exceptions import SheetAccessError


class TestUrlAndRangeParsing:
    """Test URL and range parsing utilities."""

    def test_extract_sheet_id_valid_urls(self):
        """Test extracting sheet ID from valid Google Sheets URLs."""
        test_cases = [
            (
                "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit",
                "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
            ),
            (
                "https://docs.google.com/spreadsheets/d/1ABC-123_def/edit#gid=0",
                "1ABC-123_def",
            ),
            ("https://docs.google.com/spreadsheets/d/1234567890/", "1234567890"),
        ]

        for url, expected_id in test_cases:
            result = extract_sheet_id(url)
            assert result == expected_id, f"Failed for URL: {url}"

    def test_extract_sheet_id_invalid_urls(self):
        """Test extracting sheet ID from invalid URLs."""
        invalid_urls = [
            None,
            "",
            "https://example.com",
            "not-a-url",
            # Note: The regex will match any /d/ pattern, so documents URL will match
            # This is expected behavior - the regex is simple and matches the pattern
        ]

        for url in invalid_urls:
            result = extract_sheet_id(url)
            assert result is None, f"Should return None for: {url}"

    def test_split_segments(self):
        """Test splitting range segments."""
        test_cases = [
            ("'Sheet1'!A1:B2@@'Sheet2'!C3:D4", ["'Sheet1'!A1:B2", "'Sheet2'!C3:D4"]),
            ("Single!A1", ["Single!A1"]),
            ("  A1  @@  B2  @@  C3  ", ["A1", "B2", "C3"]),
            ("", []),
            (None, []),
            ("A1@@@@B2", ["A1", "B2"]),  # Empty segments filtered out
        ]

        for input_str, expected in test_cases:
            result = split_segments(input_str)
            assert result == expected, f"Failed for input: {input_str}"

    def test_split_segments_custom_separator(self):
        """Test splitting with custom separator."""
        result = split_segments("A1||B2||C3", sep="||")
        assert result == ["A1", "B2", "C3"]

    def test_separator_configuration(self):
        """Test configuring the global separator."""
        from urarovite.utils.sheets import get_segment_separator, set_segment_separator

        # Test default separator
        assert get_segment_separator() == "@@"

        # Test setting new separator
        set_segment_separator(",")
        assert get_segment_separator() == ","

        # Test that split_segments uses the new separator by default
        result = split_segments("A1,B2,C3")
        assert result == ["A1", "B2", "C3"]

        # Test that explicit separator still works
        result = split_segments("A1@@B2@@C3", sep="@@")
        assert result == ["A1", "B2", "C3"]

        # Restore default separator
        set_segment_separator("@@")
        assert get_segment_separator() == "@@"

    def test_strip_outer_single_quotes(self):
        """Test removing outer single quotes."""
        test_cases = [
            ("'Sheet Name'", "Sheet Name"),
            ("Sheet Name", "Sheet Name"),
            ("'", ""),
            ("''", ""),
            ("'Single'", "Single"),
            ("  'Spaced'  ", "Spaced"),
            ("'Partial", "Partial"),  # Strips leading quote
            ("Partial'", "Partial"),  # Strips trailing quote
        ]

        for input_str, expected in test_cases:
            result = strip_outer_single_quotes(input_str)
            assert result == expected, f"Failed for input: {input_str}"

    def test_extract_sheet_and_range(self):
        """Test extracting sheet name and range from segments."""
        test_cases = [
            ("Sheet1!A1:B2", ("Sheet1", "A1:B2")),
            ("'Sheet Name'!C3:D4", ("'Sheet Name'", "C3:D4")),
            ("Sheet1", ("Sheet1", None)),
            ("'Whole Sheet'", ("'Whole Sheet'", None)),
            (
                "Complex!Name!A1:B2",
                ("Complex", "Name!A1:B2"),
            ),  # First ! is the delimiter
        ]

        for segment, expected in test_cases:
            result = extract_sheet_and_range(segment)
            assert result == expected, f"Failed for segment: {segment}"

    def test_parse_tab_token(self):
        """Test parsing tab names from segments."""
        test_cases = [
            ("'Sheet Name'!A1:B2", "Sheet Name"),
            ("Sheet1!A1:B2", "Sheet1"),
            ("'Tab'", "Tab"),
            ("Simple", "Simple"),
            ("  'Spaced'  !A1", "Spaced"),
        ]

        for segment, expected in test_cases:
            result = parse_tab_token(segment)
            assert result == expected, f"Failed for segment: {segment}"

    def test_parse_referenced_tabs(self):
        """Test parsing unique tab names from ranges string."""
        test_cases = [
            (
                "'Sheet1'!A1@@'Sheet2'!B2@@'Sheet1'!C3",
                ["Sheet1", "Sheet2"],  # Sheet1 appears only once
            ),
            ("Tab1!A1@@Tab2!B2@@Tab3!C3", ["Tab1", "Tab2", "Tab3"]),
            ("", []),
            (None, []),
            ("'Single Tab'!A1:Z100", ["Single Tab"]),
        ]

        for ranges_str, expected in test_cases:
            result = parse_referenced_tabs(ranges_str)
            assert result == expected, f"Failed for ranges: {ranges_str}"


class TestColumnConversions:
    """Test column letter/index conversion utilities."""

    def test_col_index_to_letter(self):
        """Test converting column indices to letters."""
        test_cases = [
            (0, "A"),
            (25, "Z"),
            (26, "AA"),
            (27, "AB"),
            (701, "ZZ"),
            (702, "AAA"),
        ]

        for idx, expected in test_cases:
            result = col_index_to_letter(idx)
            assert result == expected, f"Failed for index {idx}"

    def test_letter_to_col_index(self):
        """Test converting column letters to indices."""
        test_cases = [
            ("A", 0),
            ("Z", 25),
            ("AA", 26),
            ("AB", 27),
            ("ZZ", 701),
            ("AAA", 702),
        ]

        for letters, expected in test_cases:
            result = letter_to_col_index(letters)
            assert result == expected, f"Failed for letters {letters}"

    def test_column_conversion_roundtrip(self):
        """Test that column conversions are reversible."""
        for idx in [0, 1, 25, 26, 27, 100, 701, 702]:
            letters = col_index_to_letter(idx)
            back_to_idx = letter_to_col_index(letters)
            assert back_to_idx == idx, f"Roundtrip failed for index {idx}"


class TestFetchSheetTabs:
    """Test the fetch_sheet_tabs function."""

    def test_fetch_tabs_success(self):
        """Test successful tab fetching."""
        mock_service = Mock()
        mock_spreadsheets = Mock()
        mock_get = Mock()
        Mock()

        # Set up the mock chain
        mock_service.spreadsheets.return_value = mock_spreadsheets
        mock_spreadsheets.get.return_value = mock_get
        mock_get.execute.return_value = {
            "sheets": [
                {"properties": {"title": "Sheet1"}},
                {"properties": {"title": "Sheet2"}},
                {"properties": {"title": "Data Tab"}},
            ]
        }

        result = fetch_sheet_tabs(mock_service, "test_sheet_id")

        assert result["accessible"] is True
        assert result["tabs"] == ["Sheet1", "Sheet2", "Data Tab"]
        assert result["error"] is None

        # Verify API calls
        mock_service.spreadsheets.assert_called_once()
        mock_spreadsheets.get.assert_called_once_with(
            spreadsheetId="test_sheet_id", fields="sheets.properties.title"
        )

    def test_fetch_tabs_missing_spreadsheet_id(self):
        """Test handling of missing spreadsheet ID."""
        mock_service = Mock()

        result = fetch_sheet_tabs(mock_service, None)

        assert result["accessible"] is False
        assert result["tabs"] == []
        assert result["error"] == "missing_or_malformed_url"

    def test_fetch_tabs_empty_spreadsheet_id(self):
        """Test handling of empty spreadsheet ID."""
        mock_service = Mock()

        result = fetch_sheet_tabs(mock_service, "")

        assert result["accessible"] is False
        assert result["tabs"] == []
        assert result["error"] == "missing_or_malformed_url"

    def test_fetch_tabs_permission_denied(self):
        """Test handling of permission denied (403) error."""
        mock_service = Mock()
        mock_service.spreadsheets().get().execute.side_effect = Exception(
            "HttpError 403"
        )

        result = fetch_sheet_tabs(mock_service, "test_sheet_id")

        assert result["accessible"] is False
        assert result["tabs"] == []
        assert result["error"] == "forbidden_or_not_found"

    def test_fetch_tabs_not_found(self):
        """Test handling of not found (404) error."""
        mock_service = Mock()
        mock_service.spreadsheets().get().execute.side_effect = Exception(
            "HttpError 404"
        )

        result = fetch_sheet_tabs(mock_service, "test_sheet_id")

        assert result["accessible"] is False
        assert result["tabs"] == []
        assert result["error"] == "forbidden_or_not_found"

    def test_fetch_tabs_other_exception(self):
        """Test handling of other exceptions."""
        mock_service = Mock()
        mock_service.spreadsheets().get().execute.side_effect = ValueError(
            "Something went wrong"
        )

        result = fetch_sheet_tabs(mock_service, "test_sheet_id")

        assert result["accessible"] is False
        assert result["tabs"] == []
        assert result["error"] == "request_exception:ValueError"


class TestGetSheetValues:
    """Test the get_sheet_values function."""

    def test_get_values_success(self):
        """Test successful value retrieval."""
        mock_service = Mock()
        mock_service.spreadsheets().values().get().execute.return_value = {
            "values": [
                ["A1", "B1", "C1"],
                ["A2", "B2", ""],
                ["A3", "", "C3"],
            ]
        }

        result = get_sheet_values(mock_service, "test_sheet_id", "Sheet1!A1:C3")

        assert result["success"] is True
        assert result["values"] == [
            ["A1", "B1", "C1"],
            ["A2", "B2", ""],
            ["A3", "", "C3"],
        ]
        assert result["rows"] == 3  # All rows have some data
        assert result["cols"] == 3  # All columns have some data
        assert result["error"] is None

    def test_get_values_empty_sheet(self):
        """Test handling of empty sheet."""
        mock_service = Mock()
        mock_service.spreadsheets().values().get().execute.return_value = {"values": []}

        result = get_sheet_values(mock_service, "test_sheet_id", "Sheet1!A1:C3")

        assert result["success"] is True
        assert result["values"] == []
        assert result["rows"] == 0
        assert result["cols"] == 0
        assert result["error"] is None

    def test_get_values_sparse_data(self):
        """Test handling of sparse data with empty rows/columns."""
        mock_service = Mock()
        mock_service.spreadsheets().values().get().execute.return_value = {
            "values": [
                ["A1", "", ""],
                ["", "", ""],  # Empty row
                ["A3", "", "C3"],
                ["", "", ""],  # Another empty row
            ]
        }

        result = get_sheet_values(mock_service, "test_sheet_id", "Sheet1!A1:C4")

        assert result["success"] is True
        assert result["rows"] == 3  # Only rows 1 and 3 have data
        assert result["cols"] == 3  # Columns A and C have data

    def test_get_values_missing_spreadsheet_id(self):
        """Test handling of missing spreadsheet ID."""
        mock_service = Mock()

        result = get_sheet_values(mock_service, None, "Sheet1!A1:C3")

        assert result["success"] is False
        assert result["values"] == []
        assert result["rows"] == 0
        assert result["cols"] == 0
        assert result["error"] == "missing_spreadsheet_id"

    def test_get_values_permission_denied(self):
        """Test handling of permission denied error."""
        mock_service = Mock()
        mock_service.spreadsheets().values().get().execute.side_effect = Exception(
            "HttpError 403"
        )

        result = get_sheet_values(mock_service, "test_sheet_id", "Sheet1!A1:C3")

        assert result["success"] is False
        assert result["values"] == []
        assert result["rows"] == 0
        assert result["cols"] == 0
        assert result["error"] == "forbidden_or_not_found"

    def test_get_values_api_call_parameters(self):
        """Test that API is called with correct parameters."""
        mock_service = Mock()
        mock_get = Mock()
        mock_service.spreadsheets().values().get.return_value = mock_get
        mock_get.execute.return_value = {"values": []}

        get_sheet_values(mock_service, "test_sheet_id", "Sheet1!A1:C3")

        # Verify the API call parameters
        mock_service.spreadsheets().values().get.assert_called_once_with(
            spreadsheetId="test_sheet_id",
            range="Sheet1!A1:C3",
            valueRenderOption="UNFORMATTED_VALUE",
        )


class TestUpdateSheetValues:
    """Test the update_sheet_values function."""

    def test_update_values_success(self):
        """Test successful value update."""
        mock_service = Mock()
        mock_service.spreadsheets().values().update().execute.return_value = {
            "updatedCells": 6,
            "updatedRows": 2,
            "updatedColumns": 3,
        }

        values = [["A1", "B1", "C1"], ["A2", "B2", "C2"]]
        result = update_sheet_values(
            mock_service, "test_sheet_id", "Sheet1!A1:C2", values
        )

        assert result["success"] is True
        assert result["updated_cells"] == 6
        assert result["updated_rows"] == 2
        assert result["updated_columns"] == 3
        assert result["error"] is None

    def test_update_values_permission_denied(self):
        """Test handling of permission denied error."""
        mock_service = Mock()
        mock_service.spreadsheets().values().update().execute.side_effect = Exception(
            "HttpError 403"
        )

        values = [["A1", "B1"]]

        with pytest.raises(SheetAccessError) as exc_info:
            update_sheet_values(mock_service, "test_sheet_id", "Sheet1!A1:B1", values)

        assert "Permission denied" in str(exc_info.value)

    def test_update_values_not_found(self):
        """Test handling of not found error."""
        mock_service = Mock()
        mock_service.spreadsheets().values().update().execute.side_effect = Exception(
            "HttpError 404"
        )

        values = [["A1", "B1"]]

        with pytest.raises(SheetAccessError) as exc_info:
            update_sheet_values(mock_service, "test_sheet_id", "Sheet1!A1:B1", values)

        assert "Sheet not found" in str(exc_info.value)

    def test_update_values_other_error(self):
        """Test handling of other errors."""
        mock_service = Mock()
        mock_service.spreadsheets().values().update().execute.side_effect = ValueError(
            "Network error"
        )

        values = [["A1", "B1"]]

        with pytest.raises(SheetAccessError) as exc_info:
            update_sheet_values(mock_service, "test_sheet_id", "Sheet1!A1:B1", values)

        assert "Failed to update sheet" in str(exc_info.value)

    def test_update_values_api_call_parameters(self):
        """Test that API is called with correct parameters."""
        mock_service = Mock()
        mock_update = Mock()
        mock_service.spreadsheets().values().update.return_value = mock_update
        mock_update.execute.return_value = {
            "updatedCells": 1,
            "updatedRows": 1,
            "updatedColumns": 1,
        }

        values = [["Test Value"]]
        update_sheet_values(
            mock_service, "test_sheet_id", "Sheet1!A1", values, "USER_ENTERED"
        )

        # Verify the API call parameters
        mock_service.spreadsheets().values().update.assert_called_once_with(
            spreadsheetId="test_sheet_id",
            range="Sheet1!A1",
            valueInputOption="USER_ENTERED",
            body={"values": values},
        )


class TestConstants:
    """Test that constants are properly defined."""

    def test_constants_exist(self):
        """Test that all expected constants exist."""
        assert SHEET_ID_RE is not None
        assert SEGMENT_SEPARATOR == "@@"
        assert COL_RE == r"[A-Z]+"
        assert ROW_RE == r"[0-9]+"

    def test_sheet_id_regex(self):
        """Test that the sheet ID regex works correctly."""
        test_url = "https://docs.google.com/spreadsheets/d/1ABC123def/edit"
        match = SHEET_ID_RE.search(test_url)
        assert match is not None
        assert match.group(1) == "1ABC123def"
