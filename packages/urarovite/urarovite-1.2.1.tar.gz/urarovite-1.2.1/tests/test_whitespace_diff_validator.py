"""Tests for the whitespace difference validator."""

from unittest.mock import patch, MagicMock

from urarovite.validators import get_validator
from urarovite.validators.whitespace_diff import WhitespaceDiffValidator, run
from urarovite.core.spreadsheet import SpreadsheetMetadata


def test_validator_registration():
    """Test that the validator is registered and has the correct name."""
    validator = get_validator("whitespace_diff")
    assert isinstance(validator, WhitespaceDiffValidator)
    assert validator.id == "whitespace_diff"
    assert "Whitespace Difference" in validator.name


def test_analyze_whitespace():
    """Test whitespace analysis functionality."""
    validator = WhitespaceDiffValidator()

    # Test with leading and trailing whitespace
    result = validator._analyze_whitespace("  hello world  ")
    assert result["has_leading"] is True
    assert result["has_trailing"] is True
    assert result["normalized"] == "hello world"
    assert result["leading_whitespace"] == "  "
    assert result["trailing_whitespace"] == "  "

    # Test with no whitespace
    result = validator._analyze_whitespace("hello world")
    assert result["has_leading"] is False
    assert result["has_trailing"] is False
    assert result["normalized"] == "hello world"

    # Test with only leading whitespace
    result = validator._analyze_whitespace("  hello")
    assert result["has_leading"] is True
    assert result["has_trailing"] is False
    assert result["normalized"] == "hello"

    # Test with only trailing whitespace
    result = validator._analyze_whitespace("hello  ")
    assert result["has_leading"] is False
    assert result["has_trailing"] is True
    assert result["normalized"] == "hello"


def test_identify_whitespace_chars():
    """Test whitespace character identification."""
    validator = WhitespaceDiffValidator()

    # Test with regular spaces
    result = validator._identify_whitespace_chars("   ")
    assert len(result) == 3
    assert all(char["code"] == "space" for char in result)

    # Test with mixed whitespace
    result = validator._identify_whitespace_chars("\t \n")
    assert len(result) == 3
    codes = [char["code"] for char in result]
    assert "tab" in codes
    assert "space" in codes
    assert "newline" in codes


def test_compare_values():
    """Test value comparison for whitespace differences."""
    validator = WhitespaceDiffValidator()

    # Test identical values
    result = validator._compare_values("hello", "hello")
    assert result["has_differences"] is False

    # Test whitespace-only differences
    result = validator._compare_values("hello", "  hello  ")
    assert result["has_differences"] is True
    assert len(result["differences"]) > 0

    # Test content differences
    result = validator._compare_values("hello", "world")
    assert result["has_differences"] is True
    assert any(diff["type"] == "content_difference" for diff in result["differences"])


def test_detect_whitespace_flags():
    """Test that the validator detects whitespace flags in cells."""
    validator = WhitespaceDiffValidator()
    data = [
        ["H1", "H2"],
        ["  A  ", "B"],
        ["C", "  D  "],
        ["E", "F"],
    ]
    sheet_url = "https://docs.google.com/spreadsheets/d/sheet123/edit"

    # Mock the spreadsheet interface
    mock_spreadsheet = MagicMock()
    mock_metadata = SpreadsheetMetadata(
        spreadsheet_id="test_id",
        title="Test Sheet",
        sheet_names=["Sheet1"],
        spreadsheet_type="google_sheets",
    )
    mock_spreadsheet.get_metadata.return_value = mock_metadata

    # Create a mock SheetData object with the values attribute
    mock_sheet_data = MagicMock()
    mock_sheet_data.values = data
    mock_spreadsheet.get_sheet_data.return_value = mock_sheet_data

    with patch.object(validator, "_get_spreadsheet", return_value=mock_spreadsheet):
        result = validator.validate(
            spreadsheet_source=sheet_url,
            mode="flag",
            auth_credentials={"encoded_credentials": "fake_creds"},
        )

        # Should find flags in cells with leading/trailing whitespace
        assert result["flags_found"] > 0


def test_fix_whitespace_flags():
    """Test that the validator can fix whitespace flags."""
    validator = WhitespaceDiffValidator()
    data = [
        ["H1", "H2"],
        ["  A  ", "B"],
        ["C", "  D  "],
    ]
    sheet_url = "https://docs.google.com/spreadsheets/d/sheet123/edit"

    # Mock the spreadsheet interface
    mock_spreadsheet = MagicMock()
    mock_metadata = SpreadsheetMetadata(
        spreadsheet_id="test_id",
        title="Test Sheet",
        sheet_names=["Sheet1"],
        spreadsheet_type="google_sheets",
    )
    mock_spreadsheet.get_metadata.return_value = mock_metadata

    # Create a mock SheetData object with the values attribute
    mock_sheet_data = MagicMock()
    mock_sheet_data.values = data
    mock_spreadsheet.get_sheet_data.return_value = mock_sheet_data

    with patch.object(validator, "_get_spreadsheet", return_value=mock_spreadsheet):
        result = validator.validate(
            spreadsheet_source=sheet_url,
            mode="fix",
            auth_credentials={"encoded_credentials": "fake_creds"},
        )

        # Should apply fixes
        assert result["fixes_applied"] > 0


def test_input_output_comparison():
    """Test comparison between input and output sheets."""
    validator = WhitespaceDiffValidator()

    # Mock spreadsheet with input/output sheets
    mock_spreadsheet = MagicMock()
    mock_metadata = SpreadsheetMetadata(
        spreadsheet_id="test_id",
        title="Test Sheet",
        sheet_names=["Input", "Output"],
        spreadsheet_type="google_sheets",
    )
    mock_spreadsheet.get_metadata.return_value = mock_metadata

    # Mock input sheet data
    mock_input_data = MagicMock()
    mock_input_data.values = [["A", "B"], ["  hello  ", "world"]]
    mock_spreadsheet.get_sheet_data.side_effect = lambda name: {
        "Input": mock_input_data,
        "Output": MagicMock(values=[["A", "B"], ["hello", "world"]]),
    }.get(name)

    with patch.object(validator, "_get_spreadsheet", return_value=mock_spreadsheet):
        result = validator.validate(
            spreadsheet_source="test_url",
            mode="flag",
            auth_credentials={"encoded_credentials": "fake_creds"},
        )

        # Should detect differences between input and output
        assert result["flags_found"] > 0


def test_run_function():
    """Test the backward compatibility run function."""
    sheet_url = "https://docs.google.com/spreadsheets/d/sheet123/edit"

    with patch(
        "urarovite.validators.whitespace_diff.WhitespaceDiffValidator"
    ) as mock_validator_class:
        mock_validator = MagicMock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate.return_value = {"flags_found": 1}

        result = run(sheet_url, "flag")

        mock_validator.validate.assert_called_once()
        assert result["flags_found"] == 1


def test_whitespace_character_detection():
    """Test detection of various whitespace characters."""
    validator = WhitespaceDiffValidator()

    # Test with non-breaking space
    result = validator._analyze_whitespace("\u00a0hello\u00a0")
    assert result["has_leading"] is True
    assert result["has_trailing"] is True

    # Test with tab character
    result = validator._analyze_whitespace("\thello\t")
    assert result["has_leading"] is True
    assert result["has_trailing"] is True

    # Test with newline
    result = validator._analyze_whitespace("\nhello\n")
    assert result["has_leading"] is True
    assert result["has_trailing"] is True


def test_empty_strings():
    """Test handling of empty strings and None values."""
    validator = WhitespaceDiffValidator()

    # Test empty string
    result = validator._analyze_whitespace("")
    assert result["has_leading"] is False
    assert result["has_trailing"] is False
    assert result["normalized"] == ""

    # Test None value
    result = validator._analyze_whitespace(None)
    assert result == {}


def test_mixed_whitespace_types():
    """Test detection of mixed whitespace character types."""
    validator = WhitespaceDiffValidator()

    # Test with mixed whitespace
    result = validator._analyze_whitespace("\t \u00a0hello\n \r")
    assert result["has_leading"] is True
    assert result["has_trailing"] is True

    # Check that different types are identified
    leading_chars = result["leading_chars"]
    trailing_chars = result["trailing_chars"]

    assert len(leading_chars) == 3  # tab, space, no-break space
    assert len(trailing_chars) == 3  # newline, space, carriage return
